"""Train all four approaches sequentially, then build comparison artefacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "Approach_1"))
sys.path.insert(0, str(ROOT / "Approach_2"))
sys.path.insert(0, str(ROOT / "Approach_3"))
sys.path.insert(0, str(ROOT / "Approach_4"))

from train_sarsa import train_sarsa  # noqa: E402
from train_qlearning import train_qlearning  # noqa: E402
from train_expected_sarsa import train_expected_sarsa  # noqa: E402
from train_dyna_q import train_dyna_q  # noqa: E402
from common import save_artifacts  # noqa: E402
from visualize_results import build_all_figures  # noqa: E402


def main():
    jobs = [
        ("SARSA", ROOT / "Approach_1", train_sarsa),
        ("Q-learning", ROOT / "Approach_2", train_qlearning),
        ("Expected SARSA", ROOT / "Approach_3", train_expected_sarsa),
        ("Dyna-Q", ROOT / "Approach_4", train_dyna_q),
    ]
    for name, out, fn in jobs:
        print(f"\n===== Training {name} =====")
        q, rewards, extra = fn()
        save_artifacts(out, name, q, rewards, extra)
        print(
            f"{name}: wall={extra['wall_time_sec']:.1f}s  "
            f"last100={float(np.mean(rewards[-100:])):.2f}"
        )

    metrics_path = build_all_figures()
    print(f"\nComparison written to {metrics_path}")


if __name__ == "__main__":
    main()
