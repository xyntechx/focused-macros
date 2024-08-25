# Focused Macros Greedy Best-First: Planning
Greedy best-first search to learn focused macros and perform planning to solve the Rubik's Cube

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
Learning Time: 2:54:10
# of Macros Generated: 576
Best Net Effect (h) Heuristic: 6
Worst Net Effect (h) Heuristic: 15
Shortest Macro Length (g): 6
Longest Macro Length (g): 12
```

### Planning
Saved in `/output/cube_solution_start<index>.pkl`.

| Cube Start Index   | Greedy BFS Planning Time |
| :----------------: | :----------------------: |
| 0                  | 01:06                    |
| 1                  | 06:10                    |
| 50                 | 29:04                    |
| 99                 | 28:58                    |
