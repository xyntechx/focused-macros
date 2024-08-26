import pickle
import math
from tqdm import tqdm
from cam.domains.cube.cubeenv import CubeEnv
from utils import get_init_actions, join_int_list


def optimized_reset(curr_simulator, curr_sequence, base_actions):
    if len(base_actions) < len(curr_sequence):
        curr_simulator.reset(sequence=base_actions)
    else:
        for action in reversed(curr_sequence):
            curr_simulator.step((action + 6) % 12) # undo action


def learn_macros(base_simulator: CubeEnv, N_m=576, R_m=1, B_m=1_000_000, disable_progress=False):
    # Specs of base_simulator (describing root node of search tree)
    base_state = join_int_list(base_simulator.state)
    base_actions = base_simulator.sequence
    base_data = {base_state: {
        "f": math.inf, # f-heuristic = net effect (h) + macro length (g)
        "net_actions": [] # actions taken from base_state
    }}

    # Initialize relevant vars for BFS
    best_state = base_state # state with lowest f-heuristic (init as base_state)
    fringe = base_data # data dict of all states ready to be expanded (init as base_data)
    max_fringe_len = N_m * 10 # max allowed length for runtime optimizations
    visited = {} # data dict of all states already visited (init as empty dict)

    # Setting up simulator to be updated during search
    curr_simulator = CubeEnv()
    curr_simulator.reset(sequence=base_actions)

    with tqdm(total=B_m//R_m, disable=disable_progress) as progress:
        counter = 0

        while counter < B_m//R_m:
            if best_state in visited:
                if fringe[best_state]["f"] < visited[best_state]["f"]:
                    visited[best_state] = fringe[best_state]

                fringe.pop(best_state)
                best_state = min(fringe, key=lambda x: fringe[x]["f"])

                continue # if I've visited this state before, there's no point in expanding it again
            visited[best_state] = fringe[best_state]

            curr_sequence = fringe[best_state]["net_actions"]
            for action in curr_sequence:
                curr_simulator.step(action)

            for action in base_simulator.action_meanings:
                state, _, _ = curr_simulator.step(action)
                curr_state = join_int_list(state)
                curr_actions = curr_sequence + [action]
                curr_f = curr_simulator.diff(baseline=base_simulator.cube) + len(curr_actions)

                if curr_state in fringe:
                    if curr_f < fringe[curr_state]["f"]:
                        fringe[curr_state] = {
                            "f": curr_f,
                            "net_actions": curr_actions
                        }
                else:
                    fringe[curr_state] = {
                        "f": curr_f,
                        "net_actions": curr_actions
                    }

                    # Maintaining fringe length at max allowed length for runtime optimizations
                    if len(fringe) > max_fringe_len:
                        worst_state = max(fringe, key=lambda x: fringe[x]["f"])
                        fringe.pop(worst_state)

                curr_simulator.step((action + 6) % 12) # undo action
                counter += 1
                progress.update()

            optimized_reset(curr_simulator, curr_sequence, base_actions)
            fringe.pop(best_state)
            best_state = min(fringe, key=lambda x: fringe[x]["f"])

    macros = {}
    for _ in range(N_m//R_m):
        best_state = min(visited, key=lambda x: visited[x]["f"] - len(visited[x]["net_actions"]))
        macros[best_state] = visited.pop(best_state)

    # Stats
    best_state = min(macros, key=lambda x: macros[x]["f"] - len(macros[x]["net_actions"]))
    worst_state = max(macros, key=lambda x: macros[x]["f"] - len(macros[x]["net_actions"]))
    print(f"# of Macros Generated: {len(macros)}")
    print(f"Best Net Effect (h) Heuristic: {macros[best_state]["f"] - len(macros[best_state]["net_actions"])}")
    print(f"Worst Net Effect (h) Heuristic: {macros[worst_state]["f"] - len(macros[worst_state]["net_actions"])}")
    print(f"Shortest Macro Length (g): {len(macros[min(macros, key=lambda x: len(macros[x]["net_actions"]))]["net_actions"])}")
    print(f"Longest Macro Length (g): {len(macros[max(macros, key=lambda x: len(macros[x]["net_actions"]))]["net_actions"])}")

    return [macros[state]["net_actions"] for state in macros]


if __name__ == "__main__":
    print("Learn focused macros using best-first search")

    index = input("Enter start sequence index [0-99] (if left empty, default=0): ")
    try:
        init_actions = get_init_actions(int(index))
    except ValueError:
        init_actions = get_init_actions()

    base_simulator = CubeEnv()
    init_seq = [base_simulator.action_lookup[a] for a in init_actions]
    base_simulator.reset(sequence=init_seq)

    macros = []
    sequences = learn_macros(base_simulator)
    for seq in sequences:
        macro = " ".join([base_simulator.action_meanings[s] for s in seq])
        macros.append(macro)

    with open("output/learned_macros.pkl", "wb") as f:
        pickle.dump(macros, f)
