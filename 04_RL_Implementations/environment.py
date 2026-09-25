"""
Custom Gym-style environment: Dynamic Traffic Signal Control at a Single Intersection.

This is a discrete, tabular abstraction of a four-approach urban intersection.
Each approach is modelled as a 1-D occupancy queue (Gridworld-style lane cells).
Vehicles arrive stochastically and discharge only when their phase is green.

Assumption (explicit): we do not use real loop-detector traces. Arrivals are
synthetic Poisson processes with a mild time-of-day imbalance so that the
control problem is sequential, stochastic, and non-trivial.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# Hyper-parameters of the physical abstraction (shared by all four approaches)
# ---------------------------------------------------------------------------
MAX_QUEUE = 5          # occupancy per approach, in discrete cells 0..MAX_QUEUE
N_APPROACHES = 4       # North, South, East, West
N_PHASES = 2           # 0 = NS green / EW red; 1 = EW green / NS red
MIN_GREEN = 4          # minimum green time (steps) before a switch is allowed
EPISODE_LENGTH = 120   # one simulated peak-period "episode"
N_ACTIONS = 2          # 0 = keep current phase, 1 = request switch
SPILLBACK_PENALTY = 8.0
SWITCH_COST = 0.35


@dataclass
class EnvConfig:
    max_queue: int = MAX_QUEUE
    min_green: int = MIN_GREEN
    episode_length: int = EPISODE_LENGTH
    lambda_ns: float = 0.42   # mean arrivals per step on N and on S
    lambda_ew: float = 0.28   # mean arrivals per step on E and on W
    discharge: int = 1        # vehicles served per green approach per step
    stall_prob: float = 0.08  # chance a queued vehicle fails to move
    seed: Optional[int] = None


class TrafficSignalEnv:
    """
    Discrete-time MDP for a two-phase signal.

    State (fully observed in this simulation):
        (q_N, q_S, q_E, q_W, phase, t_green)
        queues in {0,...,MAX_QUEUE}, phase in {0,1},
        t_green in {0,...,MIN_GREEN} (clipped; encodes whether min-green is met).

    Action:
        0 keep, 1 switch. A switch is ignored if t_green < MIN_GREEN
        (hard constraint — the environment enforces it).

    Reward (to be maximised):
        r = -sum(queues) - SPILLBACK_PENALTY * n_blocked_arrivals - SWITCH_COST * switched
        Waiting is always costly; overflow (lost demand) is extra-costly;
        needless switching is mildly penalised.
    """

    metadata = {"render_modes": ["ansi"]}

    def __init__(self, config: Optional[EnvConfig] = None):
        self.cfg = config or EnvConfig()
        self.rng = np.random.default_rng(self.cfg.seed)

        self.n_queue_levels = self.cfg.max_queue + 1
        self.n_t_levels = self.cfg.min_green + 1  # 0 .. min_green inclusive
        self.n_states = (
            (self.n_queue_levels ** N_APPROACHES) * N_PHASES * self.n_t_levels
        )
        self.n_actions = N_ACTIONS
        self.action_space_n = N_ACTIONS
        self.observation_space_n = self.n_states

        self.queues = np.zeros(N_APPROACHES, dtype=np.int32)
        self.phase = 0
        self.t_green = 0
        self.t = 0
        self._last_info: Dict = {}

    # -- Gym-style API -------------------------------------------------------
    def reset(self, seed: Optional[int] = None) -> int:
        if seed is not None:
            self.rng = np.random.default_rng(seed)
        # Start with a modest residual queue (not always empty — more realistic).
        self.queues = self.rng.integers(0, 3, size=N_APPROACHES, dtype=np.int32)
        self.phase = int(self.rng.integers(0, N_PHASES))
        self.t_green = int(self.rng.integers(0, self.cfg.min_green + 1))
        self.t = 0
        return self._encode()

    def step(self, action: int) -> Tuple[int, float, bool, Dict]:
        action = int(action)
        switched = 0
        if action == 1 and self.t_green >= self.cfg.min_green:
            self.phase = 1 - self.phase
            self.t_green = 0
            switched = 1
        else:
            self.t_green = min(self.t_green + 1, self.cfg.min_green)

        served = self._discharge()
        arrivals, blocked = self._arrivals()

        total_q = int(self.queues.sum())
        reward = -float(total_q) - SPILLBACK_PENALTY * blocked - SWITCH_COST * switched

        self.t += 1
        done = self.t >= self.cfg.episode_length
        info = {
            "total_queue": total_q,
            "blocked": blocked,
            "switched": switched,
            "served": served,
            "arrivals": arrivals,
            "spillback": int(blocked > 0),
            "success": int(total_q <= 6),  # "under control" occupancy
        }
        self._last_info = info
        return self._encode(), reward, done, info

    def render(self) -> str:
        names = ["N", "S", "E", "W"]
        bars = "  ".join(
            f"{n}:{'█' * int(q)}{'.' * (self.cfg.max_queue - int(q))}"
            for n, q in zip(names, self.queues)
        )
        phase_name = "NS-green" if self.phase == 0 else "EW-green"
        text = (
            f"t={self.t:3d}  phase={phase_name:9s}  t_green={self.t_green}  {bars}"
        )
        return text

    # -- Dynamics ------------------------------------------------------------
    def _discharge(self) -> int:
        served = 0
        if self.phase == 0:
            active = (0, 1)  # N, S
        else:
            active = (2, 3)  # E, W
        for i in active:
            if self.queues[i] > 0:
                if self.rng.random() > self.cfg.stall_prob:
                    self.queues[i] -= self.cfg.discharge
                    served += 1
        return served

    def _arrivals(self) -> Tuple[int, int]:
        # Mild within-episode non-stationarity: NS heavier in first half,
        # EW slightly heavier later (peak-direction flip).
        frac = self.t / max(self.cfg.episode_length, 1)
        lam_ns = self.cfg.lambda_ns * (1.15 - 0.30 * frac)
        lam_ew = self.cfg.lambda_ew * (0.85 + 0.40 * frac)
        lambdas = [lam_ns, lam_ns, lam_ew, lam_ew]
        arrived = 0
        blocked = 0
        for i, lam in enumerate(lambdas):
            n_new = int(self.rng.poisson(lam))
            for _ in range(n_new):
                if self.queues[i] < self.cfg.max_queue:
                    self.queues[i] += 1
                    arrived += 1
                else:
                    blocked += 1
        return arrived, blocked

    # -- Discrete state encoding --------------------------------------------
    def _encode(self) -> int:
        s = 0
        base = self.n_queue_levels
        for q in self.queues:
            s = s * base + int(q)
        s = s * N_PHASES + int(self.phase)
        s = s * self.n_t_levels + int(self.t_green)
        return s

    def decode(self, s: int) -> Tuple[np.ndarray, int, int]:
        t_green = s % self.n_t_levels
        s //= self.n_t_levels
        phase = s % N_PHASES
        s //= N_PHASES
        queues = np.zeros(N_APPROACHES, dtype=np.int32)
        for i in range(N_APPROACHES - 1, -1, -1):
            queues[i] = s % self.n_queue_levels
            s //= self.n_queue_levels
        return queues, phase, t_green

    def greedy_policy_table(self, q_table: np.ndarray) -> np.ndarray:
        return np.argmax(q_table, axis=1).astype(np.int32)


def make_env(seed: Optional[int] = None) -> TrafficSignalEnv:
    cfg = EnvConfig(seed=seed)
    return TrafficSignalEnv(cfg)


def describe_env() -> str:
    env = TrafficSignalEnv()
    return (
        f"TrafficSignalEnv: |S|={env.n_states}, |A|={env.n_actions}, "
        f"T={env.cfg.episode_length}, max_queue={env.cfg.max_queue}, "
        f"min_green={env.cfg.min_green}"
    )


def rollout_greedy(
    q_table: np.ndarray,
    n_episodes: int = 30,
    seed: int = 123,
) -> Dict:
    """Evaluate a deterministic greedy policy; used for policy-quality metric."""
    env = TrafficSignalEnv(EnvConfig(seed=seed))
    returns: List[float] = []
    success_steps = 0
    total_steps = 0
    traces: List[str] = []
    for ep in range(n_episodes):
        s = env.reset(seed=seed + ep)
        G = 0.0
        done = False
        lines = [f"=== greedy eval episode {ep} ==="]
        while not done:
            a = int(np.argmax(q_table[s]))
            s, r, done, info = env.step(a)
            G += r
            success_steps += info["success"]
            total_steps += 1
            if ep == 0 and env.t <= 25:
                lines.append(env.render() + f"  a={a} r={r:6.2f}")
        returns.append(G)
        if ep == 0:
            traces = lines
    return {
        "mean_return": float(np.mean(returns)),
        "std_return": float(np.std(returns)),
        "success_rate": float(success_steps / max(total_steps, 1)),
        "trace": "\n".join(traces),
        "returns": returns,
    }
