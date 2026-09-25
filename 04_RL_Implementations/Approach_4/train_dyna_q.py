"""
Approach 4 — Dyna-Q (Q-learning + learned model + planning)

Direct RL update is identical to Q-learning. After each real step the agent:
  1. stores (S,A,R,S') in an empirical transition model,
  2. performs n planning updates by replaying sampled experienced pairs.

Traffic dynamics are locally repeatable (queue + phase + arrival noise), so a
tabular model can reuse experience and speed up credit assignment compared
with one-step Q-learning alone.
"""

from __future__ import annotations

import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common import epsilon_greedy, linear_epsilon, save_artifacts  # noqa: E402
from environment import TrafficSignalEnv, EnvConfig  # noqa: E402


def train_dyna_q(
    n_episodes: int = 1400,
    alpha: float = 0.12,
    gamma: float = 0.95,
    eps_start: float = 1.0,
    eps_end: float = 0.05,
    n_planning: int = 8,
    seed: int = 44,
) -> tuple:
    rng = np.random.default_rng(seed)
    env = TrafficSignalEnv(EnvConfig(seed=seed))
    q = np.zeros((env.n_states, env.n_actions), dtype=np.float64)
    rewards = np.zeros(n_episodes, dtype=np.float64)

    # Empirical model: (s, a) -> dict[(s2, r_key)] -> count
    # Reward is stored rounded to 2 decimals so the key stays hashable.
    model: dict = defaultdict(lambda: defaultdict(int))
    sa_keys: list = []
    sa_set = set()

    n_exploratory = 0
    n_steps = 0

    def remember(s, a, r, s2):
        key = (int(s), int(a))
        r_key = round(float(r), 2)
        model[key][(int(s2), r_key)] += 1
        if key not in sa_set:
            sa_set.add(key)
            sa_keys.append(key)

    def sample_model():
        s, a = sa_keys[int(rng.integers(0, len(sa_keys)))]
        outcomes = model[(s, a)]
        items = list(outcomes.items())
        counts = np.array([c for _, c in items], dtype=np.float64)
        counts /= counts.sum()
        idx = int(rng.choice(len(items), p=counts))
        (s2, r_key), _ = items[idx]
        return s, a, float(r_key), int(s2)

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
            max_next = 0.0 if done else float(np.max(q[s2]))
            q[s, a] += alpha * ((r + gamma * max_next) - q[s, a])
            remember(s, a, r, s2)

            # Planning: replay from the learned (stochastic) model.
            if sa_keys:
                for _ in range(n_planning):
                    ps, pa, pr, ps2 = sample_model()
                    q[ps, pa] += alpha * ((pr + gamma * float(np.max(q[ps2]))) - q[ps, pa])
            s = s2
        rewards[ep] = G
    wall = time.perf_counter() - t0
    extra = {
        "wall_time_sec": wall,
        "alpha": alpha,
        "gamma": gamma,
        "eps_start": eps_start,
        "eps_end": eps_end,
        "n_planning": n_planning,
        "n_steps": n_steps,
        "model_sa_pairs": len(sa_keys),
        "exploratory_fraction": float(n_exploratory / max(n_steps, 1)),
    }
    return q, rewards, extra


def main():
    out = Path(__file__).resolve().parent
    q, rewards, extra = train_dyna_q()
    save_artifacts(out, "Dyna-Q", q, rewards, extra)
    print(
        f"Dyna-Q done in {extra['wall_time_sec']:.1f}s | last-100 mean {rewards[-100:].mean():.2f} "
        f"| model pairs {extra['model_sa_pairs']}"
    )


if __name__ == "__main__":
    main()
