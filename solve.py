import pickle
from cam.domains.cube.cubeenv import CubeEnv
from utils import get_init_actions


if __name__ == "__main__":
    print("Solving cube with saved plan...")

    index = input("Enter start sequence index [0-99] (if left empty, default=0): ")
    try:
        init_actions = get_init_actions(int(index))
    except ValueError:
        init_actions = get_init_actions()

    with open(f"output/cube_solution_start{str(index).zfill(3)}.pkl", "rb") as f:
        plan = pickle.load(f).split(" ")

    simulator = CubeEnv()

    # Initialize cube at selected starting state
    init_seq = [simulator.action_lookup[a] for a in init_actions]
    simulator.reset(sequence=init_seq)
    print("Initial scrambled state")
    print(init_actions)
    simulator.render()

    # Solve cube with saved plan
    plan_seq = [simulator.action_lookup[a] for a in plan]
    for action in plan_seq:
        simulator.step(action)
    print("State after implementing saved plan")
    print(plan)
    simulator.render()
