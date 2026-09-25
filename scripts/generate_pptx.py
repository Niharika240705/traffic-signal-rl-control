"""12–18 slide case-study presentation with speaker notes."""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

ROOT = Path("/Users/niharikasingh/Documents/RL")
GRAPHS = ROOT / "05_Results_and_Graphs"
OUT = ROOT / "02_Presentation_PPT" / "CIA3_Component1_Case_Study_Presentation.pptx"

NAVY = RGBColor(0x1F, 0x4E, 0x79)
TEAL = RGBColor(0x2E, 0x75, 0xB6)
DARK = RGBColor(0x1A, 0x1A, 0x1A)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GOLD = RGBColor(0xC4, 0x9A, 0x3C)


def set_run(run, size=18, bold=False, color=DARK, font="Calibri"):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font


def add_bg(slide, rgb):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = rgb


def title_bar(slide, text):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.05))
    shape.fill.solid()
    shape.fill.fore_color.rgb = NAVY
    shape.line.fill.background()
    tf = shape.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    run = p.add_run()
    run.text = "  " + text
    set_run(run, size=26, bold=True, color=WHITE)


def bullets(slide, items, top=1.3, left=0.7, width=12.0, height=5.8, size=20):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.level = item[0]
        p.space_after = Pt(8)
        run = p.add_run()
        run.text = item[1]
        set_run(run, size=size - 2 * item[0], bold=(item[0] == 0 and i == 0 and False), color=DARK)


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def footer(slide, n, ntot=16):
    box = slide.shapes.add_textbox(Inches(11.6), Inches(7.15), Inches(1.5), Inches(0.3))
    p = box.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.RIGHT
    run = p.add_run()
    run.text = f"{n} / {ntot}"
    set_run(run, size=10, color=RGBColor(0x66, 0x66, 0x66))


def build():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]
    ntot = 16

    # 1 title
    s = prs.slides.add_slide(blank)
    add_bg(s, NAVY)
    box = s.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.7), Inches(2.2))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = "Adaptive Traffic Signal Control\nusing Reinforcement Learning"
    set_run(run, size=36, bold=True, color=WHITE)
    box2 = s.shapes.add_textbox(Inches(0.8), Inches(4.1), Inches(11.7), Inches(2.2))
    tf = box2.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = (
        "CIA-3  ·  Component 1 Case Study  ·  Course: Reinforcement Learning\n"
        "Team: Member 1  ·  Member 2  ·  Member 3  ·  Member 4\n"
        "September 2026"
    )
    set_run(run, size=18, color=RGBColor(0xD6, 0xE3, 0xF0))
    notes(
        s,
        "MEMBER 1 — Opening. Greet the evaluator. State the team, course, and title. "
        "Say in one sentence: we treat a traffic light as a sequential decision agent, not as a "
        "fixed timer. Mention that Component 2 uses the same case. Pause, then hand the problem over.",
    )
    footer(s, 1, ntot)

    # 2 agenda
    s = prs.slides.add_slide(blank)
    title_bar(s, "Agenda")
    bullets(
        s,
        [
            (0, "Problem: isolated intersection, keep-or-switch control"),
            (0, "Why it is sequential / real-time — and why rules are not enough"),
            (0, "MDP: state, action, reward"),
            (0, "Problem characteristics (Unit 4/5 checklist)"),
            (0, "Base algorithm: Q-learning, and the four TD variants"),
            (0, "Workflow loop + Component 2 headline result"),
            (0, "Innovation: Safe RL shielding"),
            (0, "Conclusion and what the video could not include"),
        ],
        size=22,
    )
    notes(
        s,
        "MEMBER 1. Walk the agenda quickly. Emphasise that the same MDP is used in the micro-project. "
        "Do not spend time on software here.",
    )
    footer(s, 2, ntot)

    # 3 problem
    s = prs.slides.add_slide(blank)
    title_bar(s, "A. Problem definition")
    bullets(
        s,
        [
            (0, "Domain: Transportation — one four-approach urban intersection"),
            (0, "Agent: the signal controller (cabinet logic)"),
            (0, "Decision every tick: KEEP current phase or SWITCH to the other phase"),
            (0, "Long-term objective: minimise waiting + spillback over a whole peak window"),
            (0, "Not a classification problem: today’s green changes tomorrow’s queues"),
        ],
        size=22,
    )
    notes(
        s,
        "MEMBER 1. Explain North–South versus East–West as two phases. Stress delayed cost: "
        "a greedy green can starve the cross street until overflow. Long-term objective is "
        "discounted return, not instantaneous discharge. ~90 seconds.",
    )
    footer(s, 3, ntot)

    # 4 why sequential / rules
    s = prs.slides.add_slide(blank)
    title_bar(s, "Why sequential, real-time — and why not only rules")
    bullets(
        s,
        [
            (0, "Sequential: residual queue + random arrivals = next state"),
            (0, "Real-time: an action is required every control interval"),
            (0, "Fixed-time (Webster) assumes stationary mean flows"),
            (0, "Gap-based actuation is reactive and myopic"),
            (0, "Hand-tuned thresholds do not track a mid-peak directional flip"),
            (0, "RL learns a closed-loop mapping from occupancy patterns to phase decisions"),
        ],
        size=20,
    )
    notes(
        s,
        "MEMBER 1 closing this block. Contrast Webster and actuation with value-based control. "
        "Admit we still need a conflict monitor — RL is for the split, not for safety hardware. "
        "Hand over to Member 2 for the MDP.",
    )
    footer(s, 4, ntot)

    # 5 figure intersection
    s = prs.slides.add_slide(blank)
    title_bar(s, "Environment abstraction")
    img = GRAPHS / "intersection_sketch.png"
    if img.exists():
        s.shapes.add_picture(str(img), Inches(0.6), Inches(1.3), height=Inches(5.6))
    bullets(
        s,
        [
            (0, "Gridworld-style lane cells"),
            (0, "Phase 0: NS green"),
            (0, "Phase 1: EW green"),
            (0, "Poisson arrivals (synthetic)"),
            (0, "Min-green lock = 4 steps"),
            (0, "Assumption: no real detectors"),
        ],
        top=1.4,
        left=7.3,
        width=5.5,
        height=5.5,
        size=18,
    )
    notes(
        s,
        "MEMBER 2. Point at N/S/E/W. State the explicit assumption: synthetic Poisson demand, "
        "not a named corridor. Occupancy cap of five keeps the problem tabular (|S| = 6,480).",
    )
    footer(s, 5, ntot)

    # 6 SAR
    s = prs.slides.add_slide(blank)
    title_bar(s, "B. State, action, reward")
    bullets(
        s,
        [
            (0, "State s = (qN, qS, qE, qW, phase, t_green)"),
            (1, "Queues: congestion is the primary signal"),
            (1, "Phase: discharge capability depends on who is green"),
            (1, "Timer: so the agent knows when a switch is legal"),
            (0, "Action (discrete): 0 keep, 1 switch — ignored if min-green not met"),
            (0, "Reward: R = −Σq − 8·blocked − 0.35·switched"),
            (1, "Negative: waiting, spillback, chatter"),
            (1, "Positive: returns nearer to zero (short queues, no overflow)"),
        ],
        size=20,
    )
    notes(
        s,
        "MEMBER 2. Justify each state variable in one line. Read the reward equation slowly. "
        "Mention that throughput is not double-counted: serving cars reduces future occupancy.",
    )
    footer(s, 6, ntot)

    # 7 characteristics
    s = prs.slides.add_slide(blank)
    title_bar(s, "C. RL problem characteristics")
    bullets(
        s,
        [
            (0, "Episodic — T = 120 step peak window (field would be continuing)"),
            (0, "Dynamic — arrival means drift (NS-heavy → more EW-heavy)"),
            (0, "Stochastic — Poisson arrivals + random stalls"),
            (0, "Fully observed in the simulator (field detectors → POMDP later)"),
            (0, "Discrete finite S and A  |  |S|=6480, |A|=2"),
            (0, "Simulation-based online TD  |  long-term discounted objective γ=0.95"),
        ],
        size=20,
    )
    notes(
        s,
        "MEMBER 2. This slide is the rubric checklist — say each label out loud. Note the "
        "honest gaps: episodic training versus continuing operations; fully observed sim versus "
        "noisy loops. Hand to Member 3 for algorithms.",
    )
    footer(s, 7, ntot)

    # 8 algorithm
    s = prs.slides.add_slide(blank)
    title_bar(s, "D. Base algorithm — Q-learning")
    bullets(
        s,
        [
            (0, "Why not DP?  Transition kernel P is unknown (and time-varying)"),
            (0, "Why not Monte Carlo?  120-step wait before the first update"),
            (0, "Why TD?  Bootstrap every tick — matches real-time control"),
            (0, "Why off-policy Q-learning?  Train with ε-greedy, deploy greedy"),
            (0, "Update:  Q(s,a) ← Q(s,a) + α[R + γ max_a' Q(s',a') − Q(s,a)]"),
            (0, "α=0.12,  γ=0.95,  ε: 1.0 → 0.05 over 1400 episodes"),
        ],
        size=20,
    )
    notes(
        s,
        "MEMBER 3. Derive the update in words: target is r plus discounted best next action. "
        "Stress deployed policy is greedy, so off-policy is the right default. Mention SARSA "
        "would be preferred if exploration stayed on in the cabinet.",
    )
    footer(s, 8, ntot)

    # 9 four methods
    s = prs.slides.add_slide(blank)
    title_bar(s, "Four connected TD methods (Component 2)")
    bullets(
        s,
        [
            (0, "SARSA — on-policy; target uses the action actually taken next"),
            (0, "Q-learning — off-policy; target uses max next action-value"),
            (0, "Expected SARSA — on-policy expected target; lower variance"),
            (0, "Dyna-Q — Q-learning + learned model + 8 planning updates"),
            (0, "Headline (real runs): Dyna-Q best late return and greedy eval"),
            (0, "Q-learning looked ‘fastest’ to plateau but at a weaker policy"),
        ],
        size=20,
    )
    notes(
        s,
        "MEMBER 3. One sentence each. Quote the idea that stability ≠ quality: Q-learning "
        "hit the rolling-mean test at episode 248 but Dyna-Q’s last-100 mean was better "
        "(about −811 versus −859). Do not read the full table; that lives in the report.",
    )
    footer(s, 9, ntot)

    # 10 workflow
    s = prs.slides.add_slide(blank)
    title_bar(s, "E. RL workflow")
    img = GRAPHS / "rl_workflow.png"
    if img.exists():
        s.shapes.add_picture(str(img), Inches(0.4), Inches(1.2), width=Inches(12.5))
    notes(
        s,
        "MEMBER 3. Trace the arrows: environment to state to ε-greedy action to reward and "
        "next queues, then the TD/Dyna update. Mention that a shielded Safe-RL agent would "
        "insert a filter between agent and action. Hand to Member 4.",
    )
    footer(s, 10, ntot)

    # 11 overlay result
    s = prs.slides.add_slide(blank)
    title_bar(s, "Learning curves (actual training, not mock-ups)")
    img = GRAPHS / "reward_vs_episode_overlay.png"
    if img.exists():
        s.shapes.add_picture(str(img), Inches(1.2), Inches(1.25), width=Inches(10.8))
    notes(
        s,
        "MEMBER 4. Returns are negative because reward is a cost. All four curves rise "
        "(become less negative). Dyna-Q is on top of the smoothed overlay. Variance remains "
        "because arrivals are random — that is physics, not a bug.",
    )
    footer(s, 11, ntot)

    # 12 bars
    s = prs.slides.add_slide(blank)
    title_bar(s, "Evaluation snapshot")
    img = GRAPHS / "bar_policy_quality.png"
    if img.exists():
        s.shapes.add_picture(str(img), Inches(0.4), Inches(1.25), width=Inches(6.2))
    img2 = GRAPHS / "bar_average_reward.png"
    if img2.exists():
        s.shapes.add_picture(str(img2), Inches(6.8), Inches(1.25), width=Inches(6.2))
    notes(
        s,
        "MEMBER 4. Left: greedy evaluation return. Right: last-100 training mean. Same ranking. "
        "This is the evidence slide; keep it short.",
    )
    footer(s, 12, ntot)

    # 13 innovation
    s = prs.slides.add_slide(blank)
    title_bar(s, "F. Innovation — Safe Reinforcement Learning")
    bullets(
        s,
        [
            (0, "Average return is not a municipal SLA"),
            (0, "Hard shield A_safe(s): min green, max red, spillback veto, pedestrian lock"),
            (0, "Agent maximises Q only inside the safe set (projection, not a finite penalty)"),
            (0, "Optional Lagrangian cost for long-run wait-time frequency constraints"),
            (0, "Fits this case: keep/switch chatter and directional greed are the failure modes"),
            (0, "Multi-agent corridors and digital twins come after the shield, not before"),
        ],
        size=20,
    )
    notes(
        s,
        "MEMBER 4. Distinguish shield (instant illegal actions) from Lagrange (average costs). "
        "Give one concrete example: forbid KEEP when an approach is at capacity and the other "
        "phase could serve it. Tie back to the min-green already in the simulator.",
    )
    footer(s, 13, ntot)

    # 14 assumptions
    s = prs.slides.add_slide(blank)
    title_bar(s, "Assumptions we want the examiner to see")
    bullets(
        s,
        [
            (0, "Synthetic Poisson demand — no city loop-detector log"),
            (0, "Two phases only; no protected lefts; no geometric yellow interval"),
            (0, "Perfect queue observation in sim"),
            (0, "Occupancy clipped at 5 vehicles / approach (tabular design choice)"),
            (0, "One seed per algorithm — ranking is indicative, not a 30-seed test"),
            (0, "Video of this PPT must be recorded by the four members (not generated here)"),
        ],
        size=20,
    )
    notes(
        s,
        "MEMBER 4. Academically safer to list assumptions than to hide them. Mention the "
        "self-recorded video is a team task after this slide deck is frozen.",
    )
    footer(s, 14, ntot)

    # 15 conclusion
    s = prs.slides.add_slide(blank)
    title_bar(s, "Conclusion")
    bullets(
        s,
        [
            (0, "Signal control is a real-time sequential MDP, not one-shot classification"),
            (0, "Tabular keep/switch MDP is enough to compare Unit 4/5 TD methods"),
            (0, "Base algorithm: Q-learning; strongest implemented variant: Dyna-Q"),
            (0, "Read ‘time to stability’ together with asymptotic return"),
            (0, "Safe RL shielding is the responsible extension before any field story"),
        ],
        size=22,
    )
    notes(
        s,
        "MEMBER 4. Close: problem, formulation, result, innovation. Thank the examiner. "
        "Invite questions. Members 1–3 should be ready on environment, characteristics, and updates.",
    )
    footer(s, 15, ntot)

    # 16 thank you
    s = prs.slides.add_slide(blank)
    add_bg(s, NAVY)
    box = s.shapes.add_textbox(Inches(0.8), Inches(2.4), Inches(11.7), Inches(2.5))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "Thank you\nQuestions welcome"
    set_run(run, size=40, bold=True, color=WHITE)
    box2 = s.shapes.add_textbox(Inches(0.8), Inches(5.2), Inches(11.7), Inches(1.2))
    p = box2.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "Member 1  ·  Member 2  ·  Member 3  ·  Member 4\nReplace placeholders with official names before submission."
    set_run(run, size=16, color=RGBColor(0xD6, 0xE3, 0xF0))
    notes(s, "All members: smile, stop, wait for questions. Do not ad-lib new results.")
    footer(s, 16, ntot)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(OUT)
    print("wrote", OUT)


if __name__ == "__main__":
    build()
