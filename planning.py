import pickle
from tqdm import tqdm
from cam.domains.cube.cubeenv import CubeEnv
from utils import get_init_actions, join_int_list


def bfs(simulator: CubeEnv, learned_macros, N_m=576, B_m=1_000_000, disable_progress=False):
    simulator.render()
    curr_seq = simulator.sequence
    max_gcount = 48 # maximum goal count heuristic is 48 as the simulator uses a 48-state-variable representation
    visited_states = []

    with tqdm(total=max_gcount, disable=disable_progress) as progress:
        for _ in range(B_m // (simulator.n_actions + N_m)):
            possible_gcount_actions = []

            # Primitive actions
            for a in simulator.action_meanings.keys():
                state, _, _ = simulator.step(a)
                state_str = join_int_list(state)

                # Check if state has been visited
                if state_str in visited_states:
                    simulator.step((a + 6) % 12) # undo action
                    continue
                visited_states.append(state_str)

                if simulator.diff() == 0: # solved
                    progress.last_print_n = progress.n = max_gcount
                    progress.refresh()
                    simulator.render()
                    print("Cube solved!")
                    return [*curr_seq, a][len(init_seq):]

                possible_gcount_actions.append((simulator.diff(), [a]))
                simulator.step((a + 6) % 12) # undo action

            # Learned macros
            for macro in learned_macros:
                # Perform all actions in the macro
                primitives = [simulator.action_lookup[a] for a in macro]
                for a in primitives:
                    state, _, _ = simulator.step(a)

                # Check if state has been visited
                state_str = join_int_list(simulator.state)
                if state_str in visited_states:
                    for a in reversed(primitives):
                        simulator.step((a + 6) % 12) # undo action
                    continue
                visited_states.append(state_str)

                if simulator.diff() == 0: # solved
                    progress.last_print_n = progress.n = max_gcount
                    progress.refresh()
                    simulator.render()
                    print("Cube solved!")
                    return [*curr_seq, *primitives][len(init_seq):]

                possible_gcount_actions.append((simulator.diff(), primitives))
                for a in reversed(primitives):
                    simulator.step((a + 6) % 12) # undo action

            best_macro = min(possible_gcount_actions, key=lambda x: x[0])
            best_seq = best_macro[1]
            curr_seq += best_seq
            for a in best_seq:
                simulator.step(a)

            progress.last_print_n = progress.n = max_gcount - best_macro[0]
            progress.refresh()

    simulator.render()
    print(f"Unable to solve cube in {B_m} iterations")
    return curr_seq[len(init_seq):]


if __name__ == "__main__":
    with open("output/learned_macros.pkl", "rb") as f:
        learned_macros = [macro.split(" ") for macro in pickle.load(f)]
        print(f"{len(learned_macros)} macros found")

    print("Finding plan to solve cube with learned focused macros...")

    index = input("Enter start sequence index [0-99] (if left empty, default=0): ")
    try:
        init_actions = get_init_actions(int(index))
    except ValueError:
        init_actions = get_init_actions()

    simulator = CubeEnv()
    init_seq = [simulator.action_lookup[a] for a in init_actions]
    simulator.reset(sequence=init_seq)

    seq = bfs(simulator, learned_macros)
    plan = " ".join([simulator.action_meanings[s] for s in seq])

    with open(f"output/cube_solution_start{str(index).zfill(3)}.pkl", "wb") as f:
        pickle.dump(plan, f)

    print(f"Saved plan in output/cube_solution_start{str(index).zfill(3)}.pkl (saved sequence excludes start sequence)")
    print(plan)
