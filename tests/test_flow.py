"""End-to-end flow check for AdaptiveLearn.

Walks the exact path from the project description:
  signup -> education details -> subject -> learning path -> AI tutor content
  -> assessment -> performance analysis -> Q-learning -> recommendation
  -> adaptive teacher -> next lesson -> continuous adaptation

Usage:  .venv/bin/python tests/test_flow.py [BASE_URL]
"""

import json
import sqlite3
import uuid
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000").rstrip("/")
DB = "database/adaptivelearn.db"

_failures: list[str] = []


def check(label: str, condition: bool, detail: str = "", soft: bool = False) -> None:
    mark = "PASS" if condition else ("SOFT" if soft else "FAIL")
    print(f"  [{mark}] {label}{(' -> ' + detail) if detail else ''}")
    if not condition and not soft:
        _failures.append(label)


def req(method: str, path: str, body=None, token: str | None = None):
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, method=method)
    r.add_header("Content-Type", "application/json")
    if token:
        r.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(r) as resp:
            return resp.status, json.loads(resp.read().decode() or "null")
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, {"raw": raw[:300]}


def correct_answers(topic_id: int) -> dict[str, str]:
    """Read the answer key straight from the DB so we can submit real answers."""
    con = sqlite3.connect(DB)
    rows = con.execute(
        "select id, correct_answer from questions where topic_id=?", (topic_id,)
    ).fetchall()
    con.close()
    return {str(qid): ans for qid, ans in rows}


def submit_quiz(token, topic_id, target_correct, seconds):
    """Submit a quiz getting exactly `target_correct` questions right."""
    st, qs = req("GET", f"/api/quiz/questions/{topic_id}", token=token)
    assert st == 200, f"questions fetch failed: {st} {qs}"
    key = correct_answers(topic_id)
    answers = {}
    for i, q in enumerate(qs["questions"]):
        right = key[str(q["id"])]
        if i < target_correct:
            answers[str(q["id"])] = right
        else:
            answers[str(q["id"])] = next(
                c for c in "ABCD" if c != right
            )
    st, res = req(
        "POST",
        "/api/quiz/submit",
        {"topic_id": topic_id, "answers": answers, "time_taken_seconds": seconds},
        token=token,
    )
    return st, res


def main() -> int:
    print(f"\nAdaptiveLearn end-to-end flow check against {BASE}\n")

    # ── 0. Health ──────────────────────────────────────────────────
    print("0. Backend health")
    st, d = req("GET", "/api/health")
    check("GET /api/health returns ok", st == 200 and d.get("status") == "ok", str(d))

    # ── 1. Login / sign up ─────────────────────────────────────────
    print("\n1. Login / sign up")
    run_id = uuid.uuid4().hex[:10]
    email = f"flow.{run_id}@test.com"
    st, d = req(
        "POST",
        "/api/auth/signup",
        {"name": "Flow Tester", "email": email, "password": "secret123"},
    )
    check("signup returns 200 + token", st == 200 and "access_token" in d, f"status={st} {json.dumps(d)[:120]}")
    token = d.get("access_token", "")

    st, d = req("POST", "/api/auth/login", {"email": email, "password": "secret123"})
    check("login works for the new account", st == 200 and "access_token" in d, f"status={st}")

    st, d = req("POST", "/api/auth/login", {"email": email, "password": "wrong"})
    check("wrong password is rejected with 401", st == 401, f"status={st}")

    st, d = req("GET", "/api/dashboard/")
    check("no token -> 401", st == 401, f"status={st}")

    st, d = req("GET", "/api/dashboard/", token="not-a-real-token")
    check("bad token -> 401", st == 401, f"status={st}")

    st, d = req("GET", "/api/profile/me", token=token)
    check(
        "GET /api/profile/me returns 200 with a valid token",
        st == 200 and d.get("profile") is None,
        f"status={st} body={json.dumps(d)[:120]}",
    )

    # ── 2. Education details ───────────────────────────────────────
    print("\n2. Education details selection")
    st, d = req(
        "GET", "/api/subjects/options"
    )
    check("GET /api/subjects/options lists educations", st == 200 and "B.Tech" in d.get("educations", []), str(d)[:120])

    st, d = req(
        "POST",
        "/api/profile/save",
        {"education": "B.Tech", "year": "2nd Year", "department": "Information Technology"},
        token=token,
    )
    check("POST /api/profile/save -> 200", st == 200, f"status={st} body={json.dumps(d)[:120]}")

    st, d = req("GET", "/api/profile/me", token=token)
    p = d.get("profile") or {}
    check(
        "profile persisted education/year/department",
        p.get("education") == "B.Tech"
        and p.get("year") == "2nd Year"
        and p.get("department") == "Information Technology",
        json.dumps(p)[:140],
    )

    # ── 3. Subject selection ───────────────────────────────────────
    print("\n3. Subject selection (by department)")
    q = urllib.parse.urlencode(
        {"education": "B.Tech", "year": "2nd Year", "department": "Information Technology"}
    )
    st, subjects = req("GET", f"/api/subjects/?{q}", token=token)
    check("GET /api/subjects/ returns 200", st == 200, f"status={st}")
    check(
        "subjects are filtered and all have topics",
        isinstance(subjects, list)
        and len(subjects) > 0
        and all(s["topic_count"] > 0 for s in subjects),
        json.dumps([(s["id"], s["name"], s["topic_count"]) for s in subjects])[:200],
    )
    subject_id = subjects[0]["id"]

    st, d = req(
        "POST", f"/api/profile/select-subject?subject_id={subject_id}", token=token
    )
    check(f"POST /api/profile/select-subject?subject_id={subject_id} -> 200", st == 200, f"status={st} {json.dumps(d)[:120]}")

    # ── 4. Personalized learning path ──────────────────────────────
    print("\n4. Personalized learning path")
    st, path = req("GET", f"/api/topics/learning-path/{subject_id}", token=token)
    check("GET /api/topics/learning-path/{id} -> 200 (not a 422)", st == 200, f"status={st} {json.dumps(d)[:120]}")
    check(
        "path has topics with completed/current/locked statuses",
        st == 200
        and path.get("total_topics", 0) > 0
        and {t["status"] for t in path["topics"]} <= {"completed", "current", "locked"}
        and sum(1 for t in path["topics"] if t["status"] == "current") == 1,
        f"total={path.get('total_topics')} progress={path.get('progress_percent')}%",
    )
    topic_id = path["current_topic"]["id"]

    # ── 5. AI teacher / tutor ──────────────────────────────────────
    print("\n5. AI teacher / tutor content")
    st, topic = req("GET", f"/api/topics/{topic_id}", token=token)
    check("GET /api/topics/{id} returns lesson content", st == 200 and topic.get("introduction"), f"status={st}")
    check(
        "all five tutor sections are populated",
        all(
            topic.get(k)
            for k in (
                "introduction",
                "explanation",
                "basic_example",
                "advanced_example",
                "resources",
            )
        ),
        "introduction/explanation/basic/advanced/resources",
    )

    st, d = req(
        "POST",
        "/api/tutor/ask",
        {"topic_id": topic_id, "question": "Explain this topic simply."},
        token=token,
    )
    check("POST /api/tutor/ask -> 200 with an answer", st == 200 and bool(d.get("answer")), f"status={st} style={d.get('teaching_style')}")

    # ── 6. Assessment ──────────────────────────────────────────────
    print("\n6. Assessment (10-15 topic questions)")
    st, qs = req("GET", f"/api/quiz/questions/{topic_id}", token=token)
    check("GET /api/quiz/questions/{id} -> 200", st == 200, f"status={st}")
    n = qs.get("total_questions", 0)
    check("question count is within 10-15", 10 <= n <= 15, f"got {n} questions")
    check(
        "correct answers are NOT leaked to the client",
        all("correct_answer" not in q for q in qs["questions"]),
    )

    # ── 7. Performance analysis + Q-learning: WEAK ─────────────────
    print("\n7. Weak performance -> performance analysis + Q-learning")
    st, res = submit_quiz(token, topic_id, target_correct=2, seconds=900)
    check("POST /api/quiz/submit -> 200 (was NameError before)", st == 200, f"status={st} {json.dumps(res)[:200]}")
    if st == 200:
        check("score graded correctly (2 right)", res["score"] == 2, f"score={res['score']}/{res['total_questions']}")
        check("accuracy computed", res["accuracy"] == 20.0, f"accuracy={res['accuracy']}")
        check("time taken recorded", res["time_taken_seconds"] == 900, f"{res['time_taken_seconds']}s")
        check(
            "performance classified as Weak",
            res["performance_level"] == "Weak",
            res["performance_level"],
        )
        check(
            "learning speed classified as Slow (900s/10q = 90s vs 60s budget)",
            res["learning_speed"] == "Slow",
            res["learning_speed"],
        )
        ql = res["q_learning_viz"]
        check("Q-learning state = Weak_Slow", ql["current_state"] == "Weak_Slow", ql["current_state"])
        check("Q-learning reward is negative for Weak_Slow", ql["reward"] == -10, f"reward={ql['reward']}")
        check(
            "weak student's action is masked to REVISION/PRACTICE only",
            res["rl_action"] in ("REVISION", "PRACTICE"),
            f"{res['rl_action']} (allowed={ql.get('allowed_actions')})",
        )
        check(
            "greedy policy for Weak_Slow is REVISION",
            max(ql["q_values_before"], key=lambda a: ql["q_values_before"][a]
                if a in ql["allowed_actions"] else -1e9) == "REVISION",
            json.dumps(ql["q_values_before"]),
        )
        if res["rl_action"] == "REVISION":
            check("REVISION maps to the slow/supportive teaching style",
                  res["recommendation"]["teaching_style"] == "slow",
                  res["recommendation"]["teaching_style"])
        else:
            check("PRACTICE maps to the normal teaching style",
                  res["recommendation"]["teaching_style"] == "normal",
                  res["recommendation"]["teaching_style"])
        check("review list returned for each question", len(res["review"]) == n, f"{len(res['review'])} items")
        check("weak student does NOT advance (action masking)", res["moved_to_next"] is False,
              f"moved={res['moved_to_next']}")

    # ── 8. STRONG performance ──────────────────────────────────────
    print("\n8. Strong performance -> advanced recommendation")
    st, res = submit_quiz(token, topic_id, target_correct=n, seconds=300)
    check("perfect quiz submits 200", st == 200, f"status={st}")
    if st == 200:
        check("score = all correct", res["score"] == n, f"{res['score']}/{n}")
        check("accuracy 100%", res["accuracy"] == 100.0, f"{res['accuracy']}")
        check(
            "performance classified as Excellent",
            res["performance_level"] == "Excellent",
            res["performance_level"],
        )
        check(
            "learning speed Fast (300s/10q = 30s vs 60s budget)",
            res["learning_speed"] == "Fast",
            res["learning_speed"],
        )
        ql = res["q_learning_viz"]
        check("Q-learning state = Excellent_Fast", ql["current_state"] == "Excellent_Fast", ql["current_state"])
        check("reward +10 for Excellent_Fast", ql["reward"] == 10, f"reward={ql['reward']}")
        check(
            "excellent student's action is masked to PRACTICE/CONTINUE/ADVANCED",
            res["rl_action"] in ("PRACTICE", "CONTINUE", "ADVANCED"),
            f"{res['rl_action']} (allowed={ql.get('allowed_actions')})",
        )
        expected_style = {"ADVANCED": "fast", "CONTINUE": "normal", "PRACTICE": "normal"}[res["rl_action"]]
        check(
            "recommendation teaching style matches the chosen action",
            res["recommendation"]["teaching_style"] == expected_style,
            f"{res['rl_action']} -> {res['recommendation']['teaching_style']}",
        )
        check("strong student advances to the next lesson", res["moved_to_next"] is True)
        check("next topic is returned", res["next_topic"] is not None, json.dumps(res.get("next_topic"))[:100])

        # The greedy (non-exploring) policy is the one the product relies on.
        greedy = max(ql["q_values_before"], key=ql["q_values_before"].get)
        check("greedy policy for Excellent_Fast is ADVANCED", greedy == "ADVANCED", f"greedy={greedy} q_before={ql['q_values_before']}")

        # Q-update actually happened
        act = res["rl_action"]
        before = ql["q_values_before"][act]
        after = ql["q_values"][act]
        expected = round(
            before + 0.1 * (ql["reward"] + 0.9 * ql["max_next_q"] - before), 6
        )
        check(
            "Q(s,a) updated with the Bellman rule Q+alpha[r+gamma*maxQ'-Q]",
            abs(after - expected) < 1e-6,
            f"Q({ql['current_state']},{act}): {before} -> {after} "
            f"(expected {expected}; r={ql['reward']}, maxQ'={ql['max_next_q']}, next={ql['next_state']})",
        )

    # ── 9. Learning path advanced ──────────────────────────────────
    print("\n9. Learning path advanced after a good result")
    st, path2 = req("GET", f"/api/topics/learning-path/{subject_id}", token=token)
    check(
        "current topic moved forward by one",
        path2["current_index"] == 1,
        f"current_index={path2.get('current_index')}",
    )
    check(
        "progress percentage increased",
        path2["progress_percent"] > 0,
        f"{path2['progress_percent']}% ({path2['completed']}/{path2['total_topics']})",
    )

    # ── 10. Dashboard / performance analysis page ──────────────────
    print("\n10. Dashboard + performance analysis")
    st, d = req("GET", "/api/dashboard/", token=token)
    check("GET /api/dashboard/ -> 200 (was 422 before)", st == 200, f"status={st} {json.dumps(d)[:150]}")
    if st == 200:
        check("stats show 2 attempts", d["stats"]["total_attempts"] == 2, json.dumps(d["stats"])[:160])
        check("average accuracy computed", d["stats"]["average_accuracy"] == 60.0, f"{d['stats']['average_accuracy']}")
        check("weak/average/excellent buckets counted", d["stats"]["weak_count"] == 1 and d["stats"]["excellent_count"] == 1, f"weak={d['stats']['weak_count']} exc={d['stats']['excellent_count']}")
        check("performance history has both attempts", len(d["performance_history"]) == 2, f"{len(d['performance_history'])} rows")
        check(
            "weak_topics is a list (topic 1 was mastered, so it is not weak)",
            isinstance(d["weak_topics"], list),
            json.dumps(d["weak_topics"])[:160],
        )
        check("recent recommendation present", bool(d.get("recent_recommendation")), json.dumps(d.get("recent_recommendation"))[:140])

    st, h = req("GET", "/api/dashboard/performance-history", token=token)
    check("GET /api/dashboard/performance-history -> 200 list", st == 200 and isinstance(h, list) and len(h) == 2, f"status={st}")

    # ── 10b. Weak topic detection ──────────────────────────────────
    print("\n10b. Weak topic detection")
    st, res = submit_quiz(token, topic_id + 2, target_correct=1, seconds=600)
    check("submitting a weak attempt on another topic -> 200", st == 200, f"status={st}")
    st, d = req("GET", "/api/dashboard/", token=token)
    weak_names = [w["name"] for w in d.get("weak_topics", [])]
    check(
        "a topic last scored at 10% shows up as a weak topic",
        st == 200 and len(weak_names) >= 1,
        json.dumps(d.get("weak_topics"))[:200],
    )
    check(
        "the mastered topic is NOT listed as weak",
        path["current_topic"]["name"] not in weak_names,
        f"weak={weak_names}",
    )

    # ── 11. Q-learning visualisation ───────────────────────────────
    print("\n11. Q-learning visualisation")
    st, d = req("GET", "/api/qlearning/q-table", token=token)
    check("GET /api/qlearning/q-table -> 200", st == 200, f"status={st}")
    check("Q-table covers all 9 states x 4 actions", len(d.get("states", [])) == 9 and len(d.get("actions", [])) == 4, f"{len(d.get('states',[]))}x{len(d.get('actions',[]))}")
    check("learned cells recorded for this student", len(d.get("learned_cells", [])) >= 2, f"{len(d.get('learned_cells', []))} learned")

    st, d = req("GET", "/api/qlearning/last-decision", token=token)
    check("GET /api/qlearning/last-decision -> 200", st == 200, f"status={st}")
    check(
        "last-decision includes q_values (the frontend chart needs it)",
        st == 200 and isinstance(d.get("q_values"), dict) and len(d["q_values"]) == 4,
        json.dumps(d.get("q_values"))[:160],
    )

    # ── 12. Per-student isolation ──────────────────────────────────
    print("\n12. Per-student Q-table isolation")
    email2 = f"other.{run_id}@test.com"
    st, d2 = req("POST", "/api/auth/signup", {"name": "Other", "email": email2, "password": "secret123"})
    token2 = d2.get("access_token", "")
    st, d2 = req("GET", "/api/qlearning/last-decision", token=token2)
    check("a brand-new student has no last decision", st == 200 and d2.get("current_state") is None, json.dumps(d2)[:140])
    st, t2 = req("GET", "/api/qlearning/q-table", token=token2)
    check("new student's Q-table has no learned cells", len(t2.get("learned_cells", [])) == 0, f"{len(t2.get('learned_cells', []))} learned")

    # ── 13. Every subject in the catalogue is usable ───────────────
    print("\n13. No dead-end subjects")
    st, d = req("GET", "/api/subjects/options")
    combos = 0
    dead_ends = []
    for edu in d["educations"]:
        for dept in d["departments"][edu]:
            for yr in d["years"]:
                q = urllib.parse.urlencode({"education": edu, "year": yr, "department": dept})
                st, subs = req("GET", f"/api/subjects/?{q}", token=token)
                if st != 200:
                    dead_ends.append(f"{edu}/{yr}/{dept} -> HTTP {st}")
                    continue
                if subs:
                    combos += 1
                    if any(s["topic_count"] == 0 for s in subs):
                        dead_ends.append(f"{edu}/{yr}/{dept} offers a subject with no topics")
    check("subject queries succeed for every education/department/year", not dead_ends,
          "; ".join(dead_ends[:3]))
    check("at least one populated combination exists", combos > 0, f"{combos} combinations offer subjects")

    # ── 14. A non-ML subject runs the full loop ────────────────────
    print("\n14. Full loop on a second subject (not Machine Learning)")
    q = urllib.parse.urlencode({"education": "B.Tech", "year": "1st Year", "department": "Computer Science"})
    st, subs = req("GET", f"/api/subjects/?{q}", token=token)
    check("B.Tech/1st Year/CS has subjects", st == 200 and len(subs) > 0,
          json.dumps([(s['name'], s['topic_count']) for s in subs])[:160])
    if subs:
        sid = subs[0]["id"]
        req("POST", f"/api/profile/select-subject?subject_id={sid}", token=token)
        st, lp = req("GET", f"/api/topics/learning-path/{sid}", token=token)
        check("learning path is non-empty", st == 200 and lp["total_topics"] > 0,
              f"{lp.get('total_topics')} topics")
        if lp["total_topics"]:
            tid = lp["current_topic"]["id"]
            st, qs = req("GET", f"/api/quiz/questions/{tid}", token=token)
            check("its quiz has 10-15 questions", st == 200 and 10 <= qs["total_questions"] <= 15,
                  f"{qs.get('total_questions')} questions")
            st, res = submit_quiz(token, tid, target_correct=qs["total_questions"], seconds=420)
            check("quiz submits and returns a Q-learning decision", st == 200 and "q_learning_viz" in res,
                  f"status={st} action={res.get('rl_action')}")

    print("\n" + "=" * 60)
    if _failures:
        print(f"RESULT: {len(_failures)} FAILURE(S)")
        for f in _failures:
            print(f"  - {f}")
        return 1
    print("RESULT: all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
