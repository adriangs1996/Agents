import time
from src.robot import Robot
from src.environment import Environment
from time import sleep
from os import system

SUCCESS = 1
FAILURE = 0
AVERAGE = 2


def testRobot(N: int, M: int, kids: int, dirtiness: int, obstacles: int, t: int):
    env = Environment(N, M, dirtiness, obstacles, kids, t)
    robot = Robot(env)

    elapsedTime = 0
    success = 0
    failures = 0
    average = 0
    times = 1

    ticker = r"\|/-"

    while elapsedTime < 100 * t:
        elapsedTime += 1
        print(f"Emulating: {times}% {ticker[times % 4]}", end="\r")
        # print(f"Empty: {env.EmptyCells}")
        # print(f"Dirty: {len(env.Dirt)}")
        # print(f"Dirtiness: {env.Dirtiness}%")
        # print(f"Moves remaining: {env.t - elapsedTime % t}")
        # print(f"Lap: {times}")
        # print(env)


        # Play the robot
        robot.decide()
        if env.JobDone:
            # system("clear")
            # print(f"Empty: {env.EmptyCells}")
            # print(f"Dirty: {len(env.Dirt)}")
            # print(f"Dirtiness: {env.Dirtiness}%")
            # print(env)
            success += 1
            env.randomChange(N, M, dirtiness, obstacles, kids)
            elapsedTime = times * t + 1
            times += 1

        if not env.IsClean:
            # system("clear")
            # print(f"Empty: {env.EmptyCells}")
            # print(f"Dirty: {len(env.Dirt)}")
            # print(f"Dirtiness: {env.Dirtiness}%")
            # print(env)
            failures += 1
            elapsedTime = times * t + 1
            times += 1
            env.randomChange(N, M, dirtiness, obstacles, kids)

            
        # play the environment
        env.naturalChange()

        # See if we must make a random change
        if elapsedTime % t == 0:
            average += 1
            times += 1
            env.randomChange(N, M, dirtiness, obstacles, kids)

        # sleep(0.5)

    print()
        
    print(f"Success: {success}")
    print(f"Failures: {failures}")
    print(f"Averages: {average}")


if __name__ == "__main__":
    testRobot(7, 8, 4, 30, 20, 45)