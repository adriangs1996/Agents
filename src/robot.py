from typing import List, Tuple
from environment import around, Environment, CellContent
from math import acos, inf


LEFT = 0, -1
RIGHT = 0, 1
UP = -1, 0
DOWN = 1, 0
UPRIGHT = -1, 1
UPLEFT = -1, -1
DOWNLEFT = 1, -1
DOWNRIGHT = 1, 1

CLEAN = "Clean"
HUNTKID = "Hunt"
DELIVER = "Deliver"


class Robot:
    def __init__(self, environment: Environment) -> None:
        self.environment = environment

    @property
    def RobotState(self):
        return self.environment.Robot

    @property
    def RobotIsCarryingKid(self):
        _, _, robot = self.RobotState
        return robot in (
            CellContent.RobotWithKid,
            CellContent.RobotCarryingKidInCorral,
        )

    def __deliver(self, count=2):
        if count == 0:
            return
        x, y, _ = self.RobotState
        _, d, path = self.__getDistanceToGoal((x,y), CellContent.Corral)
        if d == inf:
            print("Corral unreacheable")
        elif d == 0:
            self.drop()
        else:
            xdir, ydir = path[0][0] - x, path[0][0] - y
            self.move((xdir, ydir))
            self.__deliver(count - 1)
    
    def __moveTowardsClosestDirt(self):
        x, y, _ = self.RobotState
        _, d, path = self.__getDistanceToGoal((x,y), CellContent.Dirt)
        if d == inf:
            print("Dirt unreacheable")
        elif d == 0:
            self.clean()
        else:
            xdir, ydir = path[0][0] - x, path[0][0] - y
            self.move((xdir, ydir))

    def __moveTowardsClosestKid(self):
        x, y, _ = self.RobotState
        _, d, path = self.__getDistanceToGoal((x,y), CellContent.Kid)
        if d == inf:
            print("Kid unreacheable")
        elif d == 1:
            xdir, ydir = path[0][0] - x, path[0][0] - y
            self.move((xdir, ydir))
            self.carry()
        else:
            xdir, ydir = path[0][0] - x, path[0][0] - y
            self.move((xdir, ydir))


    def __getDistanceToGoal(self, origin: Tuple[int, int], goal: CellContent):
        # Simple BFS searching for goal.
        # This search is always made by the robot,
        # so valid cells to move does not include obstacles.
        queue: List[Tuple[Tuple[int, int], int, List[Tuple[int, int]]]] = [
            (origin, 0, [])
        ]

        target = [goal]
        if goal == CellContent.Dirt:
            target.append(CellContent.RobotWithDirt)
        if goal == CellContent.Corral:
            target.append(CellContent.RobotCarryingKidInCorral)

        while queue:
            pos, d, path = queue.pop(0)
            if self.environment[pos] in target:
                return pos, d, path
            for nextPos in around(pos):
                if self.environment[nextPos] in (
                    CellContent.Empty,
                    CellContent.Corral,
                    CellContent.Dirt,
                    CellContent.KidInCorral,
                ):
                    queue.append((nextPos, d + 1, path + [nextPos]))
        return origin, inf, []

    def __findBestKid(self):
        rx, ry, _ = self.RobotState

        d = inf
        k = (-1, -1)

        for kid in self.environment.Kids:
            pos, d1, _ = self.__getDistanceToGoal((rx, ry), self.environment[kid])
            _, d2, _ = self.__getDistanceToGoal(pos, CellContent.Corral)
            if d1 + d2 < d:
                k = pos
                d = d1 + d2
        return k

    def __evalEnvironment(self):
        # Robot should prioritize not to get fired
        # so we must define a dirtiness threshold
        # to start cleaning. But we don't want to interrupt
        # so if Robot is carrying a Kid, it should deliver him
        # to the corral, before start cleaning or get another
        # kid.

        if not self.RobotIsCarryingKid:
            if self.environment.Dirtiness >= 30:
                return CLEAN
            else:
                return HUNTKID
        else:
            return DELIVER

    def __moveToNextCell(self, nextPos: Tuple[int, int]):
        # Robot is moving alone
        if not self.RobotIsCarryingKid:
            # If next cell is Empty, just update it
            if self.environment[nextPos] == CellContent.Empty:
                self.environment[nextPos] = CellContent.Robot
            # If next cell is corral or is with kid or with dirt, then join robot
            # to that cell
            elif self.environment[nextPos] == CellContent.Dirt:
                self.environment[nextPos] = CellContent.RobotWithDirt
            elif self.environment[nextPos] == CellContent.Kid:
                self.environment[nextPos] = CellContent.RobotInCellWithKid
            elif self.environment[nextPos] == CellContent.Corral:
                self.environment[nextPos] = CellContent.RobotInCorral

        # Robot is moving with kid
        else:
            # If next cell is Empty, just Update it
            if self.environment[nextPos] == CellContent.Empty:
                self.environment[nextPos] = CellContent.RobotWithKid
            elif self.environment[nextPos] == CellContent.Corral:
                self.environment[nextPos] = CellContent.RobotCarryingKidInCorral

    def move(self, direction: Tuple[int, int]):
        x, y, cellType = self.RobotState
        xdir, ydir = direction
        nextCell = self.environment[x + xdir, y + ydir]
        if nextCell != CellContent.NotACell:
            self.__moveToNextCell((x + xdir, y + ydir))

            # Update the old cell
            if cellType == CellContent.Robot or cellType == CellContent.RobotWithKid:
                self.environment[x, y] = CellContent.Empty
            elif (
                cellType == CellContent.RobotCarryingKidInCorral
                or CellContent.RobotInCorral == cellType
            ):
                self.environment[x, y] = CellContent.Corral
            elif cellType == CellContent.RobotInCellWithKid:
                self.environment[x, y] = CellContent.Kid
            elif cellType == CellContent.RobotInCorralWithKid:
                self.environment[x, y] = CellContent.KidInCorral
        else:
            print("Robot cannot move in that direction")

    def carry(self):
        x, y, cellType = self.RobotState
        if cellType != CellContent.RobotInCellWithKid:
            print("No kid to carry in this cell.")
        else:
            self.environment[x, y] = CellContent.RobotWithKid
            self.position = x, y, CellContent.RobotWithKid
        return self.position

    def drop(self):
        x, y, cellType = self.RobotState
        if cellType == CellContent.RobotWithKid:
            self.environment[x, y] = CellContent.RobotInCellWithKid
            self.position = x, y, CellContent.RobotInCellWithKid
        elif cellType == CellContent.RobotCarryingKidInCorral:
            self.environment[x, y] = CellContent.RobotInCorralWithKid
            self.position = x, y, CellContent.RobotInCorralWithKid
        else:
            print("Robot is not carrying any kid.")
        return self.position

    def clean(self):
        x, y, cellType = self.RobotState
        if cellType != CellContent.RobotWithDirt:
            print("No dirt to clean.")
        else:
            self.environment[x, y] = CellContent.Robot
            self.position = x, y, CellContent.Robot
        return self.position

    def decide(self):
        action = self.__evalEnvironment()

        if action == CLEAN:
            self.__moveTowardsClosestDirt()
        elif action == HUNTKID:
            self.__moveTowardsClosestKid()
        else:
            self.__deliver()