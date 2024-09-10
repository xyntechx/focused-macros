import pickle
from tqdm import tqdm
from copy import deepcopy
import matplotlib.pyplot as plt
from cam.domains.cube.cubeenv import CubeEnv
from utils import get_init_actions, join_int_list


def plot_results(x, y, cube_index, title="Figure"):
    fig, ax = plt.subplots()
    ax.scatter(x, y, linewidth=2.0)
    fig.suptitle(title)

    plt.savefig(f"output/plots/{"_".join(title.lower().split())}_cube{cube_index}.png")


def generate_plan(simulator: CubeEnv, learned_macros, cube_index, N_m=576, B_m=1_000_000, disable_progress=False):
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

                    plot_results(range(0, len(effect_sizes)), effect_sizes, cube_index, title="Effect Size")
                    plot_results(range(0, len(macro_lengths)), macro_lengths, cube_index, title="Macro Length")

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

                    plot_results(range(0, len(effect_sizes)), effect_sizes, cube_index, title="Effect Size")
                    plot_results(range(0, len(macro_lengths)), macro_lengths, cube_index, title="Macro Length")

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

    plot_results(range(0, len(effect_sizes)), effect_sizes, cube_index, title="Effect Size")
    plot_results(range(0, len(macro_lengths)), macro_lengths, cube_index, title="Macro Length")

    return curr_seq[len(init_seq):]


if __name__ == "__main__":
    with open("output/learned_macros.pkl", "rb") as f:
        learned_macros = [macro.split(" ") for macro in pickle.load(f)]
        print(f"{len(learned_macros)} macros found")

    print("Finding plan to solve cube with learned focused macros...")

    index = input("Enter start sequence index [0-99] (if left empty, default=0): ")
    index = str(index if index else '0').zfill(3)
    init_actions = get_init_actions(index)

    simulator = CubeEnv()
    init_seq = [simulator.action_lookup[a] for a in init_actions]
    simulator.reset(sequence=init_seq)

    seq = generate_plan(simulator, learned_macros, index)
    plan = " ".join([simulator.action_meanings[s] for s in seq])

    with open(f"output/cube_solution_start{index}.pkl", "wb") as f:
        pickle.dump(plan, f)

    print(f"Saved plan in output/cube_solution_start{index}.pkl (saved sequence excludes start sequence)")
    print(plan)
