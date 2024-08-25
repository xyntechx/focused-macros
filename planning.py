import pickle
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


def join_int_list(lst):
    lst_str = [str(i) for i in lst]
    return "".join(lst_str)


def bfs(init_seq, learned_macros, N_m=576, B_m=1_000_000, disable_progress=False):
    simulator = CubeEnv()
    simulator.reset(sequence=init_seq)
    curr_seq = simulator.sequence
    visited_states = []

    with tqdm(total=B_m, disable=disable_progress) as progress:
        for _ in range(B_m // (simulator.n_actions + N_m)):
            possible_gcount_actions = []

            # Primitive actions
            for a in simulator.action_meanings.keys():
                state, _, _ = simulator.step(a)
                state_str = join_int_list(state)

                # Check if state has been visited
                if state_str in visited_states:
                    simulator.step((a + 6) % 12) # undo action
                    progress.update()
                    continue
                visited_states.append(state_str)

                if simulator.diff() == 0: # solved
                    simulator.render()
                    return curr_seq + [a]

                possible_gcount_actions.append((simulator.diff(), [a]))
                simulator.step((a + 6) % 12) # undo action
                progress.update()

            # Learned macros
            for macro in learned_macros:
                # Perform all actions in the macro
                primitives = [simulator.action_lookup[a] for a in macro.split(" ")]
                for a in primitives:
                    state, _, _ = simulator.step(a)

                # Check if state has been visited
                state_str = join_int_list(simulator.state)
                if state_str in visited_states:
                    for a in reversed(primitives):
                        simulator.step((a + 6) % 12) # undo action
                    progress.update()
                    continue
                visited_states.append(state_str)

                if simulator.diff() == 0: # solved
                    simulator.render()
                    return curr_seq + [a]

                possible_gcount_actions.append((simulator.diff(), primitives))
                for a in reversed(primitives):
                    simulator.step((a + 6) % 12) # undo action
                progress.update()

            best_macro = min(possible_gcount_actions, key=lambda x: x[0])
            best_seq = best_macro[1]
            print(f"Goal count: {best_macro[0]}")
            curr_seq += best_seq
            for a in best_seq:
                simulator.step(a)

    simulator.render()
    return curr_seq


if __name__ == "__main__":
    with open("output/learned_macros.pkl", "rb") as f:
        learned_macros = pickle.load(f)
        print(f"{len(learned_macros)} macros found")
        print(learned_macros)

    print("Planning...")

    index = input("Enter start sequence index [0-99] (if left empty, default=0): ")
    try:
        init_actions = get_init_actions(int(index))
    except ValueError:
        init_actions = get_init_actions()

    init_seq = [CubeEnv().action_lookup[a] for a in init_actions]
    plan = bfs(init_seq, learned_macros)

    print(plan)

    with open(f"output/cube_solution_start{str(index).zfill(3)}.pkl", "wb") as f:
        pickle.dump(plan, f)
