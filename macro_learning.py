import pickle
from tqdm import tqdm
from queue import PriorityQueue
from max_pq import MaxPQ
from cam.domains.cube.cubeenv import CubeEnv

def get_init_actions(index=0):
    """
    Get initial actions from cam/domains/cube/random_starts with index=index (e.g. index=0 => start-000.txt) to set the initial state of the cube
    """
    assert index < 100, "There are only 100 files/predetermined initial states range=[0, 99]"

    with open(f"cam/domains/cube/random_starts/start-{str(index).zfill(3)}.txt") as f:
        init_actions = f.read().strip().split(" ")
    
    return init_actions


def bfs(init_seq, N_m=576, R_m=1, B_m=1_000_000, disable_progress=False):
    # Initialize baseline simulator
    simulator_0 = CubeEnv()
    simulator_0.reset(sequence=init_seq)
    seq_0 = simulator_0.sequence

    # Initialize fringe with initial state s0
    fringe = PriorityQueue() # priority f (effect size + macro length)
    fringe.put((0, seq_0))

    visited_states = []

    macros_max_pq = MaxPQ(maxsize=N_m/R_m) # priority h (effect size)

    t_count = 0
    with tqdm(total=B_m, disable=disable_progress) as progress:
        while t_count < B_m:
            # Initialize active simulator
            curr_seq = fringe.get(block=False)[1]
            simulator = CubeEnv()

            for a in simulator.action_meanings.keys():
                t_count += 1
                progress.update()
                simulator.reset(sequence=curr_seq)

                state, _, done = simulator.step(a)

                if state in visited_states:
                    continue
                visited_states.append(state)

                seq = curr_seq + [a]
                h = simulator.diff(baseline=simulator_0.cube)
                g = len(seq) - len(seq_0)
                f = h + g

                if done:
                    if macros_max_pq.full():
                        macros_max_pq.get()
                    macros_max_pq.put((h, seq))
                    return macros_max_pq

                fringe.put((f, seq))

                if macros_max_pq.full():
                    worst_macro = macros_max_pq.get()
                    if h < worst_macro[0]:
                        macros_max_pq.put((h, seq))
                    else:
                        macros_max_pq.put(worst_macro)
                else:
                    macros_max_pq.put((h, seq))

    return macros_max_pq


if __name__ == "__main__":
    print("Learn focused macros using best-first search")

    index = input("Enter start sequence index [0-99] (if left empty, default=0): ")
    try:
        init_actions = get_init_actions(int(index))
    except ValueError:
        init_actions = get_init_actions()

    init_seq = [CubeEnv().action_lookup[a] for a in init_actions]
    macros_max_pq = bfs(init_seq)
    # macros_max_pq = bfs(init_seq, B_m=100)
    macros_set = set()
    while not macros_max_pq.empty():
        seq = macros_max_pq.get()[1]
        seq_str = " ".join([CubeEnv().action_meanings[s] for s in seq])
        macros_set.add(seq_str)

    with open("output/learned_macros.pkl", "wb") as f:
        pickle.dump(list(macros_set), f)
