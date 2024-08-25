import pickle
import math
from tqdm import tqdm
from cam.domains.cube.cubeenv import CubeEnv


def get_init_actions(index=0):
    """
    Get initial actions from cam/domains/cube/random_starts with index=index (e.g. index=0 => start-000.txt) to set the initial state of the cube
    """
    assert index < 100, "There are only 100 files/predetermined initial states range=[0, 99]"

    with open(f"cam/domains/cube/random_starts/start-{str(index).zfill(3)}.txt") as f:
        init_actions = f.read().strip().split(" ")
    
    return init_actions


def net_actions(sequence, base_actions):
    return sequence[len(base_actions):]


def join_int_list(lst):
    lst_str = [str(i) for i in lst]
    return "".join(lst_str)


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
        "net_actions": net_actions(base_actions, base_actions) # actions taken from base_state
    }}

    # Initialize relevant vars for BFS
    best_state = base_state # state with lowest f-heuristic (init as base_state)
    fringe = base_data # data dict of all states ready to be expanded (init as base_data)
    visited = {} # data dict of all states already visited (init as empty dict)

    # Setting up simulator to be updated during search
    curr_simulator = CubeEnv()
    curr_simulator.reset(sequence=base_actions)

    with tqdm(total=B_m//R_m, disable=disable_progress) as progress:
        counter = 0

        while counter < B_m//R_m:
            curr_sequence = fringe[best_state]["net_actions"][:]
            for action in curr_sequence:
                curr_simulator.step(action)

            if best_state in visited.keys():
                # Compare based on net effect (h) heuristic
                fringe_h = fringe[best_state]["f"] - len(curr_sequence)
                visited_h = visited[best_state]["f"] - len(visited[best_state]["net_actions"])

                if fringe_h < visited_h:
                    visited[best_state] = fringe[best_state]

                fringe.pop(best_state)
                best_state = min(fringe.keys(), key=lambda x: fringe[x]["f"])
                optimized_reset(curr_simulator, curr_sequence, base_actions)

                continue # if I've visited this state before, there's no point in expanding it again
            else:
                visited[best_state] = fringe[best_state]

            if len(visited) > N_m//R_m:
                # Evaluate worst state based on net effect (h) heuristic
                worst_state = max(visited.keys(), key=lambda x: visited[x]["f"] - len(visited[x]["net_actions"]))
                visited.pop(worst_state)

            for action in base_simulator.action_meanings.keys():
                state, _, _ = curr_simulator.step(action)
                curr_state = join_int_list(state)
                curr_actions = net_actions(base_actions + curr_sequence + [action], base_actions)
                curr_f = curr_simulator.diff(baseline=base_simulator.cube) + len(curr_actions)

                if curr_state in fringe.keys():
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

                curr_simulator.step((action + 6) % 12) # undo action
                counter += 1
                progress.update()

            optimized_reset(curr_simulator, curr_sequence, base_actions)

            fringe.pop(best_state)
            best_state = min(fringe.keys(), key=lambda x: fringe[x]["f"])

    # Stats
    best_state = min(visited.keys(), key=lambda x: visited[x]["f"] - len(visited[x]["net_actions"]))
    worst_state = max(visited.keys(), key=lambda x: visited[x]["f"] - len(visited[x]["net_actions"]))
    print(f"# of Macros Generated: {len(visited)}")
    print(f"Best Net Effect (h) Heuristic: {visited[best_state]["f"] - len(visited[best_state]["net_actions"])}")
    print(f"Worst Net Effect (h) Heuristic: {visited[worst_state]["f"] - len(visited[worst_state]["net_actions"])}")

    return [visited[state]["net_actions"] for state in visited]


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
