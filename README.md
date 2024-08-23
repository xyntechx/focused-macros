# Focused Macros Greedy Best-First: Planning
Greedy best-first algorithm to find focused macros for planning for solving the Rubik's Cube

## Init Setup

### Clone repo
```
git clone --recursive git@github.com:xyntechx/focused-macros-planning.git
cd focused-macros-planning
```

### Create & activate virtual environment
```
python3.12 -m venv .venv
source .venv/bin/activate
```

### Install packages
```
python3 -m pip install --upgrade pip wheel
python3 -m pip install -r requirements.txt
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

### Learn focused macros with BFS
```
python3 macro_learning.py
```

### Run planning BFS
```
python3 planning.py
```

## Details

### Macro Learning
Saved in `/output/learned_macros.pkl`

```
576 macros generated
Max (worst) h value: 16
Min (best) h value: 6
Largest macro size: 12
Smallest macro size: 6
```

### Planning
Saved in `/output/cube_solution.pkl`
