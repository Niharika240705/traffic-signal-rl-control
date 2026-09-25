"""Shared tabular-RL helpers (numpy only)."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np

from environment import TrafficSignalEnv, rollout_greedy


def epsilon_greedy(q_row: np.ndarray, epsilon: float, rng: np.random.Generator) -> int:
    if rng.random() < epsilon:
        return int(rng.integers(0, q_row.shape[0]))
    # break ties randomly among maximisers
    max_v = np.max(q_row)
    candidates = np.flatnonzero(np.isclose(q_row, max_v))
    return int(rng.choice(candidates))


def expected_q(q_row: np.ndarray, epsilon: float) -> float:
    """E_{a ~ eps-greedy}[Q(s,a)] for Expected SARSA."""
    n = q_row.shape[0]
    greedy = np.max(q_row)
    n_max = np.sum(np.isclose(q_row, greedy))
    pi = np.full(n, epsilon / n, dtype=np.float64)
    pi[np.isclose(q_row, greedy)] += (1.0 - epsilon) / n_max
    return float(np.dot(pi, q_row))


def linear_epsilon(ep: int, n_episodes: int, eps_start: float, eps_end: float) -> float:
    frac = min(1.0, ep / max(n_episodes - 1, 1))
    return eps_start + frac * (eps_end - eps_start)


def moving_average(x: np.ndarray, window: int = 50) -> np.ndarray:
    if len(x) == 0:
        return x
    w = min(window, len(x))
    kernel = np.ones(w) / w
    return np.convolve(x, kernel, mode="valid")


def episodes_to_stability(rewards: np.ndarray, window: int = 80, tol: float = 0.08) -> int:
    """
    First episode at which the rolling mean is within `tol` relative of the
    mean of the final `window` episodes, and stays there for `window/2` steps.
    Returns n_episodes if never stable.
    """
    if len(rewards) < window * 2:
        return int(len(rewards))
    final = float(np.mean(rewards[-window:]))
    scale = max(abs(final), 1.0)
    ma = moving_average(rewards, window)
    # ma[i] corresponds to episodes [i, i+window)
    hold = max(window // 2, 10)
    run = 0
    for i, v in enumerate(ma):
        if abs(v - final) / scale <= tol:
            run += 1
            if run >= hold:
                return int(i + window)  # episode index (1-based length)
        else:
            run = 0
    return int(len(rewards))


def save_artifacts(
    out_dir: Path,
    name: str,
    q_table: np.ndarray,
    rewards: np.ndarray,
    extra: Dict,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    np.save(out_dir / "q_table.npy", q_table)
    np.save(out_dir / "rewards.npy", rewards)
    policy = np.argmax(q_table, axis=1).astype(np.int32)
    np.save(out_dir / "policy.npy", policy)

    eval_stats = rollout_greedy(q_table, n_episodes=40, seed=2026)
    (out_dir / "behavior_trace.txt").write_text(eval_stats["trace"], encoding="utf-8")

    metrics = {
        "algorithm": name,
        "n_episodes": int(len(rewards)),
        "mean_reward_all": float(np.mean(rewards)),
        "mean_reward_last100": float(np.mean(rewards[-100:])),
        "std_reward_last100": float(np.std(rewards[-100:])),
        "cumulative_reward": float(np.sum(rewards)),
        "episodes_to_stability": episodes_to_stability(rewards),
        "policy_quality_mean_return": eval_stats["mean_return"],
        "policy_quality_std_return": eval_stats["std_return"],
        "eval_success_rate": eval_stats["success_rate"],
        **extra,
    }
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    summary = [
        f"Algorithm: {name}",
        f"Episodes: {len(rewards)}",
        f"Mean reward (all): {metrics['mean_reward_all']:.2f}",
        f"Mean reward (last 100): {metrics['mean_reward_last100']:.2f}",
        f"Std (last 100): {metrics['std_reward_last100']:.2f}",
        f"Cumulative reward: {metrics['cumulative_reward']:.1f}",
        f"Episodes to stability: {metrics['episodes_to_stability']}",
        f"Greedy eval mean return: {metrics['policy_quality_mean_return']:.2f}",
        f"Eval success rate: {metrics['eval_success_rate']:.3f}",
        f"Wall time (s): {extra.get('wall_time_sec', 'n/a')}",
        "",
        "Final greedy behaviour (first 25 steps of eval episode 0):",
        eval_stats["trace"],
    ]
    (out_dir / "summary.txt").write_text("\n".join(summary), encoding="utf-8")


TrainFn = Callable[..., Tuple[np.ndarray, np.ndarray, Dict]]
