# CIA-3 Reinforcement Learning Implementations

Custom Gym-style environment for **dynamic traffic signal control** at a single four-approach intersection, plus four tabular RL algorithms implemented from scratch (NumPy only).

## Approaches

| Folder | Algorithm | One-line justification |
|---|---|---|
| Approach_1 | SARSA | On-policy TD control matching a controller that keeps mild exploration when deployed. |
| Approach_2 | Q-learning | Off-policy TD control targeting a greedy deployed signal plan while exploring in simulation. |
| Approach_3 | Expected SARSA | On-policy TD with expected next-action targets; reduces variance under stochastic arrivals. |
| Approach_4 | Dyna-Q | Q-learning plus a learned tabular model and planning; reuses traffic transition experience. |

## Run

```bash
source .venv/bin/activate   # or any env with numpy + matplotlib
cd 04_RL_Implementations
python run_all.py
```

Or train one algorithm:

```bash
python Approach_1/train_sarsa.py
python Approach_2/train_qlearning.py
python Approach_3/train_expected_sarsa.py
python Approach_4/train_dyna_q.py
python visualize_results.py
```

Each approach folder stores `rewards.npy`, `q_table.npy`, `policy.npy`, `metrics.json`, `summary.txt`, and `behavior_trace.txt`.
