import pickle
from tqdm import tqdm
from queue import PriorityQueue
from cam.domains.cube.cubeenv import CubeEnv

# Best first search for planning, guided by goal-count heuristic
# Action space includes both base/primitive actions and focused macros learned via macro_learning.py


def get_init_actions(index=0):
    """
    Get initial actions from cam/domains/cube/random_starts with index=index (e.g. index=0 => start-000.txt) to set the initial state of the cube
    """
    assert index < 100, "There are only 100 files/predetermined initial states range=[0, 99]"

    with open(f"cam/domains/cube/random_starts/start-{str(index).zfill(3)}.txt") as f:
        init_actions = f.read().strip().split(" ")
    
    return init_actions


def bfs(init_seq, learned_macros, N_m=576, B_m=1_000_000, disable_progress=False):
    simulator = CubeEnv()
    simulator.reset(sequence=init_seq)
    curr_seq = simulator.sequence

    with tqdm(total=B_m, disable=disable_progress) as progress:
        for _ in range(B_m // (simulator.n_actions + N_m)):
            possible_gcount_actions = []

            # Primitive actions
            for a in simulator.action_meanings.keys():
                simulator.step(a)
                if simulator.diff() == 0: # solved
                    simulator.render()
                    return curr_seq + [a]
                possible_gcount_actions.append((simulator.diff(), [a]))
                simulator.reset(sequence=simulator.sequence)
                progress.update()

            # Macros
            for macro in learned_macros:
                primitives = [simulator.action_lookup[a] for a in macro.split(" ")]
                for a in primitives:
                    simulator.step(a)
                if simulator.diff() == 0: # solved
                    simulator.render()
                    return curr_seq + [a]
                possible_gcount_actions.append((simulator.diff(), primitives))
                simulator.reset(sequence=simulator.sequence)
                progress.update()

            best_macro = min(possible_gcount_actions, key=lambda x: x[0])
            best_action = best_macro[1]
            print(f"Goal count: {best_macro[0]}")
            curr_seq = simulator.sequence + best_action
            simulator.reset(sequence=curr_seq)

    simulator.render()
    return curr_seq


if __name__ == "__main__":
    with open("output/learned_macros.pkl", "rb") as f:
        learned_macros = pickle.load(f)
        print(f"{len(learned_macros)} macros found")

    print("Planning...")

    index = input("Enter start sequence index [0-99] (if left empty, default=0): ")
    try:
        init_actions = get_init_actions(int(index))
    except ValueError:
        init_actions = get_init_actions()

    init_seq = [CubeEnv().action_lookup[a] for a in init_actions]
    plan = bfs(init_seq, learned_macros, B_m=50_000)

    print(plan)

    with open("output/cube_solution.pkl", "wb") as f:
        pickle.dump(plan, f)
