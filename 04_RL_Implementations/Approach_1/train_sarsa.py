"""
Approach 1 — SARSA (on-policy TD control)

Update: Q(S,A) <- Q(S,A) + α [ R + γ Q(S',A') - Q(S,A) ]
A' is the action actually taken in S' (ε-greedy), so the target follows the
behaviour policy. Suitable when the deployed traffic controller will keep a
small amount of exploration (safety probing / demand drift).
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common import epsilon_greedy, linear_epsilon, save_artifacts  # noqa: E402
from environment import TrafficSignalEnv, EnvConfig  # noqa: E402


def train_sarsa(
    n_episodes: int = 1400,
    alpha: float = 0.12,
    gamma: float = 0.95,
    eps_start: float = 1.0,
    eps_end: float = 0.05,
    seed: int = 11,
) -> tuple:
    rng = np.random.default_rng(seed)
    env = TrafficSignalEnv(EnvConfig(seed=seed))
    q = np.zeros((env.n_states, env.n_actions), dtype=np.float64)
    rewards = np.zeros(n_episodes, dtype=np.float64)
    n_exploratory = 0
    n_steps = 0

    t0 = time.perf_counter()
    for ep in range(n_episodes):
        eps = linear_epsilon(ep, n_episodes, eps_start, eps_end)
        s = env.reset(seed=seed * 10000 + ep)
        a = epsilon_greedy(q[s], eps, rng)
        G = 0.0
        done = False
        while not done:
            s2, r, done, _ = env.step(a)
            G += r
            n_steps += 1
            if not done:
                a2 = epsilon_greedy(q[s2], eps, rng)
                if q[s2, a2] != np.max(q[s2]):
                    n_exploratory += 1
                td_target = r + gamma * q[s2, a2]
                next_a = a2
            else:
                td_target = r
                next_a = 0
            q[s, a] += alpha * (td_target - q[s, a])
            s, a = s2, next_a if not done else a
        rewards[ep] = G
    wall = time.perf_counter() - t0
    extra = {
        "wall_time_sec": wall,
        "alpha": alpha,
        "gamma": gamma,
        "eps_start": eps_start,
        "eps_end": eps_end,
        "n_steps": n_steps,
        "exploratory_fraction": float(n_exploratory / max(n_steps, 1)),
    }
    return q, rewards, extra


def main():
    out = Path(__file__).resolve().parent
    q, rewards, extra = train_sarsa()
    save_artifacts(out, "SARSA", q, rewards, extra)
    print(f"SARSA done in {extra['wall_time_sec']:.1f}s | last-100 mean {rewards[-100:].mean():.2f}")


if __name__ == "__main__":
    main()
