# Focused Macros
Learn focused macros (action abstractions) for efficient black-box planning

## Init Setup

```
git clone --recursive git@github.com:xyntechx/focused-macros.git
cd focused-macros
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip wheel
pip install -r requirements.txt
```

## Running

### Activate virtual environment
```
source .venv/bin/activate
```

### Update submodules
```
git submodule update --recursive
```

### Learn focused macros
```
python3 macro_learning.py
```

### Run planning
```
python3 planning.py
```

### Visualize focused macros usage
```
python3 visualize.py
```

### Solve cube with a saved plan
```
python3 solve.py
```

## Results

### Macro Learning
The learned focused macros which enable the shortest planning times are saved in `output/n10_learned_macros.pkl`. Here are the specs:

```
Max Fringe Size: N_m * 10
Learning Time: 06:38
# of Macros Generated: 576
Best Net Effect (h) Heuristic: 6
Worst Net Effect (h) Heuristic: 16
Shortest Macro Length (g): 6
Longest Macro Length (g): 16
```

List of learned focused macros `.pkl` files in `output`:
- `n10_learned_macros.pkl`: learned through greedy BFS with a fringe of max size `N_m * 10`
- `inf_learned_macros.pkl`: learned through greedy BFS with an unlimited fringe

### Planning
Plans are saved in `output/plans`.

Data from planning is saved in `output/data`. Each `.pkl` file is a pandas df storing the effect size and length of each focused macro (or primitive action) used at each timestep of the plan.

Graphs of effect size against timestep and macro length against timestep are saved in `output/plots`.

For each of these folders, its subfolders correspond to the max fringe size used for macro learning (e.g. `n10` means the focused macros used were learned through greedy BFS with a fringe of max size `N_m * 10`).
