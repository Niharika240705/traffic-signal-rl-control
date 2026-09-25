"""Component 1 case study report (10–15 pages target)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
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
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Inches


OUT = ROOT / "01_Case_Study_Report" / "CIA3_Component1_Case_Study_Report.docx"


def cover(doc):
    for _ in range(2):
        add_para(doc, "", align="center", first_line=False, space_after=0)
    add_para(
        doc,
        "CHRIST (Deemed to be University)  /  [Institution Name]",
        align="center",
        first_line=False,
        bold=True,
        size=14,
    )
    add_para(
        doc,
        "Department of Computer Science and Engineering",
        align="center",
        first_line=False,
        size=13,
    )
    add_para(doc, "", align="center", first_line=False)
    add_para(
        doc,
        "CIA-3  |  Component 1: Case Study on a Real-Time RL Application",
        align="center",
        first_line=False,
        bold=True,
        size=13,
    )
    add_para(doc, "Course: Reinforcement Learning", align="center", first_line=False)
    add_para(doc, "", align="center", first_line=False)
    add_para(
        doc,
        "Adaptive Traffic Signal Control at an Isolated Urban Intersection\n"
        "using Tabular Temporal-Difference Reinforcement Learning",
        align="center",
        first_line=False,
        bold=True,
        size=16,
    )
    add_para(doc, "", align="center", first_line=False)
    add_para(doc, "Team Members", align="center", first_line=False, bold=True)
    for m in ["Member 1", "Member 2", "Member 3", "Member 4"]:
        add_para(doc, m, align="center", first_line=False, space_after=2)
    add_para(doc, "", align="center", first_line=False)
    add_para(doc, "September 2026", align="center", first_line=False)
    doc.add_page_break()


def build():
    doc = setup_doc()
    cover(doc)

    add_heading_custom(doc, "Abstract", 1)
    add_para(
        doc,
        "This case study formulates dynamic traffic signal control at a single four-approach "
        "urban intersection as a real-time sequential decision-making problem. Fixed-time and "
        "actuated controllers remain the operational default in many cities, yet they react "
        "poorly to stochastic arrivals, directional peak flips, and the delayed cost of a "
        "bad green allocation. We model the intersection as a finite Markov Decision Process "
        "(MDP) whose state comprises discretised queue occupancies, the active phase, and a "
        "minimum-green timer; whose actions are keep-or-switch phase decisions; and whose "
        "reward penalises waiting, spillback, and needless switching. The recommended base "
        "algorithm is off-policy Q-learning, trained in a custom Gym-style simulator because "
        "live detector traces and a hardware-in-the-loop controller are unavailable. The same "
        "MDP later supports four related tabular methods (SARSA, Q-learning, Expected SARSA, "
        "and Dyna-Q) in Component 2. The proposed innovation is Safe Reinforcement Learning "
        "with an action shield that hard-enforces pedestrian clearance, maximum red time, and "
        "spillback limits that a purely reward-shaped agent can still violate.",
    )

    add_heading_custom(doc, "Topic selection and justification", 1)
    add_para(
        doc,
        "Final choice. Dynamic (adaptive) traffic signal control at an isolated four-leg "
        "intersection in the Transportation domain. We considered adaptive e-commerce pricing "
        "as an alternative, but traffic control has a clearer physical sequential structure, "
        "hard safety constraints, and a natural Gridworld-style lane abstraction that can be "
        "simulated without proprietary market data.",
    )
    add_para(
        doc,
        "A signal controller must repeatedly decide which movement is served now, knowing that "
        "today’s green both discharges the current queue and delays the opposing movement. "
        "Arrivals are stochastic, demand is non-stationary within a peak period, and the cost "
        "of a decision is delayed: a slightly early switch may look harmless at time t and "
        "produce spillback two minutes later. These properties make the problem a canonical "
        "episodic, stochastic MDP rather than a one-shot classification task. A 1-D occupancy "
        "queue per approach is a legitimate Gridworld/Maze abstraction of detector cells on "
        "each lane. Four TD-family algorithms can be compared meaningfully because they share "
        "the same state–action encoding while differing in on-policy versus off-policy targets "
        "and in whether a learned model is used for planning.",
    )
    add_para(
        doc,
        "Assumption (explicit). All numerical experiments use synthetic Poisson arrivals with "
        "a mild within-episode directional flip. They are not calibrated to a named city "
        "corridor. The formulation, however, is the same MDP a calibrated digital twin would "
        "present to a tabular or deep agent.",
    )

    add_heading_custom(doc, "Rejected alternatives (why this topic won)", 1)
    add_para(
        doc,
        "Adaptive e-commerce pricing is sequential and has a natural reward (revenue minus "
        "disutility), but a convincing simulator needs a demand curve, competitor responses, "
        "and inventory, all of which we would have fabricated even more aggressively than "
        "Poisson traffic. Hospital bed-to-ward assignment is sequential but ethically "
        "awkward to treat as a Gridworld and is closer to a stochastic assignment problem "
        "than to a keep/switch controller. A warehouse robot in a maze is already a "
        "textbook Gridworld and would look less like a real-time industrial case. Energy "
        "storage arbitrage is an excellent continuing MDP, yet the action is often continuous "
        "power, which fights the discrete algorithm list. Traffic control remains the best "
        "fit: public literature, discrete phases, delayed congestion cost, and a lane-cell "
        "abstraction that is honestly Gridworld-like without pretending to be Pac-Man.",
    )
    add_para(
        doc,
        "Team-size note. Four members map cleanly onto (i) problem and rules critique, "
        "(ii) MDP and characteristics, (iii) algorithm and workflow, (iv) innovation, "
        "results, and close — which is how the speaker script is split.",
    )

    add_heading_custom(doc, "A. Problem Definition", 1)
    add_heading_custom(doc, "A.1 Real-world problem", 2)
    add_para(
        doc,
        "Urban intersections are bottlenecks of surface transport. When a signal plan is "
        "poorly matched to demand, queues occupy upstream links, buses miss headways, and "
        "spillback can block neighbouring junctions. Traffic engineering practice still "
        "relies heavily on Webster-style fixed-time plans, time-of-day schedules, and "
        "gap-based actuated control. These methods estimate a cycle and splits from average "
        "volumes. They do not reason about the long-run discounted cost of serving North–South "
        "now versus holding green for a growing East–West platoon, nor do they automatically "
        "retune when the peak direction reverses inside the same hour.",
    )
    add_para(
        doc,
        "The real-world decision problem studied here is: at each short control interval "
        "(a one-second to few-second tick in the field; one discrete step in our simulator), "
        "should the controller keep the current green phase or switch to the opposing phase, "
        "subject to a minimum green that protects pedestrians and start-up lost time? The "
        "objective is not to maximise instantaneous discharge, but to minimise waiting, "
        "overflow, and excessive phase chopping over an entire peak period.",
    )

    add_heading_custom(doc, "A.2 Why the problem is sequential and real-time", 2)
    add_para(
        doc,
        "Sequential structure. The occupancy that will be observed at t+1 depends on the "
        "phase chosen at t, on residual queues, and on random arrivals. Credit for a switch "
        "is therefore delayed. A myopic policy that always serves the currently longest "
        "approach can starve the opposing movement until a spillback event occurs. Sequential "
        "decision-making is required so that the agent can trade a short local wait against "
        "a larger future cost.",
    )
    add_para(
        doc,
        "Real-time structure. Vehicles do not pause while an optimiser solves a mixed-integer "
        "programme. The controller must emit an action every tick from the latest detector "
        "(or simulated) state. Offline plans can be used as a prior, but the closed-loop "
        "policy has to run online. In this coursework we train in simulation and would deploy "
        "the greedy policy as a real-time lookup over discrete queue bins.",
    )

    add_heading_custom(doc, "A.3 Decisions to be made", 2)
    add_bullets(
        doc,
        [
            "Keep the current phase or request a switch to the complementary two-way phase.",
            "Respect a minimum green (and, in the Safe-RL extension, a maximum red and pedestrian clearance).",
            "Implicitly allocate green time over the episode by the sequence of keep/switch decisions rather than by a precomputed split.",
        ],
    )
    add_para(
        doc,
        "We deliberately use a binary keep/switch action instead of a continuous green-time "
        "output. Discrete actions keep the problem inside the tabular methods of Units 4–5, "
        "match the suggested algorithm list (SARSA, Q-learning, Dyna-Q, …), and still express "
        "flexible splits: a long green is simply a streak of keep actions after min-green is met.",
    )

    add_heading_custom(doc, "A.4 The agent", 2)
    add_para(
        doc,
        "The agent is a signal controller for one isolated intersection. It observes a compact "
        "state (queues, phase, timer), selects keep or switch, and receives a scalar reward. "
        "It does not control vehicle routing or speed; those are part of the environment. In "
        "an operational reading, the agent sits in the cabinet logic above the conflict "
        "monitor: the conflict monitor (or our shield) remains the last safety authority.",
    )

    add_heading_custom(doc, "A.5 Long-term objective", 2)
    add_para(
        doc,
        "Let an episode be one simulated peak window of T discrete steps. The long-term "
        "objective is to maximise the expected discounted return G = Σ_{k=0}^{T-1} γ^k R_{t+k+1}, "
        "which in our reward design is equivalent to minimising a discounted mix of total "
        "waiting, spillback events, and switch churn. Discounting (γ = 0.95 in the experiments) "
        "encodes that congestion a few seconds ahead still matters, while an unbounded horizon "
        "inside a finite peak is unnecessary. Short-term greedy discharge is therefore not "
        "the objective: a policy may legally hold a slightly shorter queue if doing so prevents "
        "a later overflow on the cross street.",
    )

    add_heading_custom(doc, "A.6 Why rule-based systems are insufficient", 2)
    add_para(
        doc,
        "Fixed-time control assumes stationary mean flows and a known saturation flow. It "
        "cannot reallocate green when a bus bunch, a downstream blockage, or a special event "
        "changes the residual queue in real time. Gap-based actuation extends green while "
        "vehicles are present, which is reactive but myopic: it has no discounted value "
        "function for the opposing queue and can over-extend green on a greedy approach. "
        "Threshold rules of the form “switch if Q_EW − Q_NS > δ” require hand-tuned δ, ignore "
        "the min-green timer as a state variable, and do not generalise when arrival rates "
        "flip mid-episode. Optimisation-based model predictive control can in principle look "
        "ahead, but it needs an accurate predictive model at every tick and is computationally "
        "heavier than a learned tabular policy. Reinforcement learning is attractive precisely "
        "because it can learn a closed-loop mapping from occupancy patterns to phase decisions "
        "by interacting with a simulator, without committing to a single analytic arrival model "
        "at deployment time.",
    )
    add_para(
        doc,
        "This is not a claim that RL should replace traffic engineering. Detector failure, "
        "legal timing constraints, and public accountability still require a rule layer. The "
        "case for RL is that the adaptive component—the split between competing movements—"
        "is a sequential stochastic control problem for which value-based methods are well "
        "studied.",
    )

    add_heading_custom(doc, "B. RL Environment Formulation", 1)
    add_heading_custom(doc, "B.1 Environment", 2)
    add_para(
        doc,
        "The environment is a custom Gym-style simulator (TrafficSignalEnv) of an isolated "
        "two-phase intersection. North and South share phase 0; East and West share phase 1. "
        "Each approach is a one-dimensional occupancy stack with at most MAX_QUEUE discrete "
        "cells. This is a Gridworld/Maze-style abstraction: each cell is analogous to a "
        "stop-bar or advance detector bin. Vehicles arrive according to independent Poisson "
        "processes whose means differ by direction and drift slowly through the episode "
        "(North–South heavier early, East–West heavier later). A green approach discharges "
        "one vehicle per step unless a stall occurs with small probability, representing "
        "start-up lost time, a slow truck, or a pedestrian in the crosswalk. Arrivals that "
        "find a full approach are blocked (spillback / lost demand). Episodes last T = 120 "
        "steps. The environment is stochastic, discrete-time, and fully observed by construction.",
    )
    if (GRAPHS / "intersection_sketch.png").exists():
        add_picture_centered(doc, GRAPHS / "intersection_sketch.png", width=4.4)
        add_caption(doc, "Figure 1. Four-approach intersection abstraction used in the case study.")

    add_heading_custom(doc, "B.2 Agent", 2)
    add_para(
        doc,
        "The learning agent maintains an action-value table Q(s, a) ∈ ℝ^{|S|×2}. Behaviour "
        "during training is ε-greedy with linear decay of ε. Evaluation uses a greedy policy "
        "π(s) = argmax_a Q(s, a). The agent does not observe future arrivals; it only sees "
        "the current occupancy, phase, and timer.",
    )

    add_heading_custom(doc, "B.3 State variables (with justification)", 2)
    add_para(
        doc,
        "The state is the tuple (q_N, q_S, q_E, q_W, φ, t_green), encoded as a single integer "
        "for tabular methods. Each component is justified as follows.",
    )
    add_table(
        doc,
        ["Variable", "Domain", "Justification"],
        [
            [
                "q_N, q_S, q_E, q_W",
                "0 … 5",
                "Occupancy is the primary congestion signal; five bins keep |S| tabular while still distinguishing empty, moderate, and saturated approaches.",
            ],
            [
                "φ (phase)",
                "{0, 1}",
                "Discharge capability depends on who currently has green; the same queue vector is a different control problem under NS versus EW green.",
            ],
            [
                "t_green",
                "0 … MIN_GREEN",
                "Switching is illegal until min-green is met. Including the timer lets the agent learn when a switch action is actually effective rather than a no-op.",
            ],
        ],
    )
    add_para(
        doc,
        "With six occupancy levels, two phases, and five timer levels, |S| = 6^4 × 2 × 5 = 6,480 "
        "states and |A| = 2, which is tractable for NumPy Q-tables. Variables deliberately omitted "
        "(exact vehicle speeds, turning proportions, downstream occupancy) would push the problem "
        "into function approximation; they are listed as limitations rather than hidden in the model.",
    )

    add_heading_custom(doc, "B.4 Action space", 2)
    add_para(
        doc,
        "The action space is discrete: a = 0 keep the current phase; a = 1 request a switch. "
        "Constraint: if t_green < MIN_GREEN, the environment ignores a switch and treats it as "
        "keep. This is an environment-level safety constraint analogous to a conflict-monitor "
        "lock. There is no continuous green-time action in Component 1/2; continuous control "
        "would require policy-gradient methods outside the mandated tabular list. Illegal "
        "actions are therefore not crashing the simulator; they are simply ineffective, which "
        "the TD error will eventually reflect.",
    )

    add_heading_custom(doc, "B.5 Reward function", 2)
    add_para(
        doc,
        "At every step the environment returns",
    )
    add_para(
        doc,
        "R = − Σ_i q_i  −  8 · n_blocked  −  0.35 · 1_{switched}.",
        align="center",
        first_line=False,
        italic=True,
    )
    add_para(
        doc,
        "Negative outcomes. Waiting is always costly (the sum of occupancies). Spillback is "
        "additionally costly so that saturating an approach is worse than spreading delay. A "
        "small switch cost discourages chatter that would be unrealistic for a field signal "
        "(yellow + all-red lost time is not modelled geometrically, so this term is a proxy).",
    )
    add_para(
        doc,
        "Positive outcomes. Because the problem is a cost-minimisation task, “positive” "
        "performance appears as returns closer to zero: short queues, no blocked arrivals, "
        "and only necessary switches. Serving vehicles reduces future occupancy and therefore "
        "improves subsequent rewards; there is no separate bonus for throughput, which would "
        "double-count discharge already reflected in the queue term. Assumption (explicit): "
        "we do not encode passenger occupancy, bus priority, or emissions. Those would change "
        "the scalarisation of the reward and are left to the Safe-RL / multi-objective extension.",
    )

    add_heading_custom(doc, "C. RL Problem Characteristics", 1)
    add_table(
        doc,
        ["Characteristic", "Classification for this case study", "Rationale"],
        [
            [
                "Episodic / continuing",
                "Episodic (finite peak window)",
                "Each training episode is a T-step peak period with a terminal time. Operation in the field is closer to continuing; we discuss that gap in limitations.",
            ],
            [
                "Static / dynamic",
                "Dynamic",
                "Arrival means drift within the episode (directional flip). The transition kernel therefore depends on time, not only on (s, a).",
            ],
            [
                "Deterministic / stochastic",
                "Stochastic",
                "Poisson arrivals and random stalls. The same (s, a) can yield different (s′, r).",
            ],
            [
                "Observability",
                "Fully observed in the simulator",
                "The agent sees exact discrete queues. Field detectors would make the problem POMDP; we treat that as a future extension, not as hidden state here.",
            ],
            [
                "State space",
                "Discrete, finite, |S|=6480",
                "Tabular encoding of queues, phase, timer.",
            ],
            [
                "Action space",
                "Discrete, |A|=2, constrained",
                "Keep/switch with min-green lock.",
            ],
            [
                "Sequential?",
                "Yes",
                "Tomorrow’s queue is today’s residual plus arrivals minus discharge.",
            ],
            [
                "Learning regime",
                "Simulation-based, online in-sim",
                "No historical (s,a,r,s′) logs from the field. Updates are incremental after each simulated step (not batch offline RL).",
            ],
            [
                "Horizon / objective",
                "Long-term (discounted episode return)",
                "γ = 0.95; reward shaping still uses instantaneous waiting so short-term cost is visible, but Q captures delayed spillback.",
            ],
        ],
    )
    add_para(
        doc,
        "Sequential decision-making rationale (expanded). If the controller only classified "
        "the current snapshot into “NS busy / EW busy”, it would ignore the timer, the "
        "asymmetric cost of switching too late, and the fact that serving a movement changes "
        "the snapshot. RL is used because the data-generating process is an MDP (approximately) "
        "and the decision is repeated under uncertainty.",
    )
    add_para(
        doc,
        "Online versus offline versus simulation-based. Component 2 trains online inside the "
        "simulator: each real interaction updates Q. Dyna-Q additionally performs simulated "
        "(planning) updates from a learned model, which is still simulation-based rather than "
        "offline RL from a frozen industrial log. True offline RL would be relevant if a city "
        "released historical controller traces; we do not have that dataset.",
    )

    add_heading_custom(doc, "Formal MDP tuple", 1)
    add_para(
        doc,
        "Collecting the pieces, the coursework MDP is M = (S, A, P, R, γ, ρ0, T) where S is "
        "the finite occupancy–phase–timer set defined above; A = {keep, switch}; P(s′ | s, a) "
        "is induced by the (unknown to the agent) Poisson-and-stall simulator and by the "
        "min-green lock; R is the bounded cost-shaped reward; γ = 0.95; ρ0 randomises a small "
        "residual queue and a random initial phase so that the agent does not only see empty "
        "intersections; and T = 120 is the absorbing clock. The Bellman optimality equation "
        "for the action-value is Q*(s, a) = E[R + γ max_a′ Q*(S′, a′) | s, a], with the "
        "expectation over P. Q-learning is a sampled, asynchronous Robbins–Monro scheme for "
        "that equation. Because P is both stochastic and slowly non-stationary in t, there is "
        "no claim that the finite-horizon Q* of a stationary kernel is attained; the practical "
        "claim is that TD still produces a useful policy for this family of peak windows.",
    )
    add_para(
        doc,
        "Credit assignment. A spillback at step t = 80 may be caused by a keep action at "
        "t = 50 that looked locally efficient. Monte Carlo would assign the entire episode "
        "return to every action, mixing many irrelevant decisions. One-step TD assigns blame "
        "locally through the bootstrap, which is the right inductive bias when congestion "
        "propagates on a short time scale (tens of steps), not only at the episode end. "
        "n-step TD and Dyna planning sit between those extremes; we implement the Dyna end "
        "of that spectrum in Component 2 rather than n-step λ-returns, to keep four methods "
        "conceptually nested: SARSA and Expected SARSA share a policy and differ in the target; "
        "Q-learning and Dyna-Q share a target and differ by an extra model.",
    )

    add_heading_custom(doc, "D. Selection of RL Algorithm", 1)
    add_para(
        doc,
        "Recommended base algorithm: Q-learning (off-policy one-step TD control).",
    )
    add_para(
        doc,
        "Why Q-learning fits. First, the MDP is finite and discrete, so dynamic programming "
        "would be possible if P(s′, r | s, a) were known. It is not: arrivals are stochastic "
        "and time-varying, and we prefer to learn from sampled interaction. Monte Carlo "
        "control would wait until the end of a 120-step episode before any update, which is "
        "slow credit assignment when a harmful switch occurs at step 10. One-step TD methods "
        "bootstrap from Q(s′, ·) and update every tick, matching the real-time loop. Second, "
        "the intended deployed policy is greedy (a cabinet should not randomly switch phases "
        "at ε = 0.1). Q-learning learns exactly that greedy action-value while behaviour "
        "remains ε-greedy in simulation—the textbook off-policy setting. Third, Q-learning is "
        "the parent of Expected SARSA (on-policy expected targets) and of Dyna-Q (Q-learning "
        "plus planning), so it is the natural hub of the four-algorithm micro-project.",
    )
    add_para(
        doc,
        "Why not DP, MC, or Actor–Critic as the base. DP needs the model; we would still have "
        "to estimate it, at which point Dyna-Q is the more honest algorithm. Monte Carlo is a "
        "valid comparison point but is not selected as the base because of high variance under "
        "Poisson noise. Actor–Critic and deep RL are reserved for larger occupancy encodings; "
        "they are not required to demonstrate Units 4–5 on this tabular MDP. SARSA remains "
        "important: if a city insisted on keeping exploratory probes at deployment, SARSA "
        "would be the safer on-policy choice. We still implement it in Component 2.",
    )
    add_para(
        doc,
        "Hyperparameters chosen for the case (and used in the micro-project): learning rate "
        "α = 0.12, discount γ = 0.95, ε decaying linearly from 1.0 to 0.05 over 1,400 episodes. "
        "These values favour continued learning on a stochastic target without freezing "
        "exploration too early. They are engineering choices, not theoretically optimal stepsizes.",
    )

    add_heading_custom(doc, "E. RL Workflow", 1)
    add_para(
        doc,
        "The closed loop, specialised to this intersection, is as follows.",
    )
    add_para(
        doc,
        "1. Environment. Occupancies, phase, and the min-green timer constitute the world. "
        "Poisson arrivals and random stalls are sampled by the simulator (stand-ins for "
        "unobserved demand and friction).",
    )
    add_para(
        doc,
        "2. State. The environment encodes (q_N, q_S, q_E, q_W, φ, t_green) as integer S_t "
        "and presents it to the agent. In a field system this encoding would be produced by "
        "binning loop-detector occupancies.",
    )
    add_para(
        doc,
        "3. Agent. With probability ε the agent selects a random keep/switch action; otherwise "
        "it selects argmax_a Q(S_t, a). Tie-breaking is uniform among maximisers so that "
        "symmetric queues do not lock onto action 0 by array-index bias.",
    )
    add_para(
        doc,
        "4. Action. The chosen bit is applied. If a switch is requested too early, the "
        "environment leaves φ unchanged and increments t_green. Otherwise a switch flips φ "
        "and resets the timer.",
    )
    add_para(
        doc,
        "5. Reward. After discharge and arrivals, the scalar R_{t+1} is computed from waiting, "
        "blocked vehicles, and whether a legal switch occurred. The agent does not see the "
        "decomposition at learning time—only the scalar—so it must discover that spillback is "
        "worse than ordinary delay.",
    )
    add_para(
        doc,
        "6. Next state. The new occupancy vector and timer become S_{t+1}. If t = T the "
        "episode terminates and G is recorded for the learning curve.",
    )
    add_para(
        doc,
        "7. Learning. Q-learning writes Q(S_t, A_t) ← Q(S_t, A_t) + α [R_{t+1} + γ max_a Q(S_{t+1}, a) − Q(S_t, A_t)] "
        "(with the bootstrap term zero at termination). SARSA uses Q(S_{t+1}, A_{t+1}) instead of "
        "the max; Expected SARSA uses Σ_a π(a|S_{t+1}) Q(S_{t+1}, a); Dyna-Q adds planning "
        "updates from an empirical model of experienced transitions. Policy improvement is "
        "greedy in Q after each update (implicit in ε-greedy).",
    )
    if (GRAPHS / "rl_workflow.png").exists():
        add_picture_centered(doc, GRAPHS / "rl_workflow.png", width=6.2)
        add_caption(doc, "Figure 2. Environment–state–agent–action–reward–next-state–learning loop.")

    add_heading_custom(doc, "F. Innovation Component — Safe Reinforcement Learning", 1)
    add_para(
        doc,
        "Proposed extension: Safe RL with a hard action shield and constrained returns, not "
        "reward shaping alone. Traffic signals are safety-critical. A learned policy that "
        "shortens pedestrian clearance, holds a movement beyond a legally implied maximum red, "
        "or ignores a queue that is about to spill into an upstream intersection is unacceptable "
        "even if its average return looks good. Our current simulator already implements one "
        "hard rule (minimum green). The innovation is to treat safety as a first-class layer.",
    )
    add_para(
        doc,
        "Mechanism. A shield filters the agent’s action before it reaches the environment "
        "(or the cabinet). Let A_safe(s) be the subset of {keep, switch} that satisfies: "
        "(i) min green and yellow/all-red if we modelled them; (ii) maximum red for each "
        "approach so that a starved movement is forced green; (iii) a spillback veto that "
        "forbids keep when an approach is at MAX_QUEUE and the opposing phase could serve it; "
        "(iv) a pedestrian call lock when a walk interval is active. The agent maximises Q "
        "only inside A_safe(s). If the unconstrained greedy action is unsafe, the shield "
        "projects onto the safe set. This is more reliable than adding a large negative reward "
        "for violations, because a finite penalty can still be offset by throughput gains.",
    )
    add_para(
        doc,
        "Constrained MDP view. One may also track an auxiliary cost C_t (for example, 1 if "
        "any approach waited more than τ_max steps) and require J_C(π) ≤ d. Lagrangian or "
        "PID-Lagrangian Safe RL would adapt a multiplier λ so that the agent maximises "
        "E[R] − λ (E[C] − d). In coursework terms, this remains tabular: we can store Q_R and "
        "Q_C. The shield handles hard instantaneous constraints; the Lagrangian handles "
        "long-run frequency constraints that cannot be judged from a single state.",
    )
    add_para(
        doc,
        "Why this enhances this case study specifically. The keep/switch MDP already tempts "
        "the agent to chatter or to over-serve the currently cheaper direction after the "
        "within-episode demand flip. Component 2 results (Dyna-Q best on mean return, still "
        "with substantial return variance) show that average waiting can improve while "
        "individual episodes remain congested. A shield would convert “usually good” into "
        "“never illegal”, which is the actual municipal requirement. Digital twins and "
        "multi-agent corridor control are compatible later steps; safety is the prerequisite "
        "for either.",
    )

    add_heading_custom(doc, "Mapping onto Units 4 and 5", 1)
    add_para(
        doc,
        "Unit 4 (Monte Carlo and TD foundations) is represented by the contrast we draw "
        "between waiting for G and bootstrapping every tick, and by the on-policy versus "
        "off-policy split (SARSA versus Q-learning). Unit 5 (expected targets and planning) "
        "is represented by Expected SARSA and Dyna-Q. We did not implement MCTS because a "
        "two-action, 6,480-state signal MDP does not need tree search at decision time; the "
        "value is already stored in Q. We did not implement Prioritized Sweeping although it "
        "is a close cousin of Dyna-Q; eight uniform planning samples already show the planning "
        "effect, and priority queues would obscure the pedagogical nested structure. Double "
        "Q-learning is listed as future work to test overestimation, which is our working "
        "hypothesis for Q-learning’s weaker plateau.",
    )
    add_para(
        doc,
        "What a deployed stack would add without changing the MDP idea. A mid-block detector "
        "would replace q_i with a filtered occupancy; a yellow plus all-red interval would "
        "extend the timer; a pedestrian button would add a binary bit to s. Each addition "
        "grows |S| multiplicatively, which is why the literature moved to deep Q-networks. "
        "For CIA-3 the correct pedagogical move is to keep the table visible so that the four "
        "updates can be read in a few lines of Python.",
    )

    add_heading_custom(doc, "Preview of Component 2 (same case study)", 1)
    add_para(
        doc,
        "The micro-project trains SARSA, Q-learning, Expected SARSA and Dyna-Q for 1,400 "
        "episodes on this exact environment. Learning is visible: first-50-episode means are "
        "near −930 to −970, last-100 means near −811 to −859. Dyna-Q is best on late return "
        "and on greedy evaluation; Q-learning meets a rolling-mean stability test earliest "
        "but at a worse plateau. Those results belong in Component 2, but they already "
        "support the Component 1 claim that off-policy one-step TD is a sensible base family "
        "and that planning is a high-value extension when transitions repeat.",
    )
    if (GRAPHS / "reward_vs_episode_overlay.png").exists():
        add_picture_centered(doc, GRAPHS / "reward_vs_episode_overlay.png", width=5.9)
        add_caption(doc, "Figure 3. Component 2 preview: smoothed episode return for the four TD methods.")

    add_heading_custom(doc, "Worked one-step example (for the presentation)", 1)
    add_para(
        doc,
        "Suppose at time t the occupancy is (3, 2, 5, 4), the phase is NS-green (φ = 0), and "
        "t_green = 4, so a switch is legal. Total waiting is 14. Action keep will discharge "
        "N and S (in expectation) while E and W sit at or near capacity, so the blocked-arrival "
        "term is likely to fire on East. Action switch forfeits 0.35 switch cost and begins "
        "serving the saturated East–West pair. A myopic rule that only looks at the current "
        "sum may keep NS green because N+S = 5 is not yet hopeless; the TD target, however, "
        "bootstraps from Q(s′, ·) in which s′ will often contain blocked=1 if we keep. This "
        "is exactly the sequential rationale: the value of switch is the avoided future "
        "spillback, not the instantaneous discharge. During early training Q is near zero, so "
        "the agent explores both actions; after many such saturations, Q(s, switch) becomes "
        "less negative than Q(s, keep). Dyna-Q can replay this (s, switch) pair during planning "
        "instead of waiting to see five-on-East again.",
    )
    add_para(
        doc,
        "If instead t_green = 1, the same switch action is a no-op. The next state keeps φ = 0 "
        "and increments the timer. Without t_green in the state, the agent would mix legal and "
        "illegal switch samples into one Q(s, switch) estimate and appear ‘unable to learn "
        "switching’. Including the timer is therefore not an implementation convenience; it is "
        "part of making the MDP Markov for the constrained action.",
    )

    add_heading_custom(doc, "Assumptions, limitations, and link to Component 2", 1)
    add_para(
        doc,
        "Assumptions. Synthetic Poisson demand; two phases only (no protected lefts); no "
        "yellow interval geometry; perfect queue observation; isolated junction (no downstream "
        "blocking except via the spillback penalty); tabular occupancy cap of five vehicles "
        "per approach. Limitations. Results will not transfer to a named corridor without "
        "recalibration; |S| will explode if turning movements and multiple lanes are added, "
        "at which point Deep RL becomes the natural continuation of this case. Component 2 "
        "implements SARSA, Q-learning, Expected SARSA, and Dyna-Q on the identical environment, "
        "compares them on eight metrics, and reports Dyna-Q as the strongest mean performer "
        "under the stated hyperparameters.",
    )

    add_heading_custom(doc, "Operational reading (how this would sit in a cabinet)", 1)
    add_para(
        doc,
        "In an operations story, detectors (or a digital twin) emit occupancies every second. "
        "A preprocessor bins them into {0,…,5}, reads the ring-and-barrier phase, and reads "
        "how long the current green has been active. The Q-table — a 6,480 × 2 array, a few "
        "hundred kilobytes — is a lookup. The shield then accepts or rejects the switch bit. "
        "Only after that does the conflict monitor see a phase request. Training never happens "
        "on the live cabinet in this design; it happens in the simulator (or twin) with the "
        "same binning. That is why we classified the work as simulation-based rather than "
        "online field learning. Online field learning would raise exploration risk that Safe "
        "RL is meant to forbid.",
    )
    add_para(
        doc,
        "Failure modes we want the team to be able to discuss in viva. (1) Detector bias: if "
        "East is systematically under-counted, the policy will starve East. (2) Demand regime "
        "unseen in training (stadium outflow) — tabular Q cannot extrapolate, which is an "
        "argument for Deep RL later. (3) Downstream blockage not in the state — the agent "
        "will dump cars onto a jammed link; a corridor multi-agent extension is the remedy. "
        "(4) Reward hacking: if switch cost is too large, the agent never switches; if "
        "spillback penalty is too large, it chatters. We chose 0.35 and 8.0 by inspection so "
        "that both terms are visible but waiting remains the main signal. Those numbers are "
        "assumptions, not calibrated economic costs.",
    )

    add_heading_custom(doc, "Conclusion", 1)
    add_para(
        doc,
        "Adaptive signal control is a genuine real-time sequential problem: today’s phase "
        "decision reshapes tomorrow’s queues under stochastic demand. We formulated an "
        "isolated intersection as a compact discrete MDP, argued that rule-based splits are "
        "myopic, selected Q-learning as the base off-policy TD method, described the full "
        "interaction loop, and proposed Safe RL with shielding as the innovation required "
        "before field consideration. The same MDP is the micro-project environment.",
    )

    add_heading_custom(doc, "References (IEEE)", 1)
    refs = [
        "[1] R. S. Sutton and A. G. Barto, Reinforcement Learning: An Introduction, 2nd ed. Cambridge, MA, USA: MIT Press, 2018.",
        "[2] F. V. Webster, “Traffic signal settings,” Road Research Technical Paper No. 39, Her Majesty’s Stationery Office, London, U.K., 1958.",
        "[3] M. Wiering, “Multi-agent reinforcement learning for traffic light control,” in Proc. ICML, 2000, pp. 1151–1158.",
        "[4] L. A. Prashanth and S. Bhatnagar, “Reinforcement learning with function approximation for traffic signal control,” IEEE Trans. Intell. Transp. Syst., vol. 12, no. 2, pp. 412–421, Jun. 2011.",
        "[5] E. van der Pol and F. A. Oliehoek, “Coordinated deep reinforcement learners for traffic light control,” in NIPS Workshop on Learning, Inference and Control of Multi-Agent Systems, 2016.",
        "[6] H. Wei, G. Zheng, H. Yao, and Z. Li, “IntelliLight: A reinforcement learning approach for intelligent traffic light control,” in Proc. KDD, 2018, pp. 2496–2505.",
        "[7] C. Chen et al., “Toward a thousand lights: Decentralized deep reinforcement learning for large-scale traffic signal control,” in Proc. AAAI, 2020, pp. 3412–3419.",
        "[8] J. García and F. Fernández, “A comprehensive survey on safe reinforcement learning,” J. Mach. Learn. Res., vol. 16, pp. 1437–1480, 2015.",
        "[9] A. Haydari and Y. Yılmaz, “Deep reinforcement learning for intelligent transportation systems: A survey,” IEEE Trans. Intell. Transp. Syst., vol. 23, no. 1, pp. 11–32, Jan. 2022.",
        "[10] N. H. Gartner, “OPAC: A demand-responsive strategy for traffic signal control,” Transp. Res. Rec., no. 906, pp. 75–81, 1983.",
    ]
    for r in refs:
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Inches(-0.3)
        p.paragraph_format.left_indent = Inches(0.3)
        p.paragraph_format.line_spacing_rule = 1
        run = p.add_run(r)
        set_run_font(run, size=11)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    print("wrote", OUT)


if __name__ == "__main__":
    build()
