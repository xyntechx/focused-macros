import pandas as pd
import seaborn as sns


def read_data(learned_macros_type, i):
    index = i.zfill(3)
    filename = f"output/data/{learned_macros_type}/{index}.pkl"
    df = pd.read_pickle(filename)
    return df


if __name__ == "__main__":
    print("Select your learned macros...")
    print("Select `n10` for macros learned using the limited fringe of maximum size N_m * 10")
    print("Select `inf` for macros learned using the unlimited fringe")

    learned_macros_type = input("Enter `n10` or `inf`: ")
    if learned_macros_type not in ["n10", "inf"]:
        exit("Invalid option entered. Rerun the program and enter either `n10` or `inf`.")

    print("Finding plan to solve cube with learned focused macros...")
    index = input("Enter start sequence index [0-99] (if left empty, default=all): ")

    if index:
        df = read_data(learned_macros_type, index)
    else:
        df = read_data(learned_macros_type, str(0))
        df.insert(0, "cube_id", [0]*df.shape[0], allow_duplicates=True)
        for i in range(1, 100):
            sub_df = read_data(learned_macros_type, str(i))
            sub_df.insert(0, "cube_id", [i]*sub_df.shape[0], allow_duplicates=True)
            df = pd.concat([df, sub_df], ignore_index=True)

    sns.set_theme()

    y = input("Select data to plot: effect size (E) or macro length (L)? ").upper()

    if y == "E":
        plot = sns.lineplot(data=df, x="step", y="effect_sizes")
        fig = plot.get_figure()
        fig.savefig(f"output/plots/{learned_macros_type}/effect_sizes_{index if index else "all"}.png")
    elif y == "L":
        plot = sns.lineplot(data=df, x="step", y="macro_lengths")
        fig = plot.get_figure()
        fig.savefig(f"output/plots/{learned_macros_type}/macro_lengths_{index if index else "all"}.png")
    else:
        exit("Invalid option entered. Rerun the program and enter either `E` or `L`.")
