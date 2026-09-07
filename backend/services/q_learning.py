"""
Q-Learning Reinforcement Learning Service for AdaptiveLearn.

Implements the Q-Learning algorithm to adaptively choose the best learning
action for each student based on their performance state.

Q-Learning Update Rule:
    Q(s, a) = Q(s, a) + α [r + γ * max(Q(s', a')) - Q(s, a)]

Where:
    s  = current state (e.g. "Weak_Slow")  -> performance_level + "_" + learning_speed
    a  = action taken (REVISION, PRACTICE, CONTINUE, ADVANCED)
    α  = learning rate (0.1)
    γ  = discount factor (0.9)
    r  = reward received
    s' = next state

The Q-table is stored **per student**, so each learner's recommendations come
from their own accumulated experience.
"""

import random
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from ..models.q_table import QTable

# ── Hyperparameters ────────────────────────────────────────────────
ALPHA = 0.1          # Learning rate
GAMMA = 0.9          # Discount factor
EPSILON = 0.1        # Exploration rate (ε-greedy)

# Seconds we consider "reasonable" for one quiz question. Used to decide
# whether a student answered Fast / Normal / Slow.
SECONDS_PER_QUESTION = 60.0

# ── States ─────────────────────────────────────────────────────────
PERFORMANCE_LEVELS = ["Weak", "Average", "Excellent"]
LEARNING_SPEEDS = ["Slow", "Normal", "Fast"]
ALL_STATES = [f"{p}_{s}" for p in PERFORMANCE_LEVELS for s in LEARNING_SPEEDS]

# ── Actions ────────────────────────────────────────────────────────
ACTIONS = ["REVISION", "PRACTICE", "CONTINUE", "ADVANCED"]

# ── Action masking (safety constraint) ─────────────────────────────
# ε-greedy exploration is for gathering experience, but these actions have a
# real side effect: CONTINUE/ADVANCED move the student forward. Without a
# constraint, a 10% random draw could tell a student who scored 2/10 to "move
# to the next topic". So exploration is restricted to actions that are
# admissible for the observed performance level:
#   Weak      -> may revise or practise, never skip ahead
#   Average   -> may revise, practise, or continue
#   Excellent -> may practise, continue, or go advanced (never forced to revise)
ALLOWED_ACTIONS = {
    "Weak": ["REVISION", "PRACTICE"],
    "Average": ["REVISION", "PRACTICE", "CONTINUE"],
    "Excellent": ["PRACTICE", "CONTINUE", "ADVANCED"],
}


def allowed_actions(state: str) -> list[str]:
    """Actions the agent may actually take from this state."""
    perf, _, _ = state.partition("_")
    return ALLOWED_ACTIONS.get(perf, ACTIONS)

# ── Reward Map ─────────────────────────────────────────────────────
REWARD_MAP = {
    ("Excellent", "Fast"):   +10,
    ("Excellent", "Normal"):  +8,
    ("Excellent", "Slow"):    +5,
    ("Average",   "Fast"):    +8,
    ("Average",   "Normal"):  +5,
    ("Average",   "Slow"):    +2,
    ("Weak",      "Fast"):    +2,
    ("Weak",      "Normal"):  -5,
    ("Weak",      "Slow"):   -10,
}

# ── Informed initialisation ────────────────────────────────────────
# A freshly created Q-table is all zeros, so `max()` over ties would always
# return the first action in the list ("REVISION") — meaning a student who
# scores 100% on their very first quiz would be told to revise. We seed the
# table with a domain prior that encodes the intended pedagogy; Q-Learning
# then moves away from that prior as the student accumulates real evidence.
_PERF_AFFINITY = {
    #                action      Weak  Average  Excellent
    "REVISION":  {"Weak":  3.0, "Average":  1.0, "Excellent": -1.0},
    "PRACTICE":  {"Weak":  1.0, "Average":  3.0, "Excellent":  0.0},
    "CONTINUE":  {"Weak": -1.0, "Average":  2.0, "Excellent":  3.5},
    "ADVANCED":  {"Weak": -2.0, "Average":  0.0, "Excellent":  3.5},
}

_SPEED_AFFINITY = {
    #                action      Slow   Normal  Fast
    "REVISION":  {"Slow":  1.5, "Normal":  0.0, "Fast": -0.5},
    "PRACTICE":  {"Slow":  0.5, "Normal":  0.5, "Fast": -0.5},
    "CONTINUE":  {"Slow": -0.5, "Normal":  0.5, "Fast":  0.5},
    "ADVANCED":  {"Slow": -1.5, "Normal":  0.0, "Fast":  1.5},
}

# Effect an action has on the estimated next state (used for bootstrapping).
_ACTION_EFFECT = {
    "REVISION": {"perf": +1, "speed": +1},   # revising lifts a struggling student
    "PRACTICE": {"perf": +1, "speed":  0},
    "CONTINUE": {"perf":  0, "speed": +1},
    "ADVANCED": {"perf": +1, "speed": +1},
}


def initial_q(state: str, action: str) -> float:
    """Prior Q-value for a (state, action) pair before any learning."""
    perf, _, speed = state.partition("_")
    return round(
        _PERF_AFFINITY[action].get(perf, 0.0) + _SPEED_AFFINITY[action].get(speed, 0.0),
        6,
    )


@dataclass
class QLDecision:
    """Result of a Q-Learning decision step."""
    current_state: str
    performance_level: str
    learning_speed: str
    chosen_action: str
    reward: int
    q_values: dict = field(default_factory=dict)
    q_values_before: dict = field(default_factory=dict)
    q_value_after: float = 0.0
    max_next_q: float = 0.0
    all_q_table: dict = field(default_factory=dict)
    next_state: str = ""
    allowed_actions: list = field(default_factory=list)
    alpha: float = ALPHA
    gamma: float = GAMMA
    epsilon: float = EPSILON
    explored: bool = False


class QLearningAgent:
    """Q-Learning agent that learns to recommend learning actions for one student."""

    def __init__(self, db: Session, user_id: int = 0):
        self.db = db
        self.user_id = user_id
        self._load_q_table()

    # ── Public API ─────────────────────────────────────────────────

    def decide(
        self,
        accuracy: float,
        time_taken_seconds: int,
        total_questions: int,
    ) -> QLDecision:
        """
        Given the latest quiz results, determine the student state,
        compute the reward, update Q-values, and return the best action.
        """
        perf = classify_performance(accuracy)
        speed = classify_speed(time_taken_seconds, total_questions)
        current_state = f"{perf}_{speed}"

        reward = REWARD_MAP.get((perf, speed), 0)

        # ε-greedy action selection, restricted to admissible actions
        action, explored = self._epsilon_greedy(current_state)

        # Snapshot before the update so the UI can show what changed.
        q_values_before = {a: self._get_q(current_state, a) for a in ACTIONS}

        next_state = self._estimate_next_state(current_state, action)
        max_next_q = max(self._get_q(next_state, a) for a in ACTIONS)
        q_value_after = self._update_q(current_state, action, reward, next_state)

        q_values = {a: self._get_q(current_state, a) for a in ACTIONS}

        full_table = {
            s: {a: self._get_q(s, a) for a in ACTIONS} for s in ALL_STATES
        }

        return QLDecision(
            current_state=current_state,
            performance_level=perf,
            learning_speed=speed,
            chosen_action=action,
            reward=reward,
            q_values=q_values,
            q_values_before=q_values_before,
            q_value_after=q_value_after,
            max_next_q=max_next_q,
            all_q_table=full_table,
            next_state=next_state,
            allowed_actions=allowed_actions(current_state),
            explored=explored,
        )

    # ── Internals ──────────────────────────────────────────────────

    def _load_q_table(self):
        """Load this student's Q-table from the DB, or initialise it with the prior."""
        rows = (
            self.db.query(QTable)
            .filter(QTable.user_id == self.user_id)
            .all()
        )
        self._q: dict[str, dict[str, float]] = {
            s: {a: initial_q(s, a) for a in ACTIONS} for s in ALL_STATES
        }
        for r in rows:
            if r.state in self._q and r.action in self._q[r.state]:
                self._q[r.state][r.action] = r.q_value

        if not rows:
            self._persist_all()

    def _get_q(self, state: str, action: str) -> float:
        return self._q.get(state, {}).get(action, 0.0)

    def _set_q(self, state: str, action: str, value: float):
        self._q.setdefault(state, {})[action] = value

    def _epsilon_greedy(self, state: str) -> tuple[str, bool]:
        """
        Choose an action using the ε-greedy policy over the admissible actions.
        Returns (action, explored).
        """
        candidates = allowed_actions(state)
        if random.random() < EPSILON:
            return random.choice(candidates), True
        q_vals = {a: self._get_q(state, a) for a in candidates}
        return max(q_vals, key=q_vals.get), False

    def _update_q(self, state: str, action: str, reward: int, next_state: str) -> float:
        """
        Apply the Q-Learning update rule and persist the row:
            Q(s,a) ← Q(s,a) + α [r + γ max_a' Q(s',a') − Q(s,a)]
        """
        current_q = self._get_q(state, action)
        max_next_q = max(self._get_q(next_state, a) for a in ACTIONS)
        new_q = round(
            current_q + ALPHA * (reward + GAMMA * max_next_q - current_q), 6
        )
        self._set_q(state, action, new_q)

        row = (
            self.db.query(QTable)
            .filter(
                QTable.user_id == self.user_id,
                QTable.state == state,
                QTable.action == action,
            )
            .first()
        )
        if row:
            row.q_value = new_q
        else:
            self.db.add(
                QTable(
                    user_id=self.user_id,
                    state=state,
                    action=action,
                    q_value=new_q,
                )
            )
        self.db.commit()
        return new_q

    def _persist_all(self):
        """Write this student's full Q-table to the database."""
        existing = {
            (r.state, r.action): r
            for r in self.db.query(QTable)
            .filter(QTable.user_id == self.user_id)
            .all()
        }
        for state, actions in self._q.items():
            for action, value in actions.items():
                row = existing.get((state, action))
                if row:
                    row.q_value = value
                else:
                    self.db.add(
                        QTable(
                            user_id=self.user_id,
                            state=state,
                            action=action,
                            q_value=value,
                        )
                    )
        self.db.commit()

    @staticmethod
    def _estimate_next_state(current_state: str, action: str) -> str:
        """Estimate the state the student is likely to reach after this action."""
        perf, _, speed = current_state.partition("_")
        effect = _ACTION_EFFECT.get(action, {"perf": 0, "speed": 0})

        pi = PERFORMANCE_LEVELS.index(perf) + effect["perf"]
        si = LEARNING_SPEEDS.index(speed) + effect["speed"]

        pi = max(0, min(pi, len(PERFORMANCE_LEVELS) - 1))
        si = max(0, min(si, len(LEARNING_SPEEDS) - 1))
        return f"{PERFORMANCE_LEVELS[pi]}_{LEARNING_SPEEDS[si]}"


# ── Shared classification helpers ──────────────────────────────────

def classify_performance(accuracy: float) -> str:
    """Bucket an accuracy percentage into a performance level."""
    if accuracy >= 80:
        return "Excellent"
    elif accuracy >= 60:
        return "Average"
    return "Weak"


def classify_speed(time_taken_seconds: int, total_questions: int) -> str:
    """
    Bucket answering speed relative to a per-question budget.

    Measuring against the topic's *study* time made almost everyone "Fast"
    (a 30-minute topic implies a 30-minute budget for a 10-question quiz),
    so we compare against a per-question allowance instead.
    """
    n = max(total_questions, 1)
    ratio = (time_taken_seconds / n) / max(SECONDS_PER_QUESTION, 1.0)
    if ratio <= 0.6:
        return "Fast"
    elif ratio <= 1.4:
        return "Normal"
    return "Slow"
