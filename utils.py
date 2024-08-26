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
