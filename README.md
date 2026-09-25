# CIA-3 Reinforcement Learning — Complete Deliverables

Adaptive **traffic signal control** at an isolated four-approach intersection.



## Topic

Dynamic keep/switch control of a two-phase signal. Sequential, stochastic, real-time, and tabular.

## Folder map (as required by the brief)

| Folder | Contents |
|---|---|
| `01_Case_Study_Report/` | Component 1 case study (`.docx`, `.pdf`) |
| `02_Presentation_PPT/` | `.pptx` + four-part speaker script |
| `03_Presentation_Video/` | Video presentation (hosted via [GitHub Releases](https://github.com/Niharika240705/traffic-signal-rl-control/releases/tag/v1.0.0)) |
| `04_RL_Implementations/` | Shared `environment.py` + Approach_1…4 |
| `05_Results_and_Graphs/` | Real Matplotlib PNGs |
| `06_Performance_Comparison/` | Table, metric definitions, observations |
| `07_Technical_Project_Report/` | Component 2 technical report (`.docx`, `.pdf`) |
| `08_References/` | IEEE reference list |

## Algorithms

1. SARSA — on-policy TD  
2. Q-learning — off-policy TD  
3. Expected SARSA — expected on-policy TD  
4. Dyna-Q — Q-learning + planning  

## Reproduce training

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd 04_RL_Implementations
python run_all.py
```

Regenerate reports/slides:

```bash
python scripts/generate_case_study.py
python scripts/generate_tech_report.py
python scripts/generate_pptx.py
```

## Video Presentation

The complete team video presentation (`Vid Presentation.mp4`) is available in [Release v1.0.0](https://github.com/Niharika240705/traffic-signal-rl-control/releases/tag/v1.0.0).

## Explicit assumptions

Synthetic Poisson arrivals; two phases; perfect queues; occupancy cap 5; no field detectors.
