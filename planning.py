import pickle
from tqdm import tqdm
from copy import deepcopy
from sys import exit
import pandas as pd

from cam.domains.cube.cubeenv import CubeEnv
from utils import get_init_actions, join_int_list


def save_results(cube_index, learned_macros_type, effect_sizes, macro_lengths):
    d = {
        "step": range(len(effect_sizes)),
        "effect_sizes": effect_sizes,
        "macro_lengths": macro_lengths,
    }
    df = pd.DataFrame(data=d)
    filename = f"output/data/{learned_macros_type}/{cube_index}.pkl"
    df.to_pickle(filename)


def generate_plan(simulator: CubeEnv, init_seq, learned_macros, learned_macros_type, cube_index, N_m=576, B_m=1_000_000, disable_progress=False):
    simulator.render()
    curr_seq = simulator.sequence
    max_gcount = 48 # maximum goal count heuristic is 48 as the simulator uses a 48-state-variable representation
    visited_states = []

    # To plot
    effect_sizes = []
    macro_lengths = []

    with tqdm(total=max_gcount, disable=disable_progress) as progress:
        for _ in range(B_m // (simulator.n_actions + N_m)):
            candidates = [] # (goal count, actions, net effect)
            base_cube = deepcopy(simulator.cube)

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

                    save_results(cube_index, learned_macros_type, effect_sizes, macro_lengths)

                    return [*curr_seq, a][len(init_seq):]

                candidates.append((simulator.diff(), [a], simulator.diff(baseline=base_cube)))
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

                    save_results(cube_index, learned_macros_type, effect_sizes, macro_lengths)

                    return [*curr_seq, *primitives][len(init_seq):]

                candidates.append((simulator.diff(), primitives, simulator.diff(baseline=base_cube)))
                for a in reversed(primitives):
                    simulator.step((a + 6) % 12) # undo action

            best_macro = min(candidates, key=lambda x: x[0])
            best_seq = best_macro[1]
            curr_seq += best_seq
            for a in best_seq:
                simulator.step(a)

            effect_sizes.append(best_macro[2])
            macro_lengths.append(len(best_macro[1]))

            progress.last_print_n = progress.n = max_gcount - best_macro[0]
            progress.refresh()

    simulator.render()
    print(f"Unable to solve cube in {B_m} iterations")

    save_results(cube_index, learned_macros_type, effect_sizes, macro_lengths)

    return curr_seq[len(init_seq):]


def main(simulator: CubeEnv, learned_macros, learned_macros_type, i):
    index = i.zfill(3)
    init_actions = get_init_actions(index)

    init_seq = [simulator.action_lookup[a] for a in init_actions]
    simulator.reset(sequence=init_seq)

    seq = generate_plan(simulator, init_seq, learned_macros, learned_macros_type, index)
    plan = " ".join([simulator.action_meanings[s] for s in seq])

    with open(f"output/plans/{learned_macros_type}/{index}.pkl", "wb") as f:
        pickle.dump(plan, f)

    print(f"Saved plan in output/plans/{learned_macros_type}/{index}.pkl (saved sequence excludes start sequence)")
    print(plan)


if __name__ == "__main__":
    print("Select your learned macros...")
    print("Select `n10` for macros learned using the limited fringe of maximum size N_m * 10")
    print("Select `inf` for macros learned using the unlimited fringe")

    learned_macros_type = input("Enter `n10` or `inf`: ")
    if learned_macros_type not in ["n10", "inf"]:
        exit("Invalid option entered. Rerun the program and enter either `n10` or `inf`.")

    with open(f"output/{learned_macros_type}_learned_macros.pkl", "rb") as f:
        learned_macros = [macro.split(" ") for macro in pickle.load(f)]
        print(f"{len(learned_macros)} macros found")

    simulator = CubeEnv()

    print("Finding plan to solve cube with learned focused macros...")
    index = input("Enter start sequence index [0-99] (if left empty, default=all): ")
    
    if index:
        plan = main(simulator, learned_macros, learned_macros_type, index)
    else:
        for i in range(100):
            plan = main(simulator, learned_macros, learned_macros_type, str(i))
