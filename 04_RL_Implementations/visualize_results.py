"""Generate comparison tables and matplotlib figures from trained artefacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from common import moving_average  # noqa: E402
from environment import TrafficSignalEnv  # noqa: E402

GRAPH_DIR = ROOT.parent / "05_Results_and_Graphs"
CMP_DIR = ROOT.parent / "06_Performance_Comparison"

APPROACHES = [
    ("SARSA", ROOT / "Approach_1"),
    ("Q-learning", ROOT / "Approach_2"),
    ("Expected SARSA", ROOT / "Approach_3"),
    ("Dyna-Q", ROOT / "Approach_4"),
]


def _style():
    plt.rcParams.update(
        {
            "figure.dpi": 140,
            "savefig.dpi": 160,
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.labelsize": 11,
            "legend.fontsize": 9,
            "axes.grid": True,
            "grid.alpha": 0.3,
        }
    )


def load_rewards():
    data = {}
    for name, folder in APPROACHES:
        data[name] = np.load(folder / "rewards.npy")
    return data


def load_metrics():
    rows = []
    for name, folder in APPROACHES:
        m = json.loads((folder / "metrics.json").read_text(encoding="utf-8"))
        rows.append(m)
    return rows


def exploration_efficiency(m: dict) -> float:
    """
    Improvement in mean return per unit of exploratory fraction.
    Higher is better: more learning extracted from exploration.
    """
    gain = m["mean_reward_last100"] - m["mean_reward_all"]
    expl = max(m.get("exploratory_fraction", 0.05), 1e-6)
    return float(gain / expl)


def comparison_table(rows: list) -> dict:
    table = {}
    for m in rows:
        name = m["algorithm"]
        table[name] = {
            "average_reward_last100": m["mean_reward_last100"],
            "episodes_to_stability": m["episodes_to_stability"],
            "cumulative_reward": m["cumulative_reward"],
            "computational_time_sec": m["wall_time_sec"],
            "stability_std_last100": m["std_reward_last100"],
            "policy_quality_eval_return": m["policy_quality_mean_return"],
            "success_rate_eval": m["eval_success_rate"],
            "exploration_efficiency": exploration_efficiency(m),
            "mean_reward_all": m["mean_reward_all"],
        }
    return table


def metric_definitions() -> str:
    return """
METRIC DEFINITIONS (explicit)

1. Average reward
   Mean undiscounted episode return over the last 100 training episodes.
   Return G = sum_{t=0}^{T-1} r_t with T = episode length.

2. Convergence speed / episodes to stability
   Smallest episode index i such that the 80-episode rolling mean stays within
   8% of the final-100-episode mean for at least 40 consecutive rolling windows.
   Smaller is faster convergence.

3. Cumulative reward
   Sum of episode returns over the entire training run. Reflects both
   transient (exploration) and asymptotic performance.

4. Computational time
   Wall-clock seconds for the training loop on the host machine
   (time.perf_counter).

5. Stability / variance
   Standard deviation of episode return over the last 100 training episodes.
   Lower is more stable.

6. Policy quality
   Mean return of the greedy policy (ε = 0) over 40 independent evaluation
   episodes with fixed evaluation seeds.

7. Success rate
   Fraction of evaluation time-steps in which total occupancy across the four
   approaches is ≤ 6 (queues 'under control', no chronic congestion).

8. Exploration efficiency
   (mean_reward_last100 − mean_reward_all) / exploratory_action_fraction.
   Measures how much late-training improvement was obtained per unit of
   exploration during learning.
""".strip()


def build_all_figures() -> Path:
    _style()
    GRAPH_DIR.mkdir(parents=True, exist_ok=True)
    CMP_DIR.mkdir(parents=True, exist_ok=True)

    rewards = load_rewards()
    rows = load_metrics()
    table = comparison_table(rows)
    (CMP_DIR / "metrics_table.json").write_text(json.dumps(table, indent=2), encoding="utf-8")
    (CMP_DIR / "metric_definitions.txt").write_text(metric_definitions(), encoding="utf-8")

    # Markdown + CSV table
    headers = [
        "Algorithm",
        "Avg reward (last 100)",
        "Episodes to stability",
        "Cumulative reward",
        "Time (s)",
        "Std last 100",
        "Policy quality (eval G)",
        "Success rate",
        "Exploration efficiency",
    ]
    lines = ["|" + "|".join(headers) + "|", "|" + "|".join(["---"] * len(headers)) + "|"]
    csv_rows = [",".join(headers)]
    for name, folder in APPROACHES:
        t = table[name]
        vals = [
            name,
            f"{t['average_reward_last100']:.2f}",
            str(int(t["episodes_to_stability"])),
            f"{t['cumulative_reward']:.1f}",
            f"{t['computational_time_sec']:.1f}",
            f"{t['stability_std_last100']:.2f}",
            f"{t['policy_quality_eval_return']:.2f}",
            f"{t['success_rate_eval']:.3f}",
            f"{t['exploration_efficiency']:.2f}",
        ]
        lines.append("|" + "|".join(vals) + "|")
        csv_rows.append(",".join(vals))
    (CMP_DIR / "comparison_table.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (CMP_DIR / "comparison_table.csv").write_text("\n".join(csv_rows) + "\n", encoding="utf-8")

    names = [n for n, _ in APPROACHES]
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

    # 1. Individual learning curves
    for (name, _), color in zip(APPROACHES, colors):
        r = rewards[name]
        ma = moving_average(r, 50)
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.plot(r, alpha=0.25, color=color, label="Episode return")
        ax.plot(np.arange(len(ma)) + 49, ma, color=color, lw=2.0, label="50-episode moving average")
        ax.set_title(f"Learning Curve — {name}")
        ax.set_xlabel("Episode")
        ax.set_ylabel("Episode return G")
        ax.legend()
        fig.tight_layout()
        fig.savefig(GRAPH_DIR / f"learning_curve_{name.replace(' ', '_').replace('-', '_')}.png")
        plt.close(fig)

    # 2. Overlay reward vs episode
    fig, ax = plt.subplots(figsize=(9, 5))
    for (name, _), color in zip(APPROACHES, colors):
        ma = moving_average(rewards[name], 50)
        ax.plot(np.arange(len(ma)) + 49, ma, color=color, lw=2.0, label=name)
    ax.set_title("Reward vs Episode (50-episode moving average, all approaches)")
    ax.set_xlabel("Episode")
    ax.set_ylabel("Smoothed episode return")
    ax.legend()
    fig.tight_layout()
    fig.savefig(GRAPH_DIR / "reward_vs_episode_overlay.png")
    plt.close(fig)

    # 3. Overlay raw (light) + also cumulative
    fig, ax = plt.subplots(figsize=(9, 5))
    for (name, _), color in zip(APPROACHES, colors):
        ax.plot(np.cumsum(rewards[name]), color=color, lw=2.0, label=name)
    ax.set_title("Cumulative Training Return vs Episode")
    ax.set_xlabel("Episode")
    ax.set_ylabel("Cumulative return")
    ax.legend()
    fig.tight_layout()
    fig.savefig(GRAPH_DIR / "cumulative_reward.png")
    plt.close(fig)

    # 4. Bar charts for metrics
    def bar_plot(keys, ylabel, title, fname, higher_better=True):
        fig, ax = plt.subplots(figsize=(8, 4.8))
        vals = [table[n][keys] for n in names]
        bars = ax.bar(names, vals, color=colors, edgecolor="black", linewidth=0.5)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, b.get_height(), f"{v:.2f}", ha="center", va="bottom", fontsize=8)
        fig.tight_layout()
        fig.savefig(GRAPH_DIR / fname)
        plt.close(fig)

    bar_plot("average_reward_last100", "Mean return", "Average Reward (last 100 episodes)", "bar_average_reward.png")
    bar_plot("episodes_to_stability", "Episodes", "Episodes to Stability (lower is faster)", "bar_convergence.png")
    bar_plot("computational_time_sec", "Seconds", "Computational Time (training wall-clock)", "bar_time.png")
    bar_plot("stability_std_last100", "Std. of return", "Stability: Std. Dev. of Last 100 Returns", "bar_stability.png")
    bar_plot("policy_quality_eval_return", "Eval mean G", "Policy Quality (greedy evaluation return)", "bar_policy_quality.png")
    bar_plot("success_rate_eval", "Fraction of steps", "Success Rate (queue ≤ 6 during evaluation)", "bar_success_rate.png")
    bar_plot("exploration_efficiency", "Δreturn / explore frac.", "Exploration Efficiency", "bar_exploration_efficiency.png")

    # 5. Box plot of last 200 episode returns
    fig, ax = plt.subplots(figsize=(8, 5))
    data = [rewards[n][-200:] for n in names]
    bp = ax.boxplot(data, tick_labels=names, patch_artist=True)
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
    ax.set_title("Return Distribution (last 200 training episodes)")
    ax.set_ylabel("Episode return")
    fig.tight_layout()
    fig.savefig(GRAPH_DIR / "box_last200_returns.png")
    plt.close(fig)

    # 6. Policy heatmap: switch probability vs (NS queue, EW queue) averaged over other factors
    env = TrafficSignalEnv()
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    axes = axes.ravel()
    for ax, (name, folder), color in zip(axes, APPROACHES, colors):
        policy = np.load(folder / "policy.npy")
        heat = np.zeros((env.n_queue_levels, env.n_queue_levels))
        counts = np.zeros_like(heat)
        for s, a in enumerate(policy):
            q, phase, t_green = env.decode(s)
            ns = min(env.cfg.max_queue, int(q[0] + q[1]))
            ew = min(env.cfg.max_queue, int(q[2] + q[3]))
            # Map combined 0..10 into 0..5 by clipping already; use min of pair instead
            ns_b = int(max(q[0], q[1]))
            ew_b = int(max(q[2], q[3]))
            heat[ns_b, ew_b] += a  # 1 = prefer switch
            counts[ns_b, ew_b] += 1
        with np.errstate(divide="ignore", invalid="ignore"):
            heat = np.divide(heat, counts, out=np.zeros_like(heat), where=counts > 0)
        im = ax.imshow(heat, origin="lower", cmap="RdYlBu", vmin=0, vmax=1)
        ax.set_title(f"P(switch | max NS, max EW) — {name}")
        ax.set_xlabel("Max(E, W) queue")
        ax.set_ylabel("Max(N, S) queue")
        fig.colorbar(im, ax=ax, fraction=0.046)
    fig.tight_layout()
    fig.savefig(GRAPH_DIR / "policy_heatmaps.png")
    plt.close(fig)

    # observations
    best_avg = max(names, key=lambda n: table[n]["average_reward_last100"])
    best_eval = max(names, key=lambda n: table[n]["policy_quality_eval_return"])
    fastest = min(names, key=lambda n: table[n]["episodes_to_stability"])
    most_stable = min(names, key=lambda n: table[n]["stability_std_last100"])
    notes = f"""
OBSERVATIONS
============
Best average training reward (last 100): {best_avg}
Best greedy evaluation policy: {best_eval}
Fastest episodes-to-stability: {fastest}
Most stable (lowest last-100 std): {most_stable}

Interpretation notes are expanded in the Technical Project Report (Section 8–10)
and in 06_Performance_Comparison/comparison_observations.txt.
""".strip()
    (CMP_DIR / "comparison_observations.txt").write_text(notes, encoding="utf-8")
    return CMP_DIR / "metrics_table.json"


if __name__ == "__main__":
    build_all_figures()
    print("Figures written to", GRAPH_DIR)
