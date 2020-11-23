from src.robot import Robot
from src.environment import Environment

SUCCESS = 1
FAILURE = 0
AVERAGE = 2


def testRobot(N: int, M: int, kids: int, dirtiness: int, obstacles: int, t: int):
    env = Environment(N, M, dirtiness, obstacles, kids, t)
    robot = Robot(env)

    elapsedTime = 0

    while elapsedTime < 100 * t:
        elapsedTime += 1

        if env.JobDone:
            return SUCCESS

        if not env.IsClean:
            return FAILURE

        # Play the robot
        robot.decide()

        # play the environment
        env.naturalChange()

        # See if we must make a random change
        if elapsedTime % t == 0:
            env.randomChange(N, M, dirtiness, obstacles, kids)
    return AVERAGE