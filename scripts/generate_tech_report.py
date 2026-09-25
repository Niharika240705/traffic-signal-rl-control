"""Component 2 technical project report (15–20 pages target)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from docx.enum.text import WD_ALIGN_PARAGRAPH  # noqa: F401
from docx.shared import Inches, Pt

from docx_style import (  # noqa: E402
    GRAPHS,
    ROOT,
    add_bullets,
    add_caption,
    add_heading_custom,
    add_para,
    add_picture_centered,
    add_table,
    set_run_font,
    setup_doc,
)

OUT = ROOT / "07_Technical_Project_Report" / "CIA3_Component2_Technical_Project_Report.docx"
METRICS = json.loads((ROOT / "06_Performance_Comparison" / "metrics_table.json").read_text())


def g(name, key, fmt=".2f"):
    v = METRICS[name][key]
    if isinstance(v, float):
        return format(v, fmt)
    return str(v)


def cover(doc):
    for _ in range(1):
        add_para(doc, "", align="center", first_line=False, space_after=0)
    add_para(doc, "[Institution Name]", align="center", first_line=False, bold=True, size=14)
    add_para(doc, "Department of Computer Science and Engineering", align="center", first_line=False)
    add_para(doc, "", align="center", first_line=False)
    add_para(
        doc,
        "CIA-3  |  Component 2: Micro Project  |  Technical Project Report",
        align="center",
        first_line=False,
        bold=True,
        size=13,
    )
    add_para(doc, "Course: Reinforcement Learning", align="center", first_line=False)
    add_para(doc, "", align="center", first_line=False)
    add_para(
        doc,
        "Comparative Study of SARSA, Q-learning, Expected SARSA and Dyna-Q\n"
        "for Adaptive Traffic Signal Control in a Custom Discrete Simulator",
        align="center",
        first_line=False,
        bold=True,
        size=16,
    )
    add_para(doc, "", align="center", first_line=False)
    add_para(doc, "Team Members", align="center", first_line=False, bold=True)
    for m in ["Member 1", "Member 2", "Member 3", "Member 4"]:
        add_para(doc, m, align="center", first_line=False, space_after=2)
    add_para(doc, "September 2026", align="center", first_line=False)
    doc.add_page_break()


def fig(doc, fname, caption, width=5.9):
    path = GRAPHS / fname
    if path.exists():
        add_picture_centered(doc, path, width=width)
        add_caption(doc, caption)


def build():
    doc = setup_doc()
    cover(doc)

    add_heading_custom(doc, "2. Abstract", 1)
    add_para(
        doc,
        "This micro-project continues the Component 1 case study of adaptive traffic signal "
        "control at an isolated four-approach intersection. A custom Gym-style environment "
        "exposes a 6,480-state tabular MDP whose actions are keep-or-switch phase decisions "
        "and whose reward penalises waiting, spillback, and switch chatter. Four conceptually "
        "related temporal-difference methods were implemented from scratch in Python/NumPy: "
        "on-policy SARSA, off-policy Q-learning, Expected SARSA, and Dyna-Q with an empirical "
        "stochastic model and eight planning steps. Each algorithm trained for 1,400 episodes "
        "of 120 steps with identical stepsize, discount, and ε-schedule. On last-100-episode "
        f"mean return, Dyna-Q reached {g('Dyna-Q','average_reward_last100')} versus "
        f"{g('Expected SARSA','average_reward_last100')} for Expected SARSA, "
        f"{g('SARSA','average_reward_last100')} for SARSA, and "
        f"{g('Q-learning','average_reward_last100')} for Q-learning. Greedy evaluation "
        f"confirmed the same ranking (Dyna-Q eval return {g('Dyna-Q','policy_quality_eval_return')}). "
        "Q-learning met the rolling-mean stability test earliest but plateaued at a weaker "
        "policy. The main conclusion is that, for this stochastic queueing MDP, planning with "
        "a learned model (Dyna-Q) and expected on-policy targets (Expected SARSA) outperform "
        "plain one-step SARSA and Q-learning on asymptotic return, at the cost of extra "
        "compute for Dyna-Q. Safe RL shielding is recommended before any field interpretation.",
    )

    add_heading_custom(doc, "3. Keywords", 1)
    add_para(
        doc,
        "Reinforcement Learning; Traffic Signal Control; SARSA; Q-learning; Expected SARSA; "
        "Dyna-Q; Real-time Sequential Decision Making.",
        first_line=False,
    )

    add_heading_custom(doc, "4. Introduction", 1)
    add_para(
        doc,
        "Background. Isolated intersections remain the elementary control unit of urban "
        "networks. Even when a city later coordinates corridors, the local cabinet must still "
        "decide, at each tick, whether to extend the current green or to serve the opposing "
        "movement. Demand is noisy, peak direction can reverse inside a single peak window, "
        "and the cost of a late switch is delayed spillback rather than an immediate labelled "
        "error. These properties place the problem in sequential stochastic control.",
    )
    add_para(
        doc,
        "Why reinforcement learning. Classical Webster splits and gap-based actuation are "
        "open-loop or myopic. They do not estimate a discounted action-value for keep versus "
        "switch. RL agents can learn such values by interacting with a simulator when field "
        "logs and a calibrated microscopic model are unavailable—as is the case for this "
        "coursework. We therefore built a compact discrete environment whose occupancy cells "
        "play the role of a Gridworld lane, and we trained tabular agents that remain within "
        "the algorithmic vocabulary of Units 4 and 5.",
    )
    add_para(
        doc,
        "Four approaches, briefly. SARSA evaluates the ε-greedy behaviour policy, which is "
        "appropriate if a little exploration would remain at deployment. Q-learning evaluates "
        "the greedy policy while exploring, matching a simulation-train / greedy-deploy "
        "workflow. Expected SARSA replaces the sampled next-action bootstrap with an "
        "expectation under π, reducing variance when Poisson arrivals make SARSA’s target "
        "noisy. Dyna-Q layers a learned transition model and n planning updates on top of "
        "Q-learning, reusing scarce occupancy patterns. One-line justifications: SARSA — "
        "on-policy TD for exploratory controllers; Q-learning — off-policy TD for greedy "
        "cabinets; Expected SARSA — lower-variance on-policy TD; Dyna-Q — model-based "
        "acceleration of Q-learning when dynamics are locally repeatable.",
    )
    add_para(
        doc,
        "Objective. Implement a shared environment and four from-scratch training loops; "
        "produce real learning curves (not fabricated); compare the methods on at least four "
        "explicitly defined metrics; analyse why the ranking occurred; and document a Safe RL "
        "innovation consistent with Component 1.",
    )

    add_heading_custom(doc, "5. Literature Review", 1)
    add_para(
        doc,
        "Wiering [3] treated junctions as multi-agent RL problems and showed that local "
        "Q-learning can reduce waiting relative to fixed plans, at the cost of coordination "
        "externalities. Prashanth and Bhatnagar [4] introduced function approximation for "
        "signal control, addressing the tabular curse of dimensionality that we still accept "
        "in this micro-project by capping occupancy at five. Van der Pol and Oliehoek [5] and "
        "Wei et al. [6] moved to deep RL (DQN-style) for richer detector features; IntelliLight "
        "in particular reported gains over actuated control on a calibrated simulator. Chen "
        "et al. [7] scaled decentralized deep RL toward large networks. Haydari and Yılmaz [9] "
        "survey the ITS literature and stress sim-to-real, safety, and reward specification "
        "as open issues. García and Fernández [8] survey Safe RL, which we adopt as the "
        "innovation layer rather than as a trained constrained optimiser in this delivery.",
    )
    add_para(
        doc,
        "Strengths of prior work include demonstrated delay reductions in simulation and an "
        "increasingly standard MDP framing (queues, phases, waiting rewards). Limitations "
        "include reliance on heavy simulators (SUMO, VISSIM) that are difficult to reimplement "
        "from scratch for a four-person coursework, sparse reporting of tabular TD ablations, "
        "and frequent omission of hard timing constraints. Our contribution is not a new "
        "SOTA controller; it is a transparent, fully from-scratch comparison of four TD "
        "methods on one documented MDP, with reproducible artefacts.",
    )
    add_para(
        doc,
        "Classical traffic control remains the baseline family: Webster’s formula [2] and "
        "demand-responsive logic such as OPAC [10] still explain deployed cabinets. RL should "
        "be read as a data-driven alternative for the split decision, not as a replacement for "
        "the conflict monitor.",
    )

    add_heading_custom(doc, "6. Methodology", 1)
    add_heading_custom(doc, "6.1 Case study recap", 2)
    add_para(
        doc,
        "The case study (Component 1) defined an isolated two-phase intersection in which a "
        "single agent chooses keep or switch. The long-term objective is discounted return "
        "equal to negative waiting, spillback, and switch cost. Rule-based splits are treated "
        "as insufficient because they do not estimate delayed value under a directional demand "
        "flip. The same MDP is used here without retuning the physics between algorithms.",
    )
    fig(doc, "intersection_sketch.png", "Figure 1. Intersection abstraction (N/S versus E/W phases).", 4.3)

    add_heading_custom(doc, "6.2 RL environment design", 2)
    add_para(
        doc,
        "State. s = (q_N, q_S, q_E, q_W, φ, t_green) with q_i ∈ {0,…,5}, φ ∈ {0,1}, "
        "t_green ∈ {0,…,4}. Integer encoding yields |S| = 6,480. Action. a ∈ {0,1} = "
        "{keep, switch}; switches with t_green < 4 are no-ops. Reward. "
        "R = −Σ q_i − 8 n_blocked − 0.35·1_switched. Episode. T = 120 steps, then terminate "
        "(episodic MDP). Environment type. Stochastic, dynamic (time-varying Poisson means), "
        "fully observed in simulation, discrete state and action, simulation-based learning. "
        "Assumption: arrivals are synthetic; stall probability 0.08 approximates lost time.",
    )
    add_para(
        doc,
        "Transition sketch. If phase 0 is green, approaches N and S each attempt to discharge "
        "one vehicle; E and W do not. Poisson arrivals are then added independently. Occupancy "
        "is clipped at MAX_QUEUE = 5; excess counts as blocked. The directional means start "
        "NS-heavy and become relatively more EW-heavy as t/T increases, so a static split is "
        "structurally suboptimal.",
    )

    add_heading_custom(doc, "6.3 Approach 1 — SARSA", 2)
    add_para(
        doc,
        "Explanation. SARSA is on-policy one-step TD control [1]. After transitioning "
        "(S, A, R, S′) and selecting A′ ∼ π_ε(·|S′), the update is "
        "Q(S,A) ← Q(S,A) + α[R + γ Q(S′,A′) − Q(S,A)]. Suitability. If the cabinet retains "
        "exploratory probes, the learned Q matches the behaviour that will actually run. "
        "Implementation. NumPy table; linear ε decay; random tie-break among greedy actions; "
        "training loop in Approach_1/train_sarsa.py; artefacts: rewards.npy, q_table.npy, "
        "policy.npy, metrics.json, behavior_trace.txt.",
    )

    add_heading_custom(doc, "6.4 Approach 2 — Q-learning", 2)
    add_para(
        doc,
        "Explanation. Off-policy TD control uses the greedy backup "
        "R + γ max_a Q(S′,a) regardless of the ε-greedy action that will be taken next [1]. "
        "Suitability. Matches simulation with exploration and greedy deployment. Risk: the "
        "max operator can overestimate under noisy rewards (addressed conceptually by Double "
        "Q-learning, not implemented here). Implementation. Approach_2/train_qlearning.py with "
        "the same α, γ, ε as SARSA so that differences are algorithmic rather than hyperparameter "
        "search artefacts. Seeds differ so that the four runs are independent stochastic trials.",
    )

    add_heading_custom(doc, "6.5 Approach 3 — Expected SARSA", 2)
    add_para(
        doc,
        "Explanation. The bootstrap target is Σ_a π_ε(a|S′) Q(S′,a), i.e. the expectation "
        "under the current ε-greedy policy rather than a single sampled A′ [1]. Suitability. "
        "Poisson arrivals make sampled SARSA targets noisy; taking the expectation reduces "
        "that source of variance while remaining on-policy with respect to π_ε. Implementation. "
        "Approach_3/train_expected_sarsa.py; π_ε puts probability ε/|A| on every action and "
        "splits the remaining 1−ε uniformly among greedy maximisers.",
    )

    add_heading_custom(doc, "6.6 Approach 4 — Dyna-Q", 2)
    add_para(
        doc,
        "Explanation. After each real Q-learning update, the pair (S,A) and the observed "
        "(S′,R) increment an empirical count model. Then n = 8 planning steps sample a "
        "previously seen (S,A) uniformly and sample (S′,R) from the empirical multinomial, "
        "applying the same Q-learning backup [1]. Suitability. Occupancy dynamics are locally "
        "repeatable even though they are stochastic; planning reuses those samples. "
        "Implementation. Approach_4/train_dyna_q.py. Assumption: the model is non-stationary "
        "in truth (arrival means drift with t) but the tabular model is time-aggregated, so "
        "planning is slightly misspecified. This is discussed in Section 10.",
    )
    fig(doc, "rl_workflow.png", "Figure 2. Shared interaction and learning loop.", 6.0)

    add_heading_custom(doc, "7. Experimental Setup", 1)
    add_para(
        doc,
        "Hardware/software. Experiments were run on a macOS (Darwin) host with CPython 3 in "
        "a project virtual environment. No GPU is required. Software: Python 3, NumPy 1.26+, "
        "Matplotlib 3.8+, python-docx and python-pptx only for reporting. No Gym/PettingZoo/"
        "Stable-Baselines3/Tianshou stack is used for learning—the environment is Gym-style "
        "in API shape (reset/step) but implemented locally.",
    )
    add_para(
        doc,
        "Environment configuration. MAX_QUEUE = 5, MIN_GREEN = 4, T = 120, λ_NS = 0.42, "
        "λ_EW = 0.28 with the documented linear drift, discharge = 1, stall probability = 0.08, "
        "spillback penalty = 8, switch cost = 0.35. Training: 1,400 episodes per algorithm. "
        "Evaluation: 40 greedy episodes with fixed seeds (2026 + i).",
    )
    add_table(
        doc,
        ["Hyperparameter", "Value", "Notes"],
        [
            ["α (learning rate)", "0.12", "Constant; not annealed"],
            ["γ (discount)", "0.95", "Values near-horizon waiting"],
            ["ε start → end", "1.0 → 0.05", "Linear in episode index"],
            ["Episodes", "1400", "Shared"],
            ["Planning steps n (Dyna-Q)", "8", "Per real interaction"],
            ["Seeds", "11 / 22 / 33 / 44", "SARSA / QL / ExpSARSA / Dyna-Q"],
        ],
    )
    add_para(
        doc,
        "Metric definitions (how each number is calculated).",
    )
    add_bullets(
        doc,
        [
            "Average reward: mean undiscounted episode return over the last 100 training episodes.",
            "Episodes to stability: first index where an 80-episode rolling mean stays within 8% of the final-100 mean for 40 consecutive windows (else 1400).",
            "Cumulative reward: sum of all 1,400 training returns (includes exploration).",
            "Computational time: wall-clock seconds of the training loop (time.perf_counter).",
            "Stability/variance: standard deviation of the last 100 training returns.",
            "Policy quality: mean greedy return over 40 evaluation episodes.",
            "Success rate: fraction of evaluation steps with total occupancy ≤ 6.",
            "Exploration efficiency: (last-100 mean − overall mean) / fraction of exploratory actions.",
        ],
    )

    add_heading_custom(doc, "8. Results", 1)
    add_para(
        doc,
        "All curves below are produced from the saved rewards.npy files of the four training "
        "runs. They are not schematic drawings.",
    )
    fig(doc, "learning_curve_SARSA.png", "Figure 3. SARSA learning curve (raw return and 50-episode moving average).")
    fig(doc, "learning_curve_Q_learning.png", "Figure 4. Q-learning learning curve.")
    fig(doc, "learning_curve_Expected_SARSA.png", "Figure 5. Expected SARSA learning curve.")
    fig(doc, "learning_curve_Dyna_Q.png", "Figure 6. Dyna-Q learning curve.")
    fig(doc, "reward_vs_episode_overlay.png", "Figure 7. Overlay of smoothed episode returns for all four approaches.")
    fig(doc, "cumulative_reward.png", "Figure 8. Cumulative training return versus episode.")

    add_para(
        doc,
        "Table 1 reports the quantitative comparison. Dyna-Q attains the best last-100 mean, "
        "the best greedy evaluation return, the best cumulative training return, the highest "
        "evaluation success rate, and the lowest late-training standard deviation. Expected "
        "SARSA is second on late mean return and best on exploration efficiency. Q-learning "
        "triggers the stability rule earliest (248 episodes) but with a weaker plateau. "
        "SARSA is slower to settle (740 episodes) and sits between Q-learning and Expected "
        "SARSA on late return.",
    )
    add_table(
        doc,
        ["Metric", "SARSA", "Q-learning", "Expected SARSA", "Dyna-Q"],
        [
            ["Avg reward last 100", g("SARSA", "average_reward_last100"), g("Q-learning", "average_reward_last100"), g("Expected SARSA", "average_reward_last100"), g("Dyna-Q", "average_reward_last100")],
            ["Episodes to stability", g("SARSA", "episodes_to_stability", ".0f"), g("Q-learning", "episodes_to_stability", ".0f"), g("Expected SARSA", "episodes_to_stability", ".0f"), g("Dyna-Q", "episodes_to_stability", ".0f")],
            ["Cumulative reward", g("SARSA", "cumulative_reward", ".1f"), g("Q-learning", "cumulative_reward", ".1f"), g("Expected SARSA", "cumulative_reward", ".1f"), g("Dyna-Q", "cumulative_reward", ".1f")],
            ["Time (s)", g("SARSA", "computational_time_sec"), g("Q-learning", "computational_time_sec"), g("Expected SARSA", "computational_time_sec"), g("Dyna-Q", "computational_time_sec")],
            ["Std last 100", g("SARSA", "stability_std_last100"), g("Q-learning", "stability_std_last100"), g("Expected SARSA", "stability_std_last100"), g("Dyna-Q", "stability_std_last100")],
            ["Eval policy quality", g("SARSA", "policy_quality_eval_return"), g("Q-learning", "policy_quality_eval_return"), g("Expected SARSA", "policy_quality_eval_return"), g("Dyna-Q", "policy_quality_eval_return")],
            ["Eval success rate", g("SARSA", "success_rate_eval", ".3f"), g("Q-learning", "success_rate_eval", ".3f"), g("Expected SARSA", "success_rate_eval", ".3f"), g("Dyna-Q", "success_rate_eval", ".3f")],
            ["Exploration efficiency", g("SARSA", "exploration_efficiency"), g("Q-learning", "exploration_efficiency"), g("Expected SARSA", "exploration_efficiency"), g("Dyna-Q", "exploration_efficiency")],
        ],
    )
    add_caption(doc, "Table 1. Performance comparison (computed from training artefacts). Returns are negative because the reward is a cost.")

    fig(doc, "bar_average_reward.png", "Figure 9. Average reward (last 100 episodes).")
    fig(doc, "bar_convergence.png", "Figure 10. Episodes to stability.")
    fig(doc, "bar_policy_quality.png", "Figure 11. Greedy evaluation return (policy quality).")
    fig(doc, "bar_success_rate.png", "Figure 12. Evaluation success rate.")
    fig(doc, "bar_stability.png", "Figure 13. Late-training return standard deviation.")
    fig(doc, "bar_time.png", "Figure 14. Training wall-clock time.")
    fig(doc, "bar_exploration_efficiency.png", "Figure 15. Exploration efficiency.")
    fig(doc, "box_last200_returns.png", "Figure 16. Box plot of the last 200 training returns.")
    fig(doc, "policy_heatmaps.png", "Figure 17. Policy heatmaps: empirical P(switch) versus max NS and max EW occupancy.")

    add_para(
        doc,
        "Observations. (1) All four agents improve from first-50-episode means near −930 to "
        "−970 toward last-100 means near −810 to −860, so learning is real, not a flat random "
        "policy. (2) Residual variance remains large (std ≈ 132–141) because Poisson demand "
        "and the mid-episode directional flip make some episodes intrinsically harder. (3) "
        "Success rates hover near 0.50–0.53: the occupancy cap and arrival rates were chosen "
        "to keep the MDP non-trivial; a saturated but still improving controller is expected. "
        "(4) Heatmaps show switch probability rising when the unserved direction is more "
        "loaded than the served one, which is qualitatively correct phase logic. (5) Dyna-Q’s "
        "cumulative-return curve lies above the others for most of training, indicating that "
        "planning helps during exploration, not only at the end.",
    )

    add_heading_custom(doc, "9. Comparative Analysis", 1)
    add_para(
        doc,
        "We compare on eight metrics (more than the required four): average reward, episodes "
        "to stability, cumulative reward, computational time, stability/variance, policy "
        "quality, success rate, and exploration efficiency.",
    )
    add_para(
        doc,
        "Average reward and policy quality. Ranking by last-100 mean and by greedy eval is "
        "identical: Dyna-Q > Expected SARSA > SARSA > Q-learning. The off-policy max operator "
        "did not yield the best greedy policy here. A plausible reason is overestimation plus "
        "a time-varying kernel: early-episode backups that assume the current greedy action "
        "is optimal under a later arrival regime inject bias that planning and expected "
        "targets dilute differently.",
    )
    add_para(
        doc,
        "Convergence speed. Q-learning looks “fastest” on the stability statistic because it "
        "settles early onto a mediocre plateau. That is not the same as being the best learner. "
        "Dyna-Q and SARSA keep improving longer, so they cross the 8% band later. The metric "
        "must therefore be read together with asymptotic return, not in isolation.",
    )
    add_para(
        doc,
        "Cumulative reward. Dyna-Q’s sum is the least negative, so its advantage is not only "
        "a last-window artefact. Expected SARSA beats SARSA slightly, consistent with "
        "lower-variance updates wasting fewer episodes on unlucky A′ samples.",
    )
    add_para(
        doc,
        "Computational time. SARSA and Q-learning are ~2.2–2.4 s; Expected SARSA ~5.7 s "
        "(extra inner product over actions, still |A|=2 so the gap is mostly Python overhead "
        "in the expected_q helper); Dyna-Q ~14.1 s because of eight planning updates and "
        "dictionary model sampling. For this |S|, all times are negligible; the ranking would "
        "matter more at larger n_planning or with function approximation.",
    )
    add_para(
        doc,
        "Stability, success, exploration efficiency. Dyna-Q is slightly more stable and more "
        "often “under control” at evaluation. Expected SARSA extracts the most late-training "
        "improvement per unit of exploration. Q-learning’s exploration efficiency is weakest, "
        "matching its smaller gap between overall mean and last-100 mean.",
    )
    add_para(
        doc,
        "Strengths and weaknesses. SARSA: simple, on-policy, but noisy targets. Q-learning: "
        "simple off-policy, early plateau, weaker asymptote here. Expected SARSA: best "
        "variance-adjusted on-policy learner in this set; slightly slower per step. Dyna-Q: "
        "best returns; heaviest compute; model ignores explicit time index. "
        "Best-performing algorithm overall: Dyna-Q, because it wins the metrics that describe "
        "deployed quality (eval return, late training return, success rate, cumulative return) "
        "with only a modest runtime penalty on this tabular problem.",
    )

    add_heading_custom(doc, "10. Discussion", 1)
    add_para(
        doc,
        "Why Dyna-Q and Expected SARSA performed better. The environment reuses similar "
        "(queue, phase, timer) tuples many times. Planning spreads a newly observed spillback "
        "cost to other previously visited pairs without waiting to re-encounter them. Expected "
        "SARSA avoids the extra noise of sampling A′ when ε is still large. Q-learning’s max "
        "backup is optimistic when both actions look similar under sparse visits, which is "
        "common early in a 6,480-state space.",
    )
    add_para(
        doc,
        "Effect of environment characteristics. Stochasticity inflates return variance for "
        "every method; no algorithm can drive std to zero while arrivals are Poisson. "
        "Dynamic (time-varying) demand hurts any time-aggregated model: Dyna-Q’s planning "
        "distribution mixes early-NS-peak and late-EW-peak transitions. That misspecification "
        "did not erase its advantage, but it cautions against inflating n_planning blindly. "
        "Partial observability is not present in the simulator; adding detector noise would "
        "likely shrink the gap between methods and motivate memory or a POMDP filter. "
        "The min-green constraint makes many switch actions ineffective; including t_green in "
        "the state is therefore essential, otherwise TD methods would average good and bad "
        "switch outcomes into one confused Q(s, switch).",
    )
    add_para(
        doc,
        "Limitations of the experiment. Single random seed per algorithm (four seeds total), "
        "not a 30-seed statistical test; constant α; no hyperparameter sweep; no SUMO "
        "validation; occupancy cap clips physics; two phases only; wall-clock times are "
        "machine-specific. The success-rate threshold (total queue ≤ 6) is a chosen operating "
        "definition, not a municipal SLA. These limitations are acceptable for a transparent "
        "coursework comparison but not for a deployment claim.",
    )

    add_heading_custom(doc, "11. Innovation Component", 1)
    add_para(
        doc,
        "As in Component 1, the innovation is Safe Reinforcement Learning with a hard action "
        "shield plus, optionally, a constrained-MDP cost for maximum wait. Technical depth: "
        "define A_safe(s) ⊆ {keep, switch} from predicates min_green(s), max_red(s), "
        "spillback_veto(s), and pedestrian_lock(s). The behaviour policy samples only from "
        "A_safe(s); if that set is a singleton, exploration is automatically suppressed. "
        "Q-learning then becomes ordinary Q-learning on the shielded MDP. For long-run "
        "constraints, store a cost critic Q_C and update a Lagrange multiplier "
        "λ ← [λ + η (Ĉ − d)]_+, training on reward R − λ C. The shield handles instantaneous "
        "illegal actions; the multiplier handles average-wait SLAs that cannot be judged from "
        "one tick. This is a better fit than Multi-Agent RL for a first extension because the "
        "present environment is a single junction; multi-agent corridor control would multiply "
        "|S| and is listed as future work.",
    )
    add_para(
        doc,
        "Digital-twin compatibility. The same shield can wrap a SUMO controller: the learning "
        "agent proposes a phase, the twin’s traffic-signal program rejects illegal commands, "
        "and the TD update uses the executed (possibly projected) action—exactly SARSA’s "
        "on-policy semantics. That is another reason to keep SARSA in the algorithm set even "
        "though Dyna-Q won the unconstrained ranking.",
    )

    add_heading_custom(doc, "12. Conclusion", 1)
    add_para(
        doc,
        "Learnings. A compact occupancy MDP is sufficient to expose differences among TD "
        "control algorithms. Smoothed learning curves, greedy evaluation, and a stability "
        "statistic tell different stories and must be read together. Implementing the four "
        "updates from scratch clarifies that Expected SARSA and Dyna-Q are small, principled "
        "modifications of the same loop rather than unrelated libraries.",
    )
    add_para(
        doc,
        "Most suitable approach. Dyna-Q is the most suitable tabular method for this "
        "simulator under the stated hyperparameters, with Expected SARSA as a strong "
        "model-free runner-up when planning cost or model bias is a concern.",
    )
    add_para(
        doc,
        "Future scope. (i) Safe-RL shield and Lagrangian costs; (ii) time-indexed or "
        "tile-coded state to capture demand drift; (iii) Double Q-learning to test the "
        "overestimation hypothesis; (iv) SUMO digital twin with detector noise; (v) multi-agent "
        "control of an arterial. None of these require abandoning the MDP written for CIA-3; "
        "they extend it.",
    )
    add_para(
        doc,
        "Reproducibility. Every number in Table 1 is regenerated by python run_all.py. "
        "Q-tables, episode returns, greedy traces, and PNG figures are stored beside the "
        "code. Random seeds are documented. A different machine will change wall-clock times "
        "but should reproduce the algorithm ranking within ordinary Poisson noise.",
    )
    add_para(
        doc,
        "Pedagogical outcome. Implementing Expected SARSA made the on-policy distribution "
        "explicit; implementing Dyna-Q made the difference between a real interaction and a "
        "model sample explicit. Those two distinctions are the intellectual core of Units 4 "
        "and 5 and are easy to miss if one only calls a library fit method. The traffic story "
        "is the motivation; the nested TD updates are the actual coursework object.",
    )

    add_heading_custom(doc, "13. References", 1)
    refs = [
        "[1] R. S. Sutton and A. G. Barto, Reinforcement Learning: An Introduction, 2nd ed. Cambridge, MA, USA: MIT Press, 2018.",
        "[2] F. V. Webster, “Traffic signal settings,” Road Research Technical Paper No. 39, HMSO, London, U.K., 1958.",
        "[3] M. Wiering, “Multi-agent reinforcement learning for traffic light control,” in Proc. 17th Int. Conf. Machine Learning (ICML), 2000, pp. 1151–1158.",
        "[4] L. A. Prashanth and S. Bhatnagar, “Reinforcement learning with function approximation for traffic signal control,” IEEE Trans. Intell. Transp. Syst., vol. 12, no. 2, pp. 412–421, Jun. 2011.",
        "[5] E. van der Pol and F. A. Oliehoek, “Coordinated deep reinforcement learners for traffic light control,” in Proc. NIPS Workshop on Learning, Inference and Control of Multi-Agent Systems, 2016.",
        "[6] H. Wei, G. Zheng, H. Yao, and Z. Li, “IntelliLight: A reinforcement learning approach for intelligent traffic light control,” in Proc. 24th ACM SIGKDD Conf. Knowledge Discovery and Data Mining (KDD), 2018, pp. 2496–2505.",
        "[7] C. Chen et al., “Toward a thousand lights: Decentralized deep reinforcement learning for large-scale traffic signal control,” in Proc. AAAI Conf. Artificial Intelligence, 2020, pp. 3412–3419.",
        "[8] J. García and F. Fernández, “A comprehensive survey on safe reinforcement learning,” J. Mach. Learn. Res., vol. 16, no. 42, pp. 1437–1480, 2015.",
        "[9] A. Haydari and Y. Yılmaz, “Deep reinforcement learning for intelligent transportation systems: A survey,” IEEE Trans. Intell. Transp. Syst., vol. 23, no. 1, pp. 11–32, Jan. 2022.",
        "[10] N. H. Gartner, “OPAC: A demand-responsive strategy for traffic signal control,” Transp. Res. Rec., no. 906, pp. 75–81, 1983.",
        "[11] C. J. C. H. Watkins and P. Dayan, “Q-learning,” Mach. Learn., vol. 8, pp. 279–292, 1992.",
        "[12] G. A. Rummery and M. Niranjan, “On-line Q-learning using connectionist systems,” Tech. Rep. CUED/F-INFENG/TR 166, Univ. Cambridge, 1994.",
        "[13] R. S. Sutton, “Dyna, an integrated architecture for learning, planning, and reacting,” ACM SIGART Bulletin, vol. 2, no. 4, pp. 160–163, 1991.",
        "[14] H. van Seijen, H. van Hasselt, S. Whiteson, and M. Wiering, “A theoretical and empirical analysis of Expected Sarsa,” in Proc. IEEE Symp. Adaptive Dynamic Programming and Reinforcement Learning, 2009, pp. 177–184.",
        "[15] P. Hunt, D. Robertson, R. Bretherton, and R. Winton, “SCOOT—a traffic responsive method of coordinating signals,” TRRL Laboratory Report 1014, Crowthorne, U.K., 1981.",
    ]
    for r in refs:
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Inches(-0.35)
        p.paragraph_format.left_indent = Inches(0.35)
        run = p.add_run(r)
        set_run_font(run, size=11)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    print("wrote", OUT)


if __name__ == "__main__":
    build()
