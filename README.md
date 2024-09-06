# Focused Macros
Greedy best-first search to learn focused macros and perform planning to solve the Rubik's Cube

## Init Setup

### Clone repo
```
git clone --recursive git@github.com:xyntechx/focused-macros.git
cd focused-macros
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

### Learn focused macros
```
python3 macro_learning.py
```

### Run planning
```
python3 planning.py
```

### Solve cube with a saved plan
```
python3 solve.py
```

## Results

### Macro Learning
Saved in `/output/learned_macros.pkl`

```
Max Fringe Size: N_m * 10
Learning Time: 06:38
# of Macros Generated: 576
Best Net Effect (h) Heuristic: 6
Worst Net Effect (h) Heuristic: 16
Shortest Macro Length (g): 6
Longest Macro Length (g): 16
```

### Planning
Saved in `/output/cube_solution_start<index>.pkl`

| Cube Start Index   | Greedy BFS Planning Time |
| :----------------: | :----------------------: |
| 0                  | 00:36                    |
| 1                  | 04:00                    |
| 14                 | 01:15                    |
| 20                 | 10:14                    |
| 50                 | 07:51                    |
| 99                 | 02:04                    |
