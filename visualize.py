import pandas as pd
import seaborn as sns


def read_data(learned_macros_type, i):
    index = i.zfill(3)
    filename = f"output/data/{learned_macros_type}/{index}.pkl"
    df = pd.read_pickle(filename)
    return df


def populate_df(df, learned_macros_type, index=None):
    if index:
        sub_df = read_data(learned_macros_type, index)
        sub_df.insert(0, "cube_id", [int(index)]*sub_df.shape[0], allow_duplicates=True)
        sub_df.insert(0, "learned_macros_type", [learned_macros_type]*sub_df.shape[0], allow_duplicates=True)
        df = pd.concat([df, sub_df], ignore_index=True)
    else:
        for i in range(100):
            sub_df = read_data(learned_macros_type, str(i))
            sub_df.insert(0, "cube_id", [i]*sub_df.shape[0], allow_duplicates=True)
            sub_df.insert(0, "learned_macros_type", [learned_macros_type]*sub_df.shape[0], allow_duplicates=True)
            df = pd.concat([df, sub_df], ignore_index=True)
    return df


def generate_plot(df, y_code, index, learned_macros_type="all"):
    assert y_code in ["E", "L"], "Invalid option entered. Rerun the program and enter either `E` or `L`."
    metric = "effect_sizes" if y_code == "E" else "macro_lengths"

    plot = sns.lineplot(data=df, x="step", y=metric, hue="learned_macros_type")
    fig = plot.get_figure()
    fig.savefig(f"output/plots/{learned_macros_type}/{metric}_{index if index else "all"}.png")


if __name__ == "__main__":
    print("Select your learned macros...")
    print("Select `n10` for macros learned using the limited fringe of maximum size N_m * 10")
    print("Select `inf` for macros learned using the unlimited fringe")

    learned_macros_type = input("Enter `n10` or `inf` (if left empty, default=all): ")
    if learned_macros_type and learned_macros_type not in ["n10", "inf"]:
        exit("Invalid option entered. Rerun the program and enter either `n10` or `inf`.")

    index = input("Enter start sequence index [0-99] (if left empty, default=all): ")
    y_code = input("Select data to plot: effect size (E) or macro length (L)? ").upper()

    sns.set_theme()

    df = pd.DataFrame()

    if learned_macros_type:
        df = populate_df(df, learned_macros_type, index=index if index else None)
    else:
        df = populate_df(df, "inf", index=index if index else None)
        df = populate_df(df, "n10", index=index if index else None)
        learned_macros_type = "all"

    generate_plot(df, y_code, index, learned_macros_type=learned_macros_type)
