"""Static diagrams that do not depend on training results."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "05_Results_and_Graphs"
GRAPH.mkdir(parents=True, exist_ok=True)


def workflow_diagram():
    fig, ax = plt.subplots(figsize=(11, 6.2))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 6.4)
    ax.axis("off")
    ax.set_title("RL Workflow — Adaptive Traffic Signal Control", fontsize=14, pad=8)

    boxes = [
        (0.3, 4.2, 2.2, 1.3, "Environment\nqueues, phase,\nmin-green timer"),
        (3.0, 4.2, 2.2, 1.3, "State S_t\n(qN,qS,qE,qW,\nφ, t_green)"),
        (5.7, 4.2, 2.2, 1.3, "Agent\nε-greedy over Q"),
        (8.4, 4.2, 2.2, 1.3, "Action A_t\nkeep / switch"),
        (8.4, 1.6, 2.2, 1.3, "Reward R_{t+1}\n−wait −spill −switch"),
        (5.7, 1.6, 2.2, 1.3, "Next state S_{t+1}\narrivals + discharge"),
        (3.0, 1.6, 2.2, 1.3, "TD / Dyna\nupdate Q"),
        (0.3, 1.6, 2.2, 1.3, "Learned policy\nπ(s)=argmax Q"),
    ]
    for x, y, w, h, txt in boxes:
        ax.add_patch(
            FancyBboxPatch(
                (x, y), w, h, boxstyle="round,pad=0.03,rounding_size=0.15",
                facecolor="#e8f1fb", edgecolor="#1f4e79", linewidth=1.4,
            )
        )
        ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=8.5)

    arrows = [
        ((2.5, 4.85), (3.0, 4.85)),
        ((5.2, 4.85), (5.7, 4.85)),
        ((7.9, 4.85), (8.4, 4.85)),
        ((9.5, 4.2), (9.5, 2.9)),
        ((8.4, 2.25), (7.9, 2.25)),
        ((5.7, 2.25), (5.2, 2.25)),
        ((3.0, 2.25), (2.5, 2.25)),
        ((1.4, 2.9), (1.4, 4.2)),
    ]
    for (x1, y1), (x2, y2) in arrows:
        ax.add_patch(
            FancyArrowPatch(
                (x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=12,
                linewidth=1.3, color="#333333",
            )
        )
    fig.tight_layout()
    fig.savefig(GRAPH / "rl_workflow.png")
    plt.close(fig)


def intersection_sketch():
    fig, ax = plt.subplots(figsize=(6.2, 6.2))
    ax.set_xlim(-3.2, 3.2)
    ax.set_ylim(-3.2, 3.2)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Four-approach intersection abstraction", fontsize=12)
    # roads
    ax.add_patch(plt.Rectangle((-0.7, -3), 1.4, 6, color="#d9d9d9"))
    ax.add_patch(plt.Rectangle((-3, -0.7), 6, 1.4, color="#d9d9d9"))
    ax.add_patch(plt.Rectangle((-0.7, -0.7), 1.4, 1.4, color="#fff2cc", ec="#333"))
    ax.text(0, 0, "Signal\nagent", ha="center", va="center", fontsize=8)
    ax.text(0, 2.6, "N queue", ha="center", fontsize=9)
    ax.text(0, -2.7, "S queue", ha="center", fontsize=9)
    ax.text(2.6, 0.15, "E", ha="center", fontsize=9)
    ax.text(-2.6, 0.15, "W", ha="center", fontsize=9)
    ax.annotate("Phase 0: NS green", xy=(0, 1.2), xytext=(1.4, 2.0),
                arrowprops=dict(arrowstyle="->"), fontsize=8)
    ax.annotate("Phase 1: EW green", xy=(1.2, 0), xytext=(1.5, -1.8),
                arrowprops=dict(arrowstyle="->"), fontsize=8)
    fig.tight_layout()
    fig.savefig(GRAPH / "intersection_sketch.png")
    plt.close(fig)


if __name__ == "__main__":
    workflow_diagram()
    intersection_sketch()
    print("static figures ok")
