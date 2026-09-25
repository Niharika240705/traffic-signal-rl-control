"""
Approach 3 — Expected SARSA

Update: Q(S,A) <- Q(S,A) + α [ R + γ Σ_a π(a|S') Q(S',a) - Q(S,A) ]
Uses the expected value under the current ε-greedy policy instead of a
sampled next action. Lower variance than SARSA; still on-policy w.r.t. π.
Useful for noisy traffic arrivals where sampled SARSA targets jitter.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common import epsilon_greedy, expected_q, linear_epsilon, save_artifacts  # noqa: E402
from environment import TrafficSignalEnv, EnvConfig  # noqa: E402


def train_expected_sarsa(
    n_episodes: int = 1400,
    alpha: float = 0.12,
    gamma: float = 0.95,
    eps_start: float = 1.0,
    eps_end: float = 0.05,
    seed: int = 33,
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
        G = 0.0
        done = False
        while not done:
            a = epsilon_greedy(q[s], eps, rng)
            if q[s, a] != np.max(q[s]):
                n_exploratory += 1
            s2, r, done, _ = env.step(a)
            G += r
            n_steps += 1
            next_v = 0.0 if done else expected_q(q[s2], eps)
            q[s, a] += alpha * ((r + gamma * next_v) - q[s, a])
            s = s2
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
    q, rewards, extra = train_expected_sarsa()
    save_artifacts(out, "Expected SARSA", q, rewards, extra)
    print(f"Expected SARSA done in {extra['wall_time_sec']:.1f}s | last-100 mean {rewards[-100:].mean():.2f}")


if __name__ == "__main__":
    main()
