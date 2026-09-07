"""
Q-Learning Reinforcement Learning Service for AdaptiveLearn.

Implements the Q-Learning algorithm to adaptively choose the best learning
action for each student based on their performance state.

Q-Learning Update Rule:
    Q(s, a) = Q(s, a) + α [r + γ * max(Q(s', a')) - Q(s, a)]

Where:
    s  = current state (e.g. "Weak_Slow")
    a  = action taken (REVISION, PRACTICE, CONTINUE, ADVANCED)
    α  = learning rate (0.1)
    γ  = discount factor (0.9)
    r  = reward received
    s' = next state
"""

import random
from dataclasses import dataclass

import numpy as np
from sqlalchemy.orm import Session

from ..models.q_table import QTable

# ── Hyperparameters ────────────────────────────────────────────────
ALPHA = 0.1          # Learning rate
GAMMA = 0.9          # Discount factor
EPSILON = 0.1        # Exploration rate (ε-greedy)

# ── States ─────────────────────────────────────────────────────────
PERFORMANCE_LEVELS = ["Weak", "Average", "Excellent"]
LEARNING_SPEEDS = ["Slow", "Normal", "Fast"]
ALL_STATES = [f"{p}_{s}" for p in PERFORMANCE_LEVELS for s in LEARNING_SPEEDS]

# ── Actions ────────────────────────────────────────────────────────
ACTIONS = ["REVISION", "PRACTICE", "CONTINUE", "ADVANCED"]

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


@dataclass
class QLDecision:
    """Result of a Q-Learning decision step."""
    current_state: str
    performance_level: str
    learning_speed: str
    chosen_action: str
    reward: int
    q_values: dict[str, float]
    all_q_table: dict[str, dict[str, float]]
    next_state: str


class QLearningAgent:
    """Q-Learning agent that learns to recommend learning actions."""

    def __init__(self, db: Session):
        self.db = db
        self._load_q_table()

    # ── Public API ─────────────────────────────────────────────────

    def decide(
        self,
        accuracy: float,
        time_taken_seconds: int,
        topic_study_time: int,
    ) -> QLDecision:
        """
        Given the latest quiz results, determine the student state,
        compute the reward, update Q-values, and return the best action.
        """
        perf = self._classify_performance(accuracy)
        speed = self._classify_speed(time_taken_seconds, topic_study_time)
        current_state = f"{perf}_{speed}"

        reward = REWARD_MAP.get((perf, speed), 0)

        # Determine next state (simplified: same state transitions)
        next_state = self._estimate_next_state(current_state, reward)

        # Epsilon-greedy action selection
        action = self._epsilon_greedy(current_state)

        # Q-Learning update
        self._update_q(current_state, action, reward, next_state)

        # Build Q-value snapshot for the current state
        q_values = {a: self._get_q(current_state, a) for a in ACTIONS}

        # Full Q-table snapshot for visualisation
        full_table = {}
        for s in ALL_STATES:
            full_table[s] = {a: self._get_q(s, a) for a in ACTIONS}

        return QLDecision(
            current_state=current_state,
            performance_level=perf,
            learning_speed=speed,
            chosen_action=action,
            reward=reward,
            q_values=q_values,
            all_q_table=full_table,
            next_state=next_state,
        )

    # ── Internals ──────────────────────────────────────────────────

    def _load_q_table(self):
        """Load existing Q-table from DB or initialise with zeros."""
        rows = self.db.query(QTable).all()
        if rows:
            self._q: dict[str, dict[str, float]] = {}
            for r in rows:
                self._q.setdefault(r.state, {})[r.action] = r.q_value
        else:
            self._q = {s: {a: 0.0 for a in ACTIONS} for s in ALL_STATES}
            self._persist_all()

    def _get_q(self, state: str, action: str) -> float:
        return self._q.get(state, {}).get(action, 0.0)

    def _set_q(self, state: str, action: str, value: float):
        self._q.setdefault(state, {})[action] = value

    def _epsilon_greedy(self, state: str) -> str:
        """Choose action using ε-greedy policy."""
        if random.random() < EPSILON:
            return random.choice(ACTIONS)
        q_vals = self._q.get(state, {a: 0.0 for a in ACTIONS})
        return max(q_vals, key=q_vals.get)

    def _update_q(self, state: str, action: str, reward: int, next_state: str):
        """
        Apply the Q-Learning update rule:
        Q(s,a) ← Q(s,a) + α [r + γ max_a' Q(s',a') − Q(s,a)]
        """
        current_q = self._get_q(state, action)
        max_next_q = max(
            (self._get_q(next_state, a) for a in ACTIONS), default=0.0
        )
        new_q = current_q + ALPHA * (reward + GAMMA * max_next_q - current_q)
        self._set_q(state, action, round(new_q, 6))

        # Persist to DB
        row = (
            self.db.query(QTable)
            .filter(QTable.state == state, QTable.action == action)
            .first()
        )
        if row:
            row.q_value = round(new_q, 6)
        else:
            self.db.add(QTable(state=state, action=action, q_value=round(new_q, 6)))
        self.db.commit()

    def _persist_all(self):
        """Write the full Q-table to the database."""
        for state, actions in self._q.items():
            for action, value in actions.items():
                existing = (
                    self.db.query(QTable)
                    .filter(QTable.state == state, QTable.action == action)
                    .first()
                )
                if existing:
                    existing.q_value = value
                else:
                    self.db.add(QTable(state=state, action=action, q_value=value))
        self.db.commit()

    @staticmethod
    def _classify_performance(accuracy: float) -> str:
        if accuracy >= 80:
            return "Excellent"
        elif accuracy >= 60:
            return "Average"
        return "Weak"

    @staticmethod
    def _classify_speed(time_taken: int, study_time: int) -> str:
        ratio = time_taken / max(study_time, 1)
        if ratio <= 0.5:
            return "Fast"
        elif ratio <= 1.0:
            return "Normal"
        return "Slow"

    @staticmethod
    def _estimate_next_state(current_state: str, reward: int) -> str:
        """Simple heuristic to estimate the next state for bootstrapping."""
        parts = current_state.split("_")
        perf, speed = parts[0], parts[1]

        perf_order = ["Weak", "Average", "Excellent"]
        speed_order = ["Slow", "Normal", "Fast"]

        pi = perf_order.index(perf)
        si = speed_order.index(speed)

        if reward >= 8:
            pi = min(pi + 1, 2)
            si = min(si + 1, 2)
        elif reward >= 5:
            si = min(si + 1, 2)
        elif reward <= -5:
            pi = max(pi - 1, 0)

        return f"{perf_order[pi]}_{speed_order[si]}"
