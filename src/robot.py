from enum import Enum
from typing import List, Tuple
from .environment import around, Environment, CellContent
from math import inf

CLEAN = "Clean"
HUNTKID = "Hunt"
DELIVER = "Deliver"


class Action(Enum):
    Clean = 0
    Hunt = 1
    Deliver = 2


class Robot:
    def __init__(self, environment: Environment) -> None:
        self.environment = environment
        self.__clean_forever = False

    @property
    def RobotState(self):
        return self.environment.Robot

    @property
    def RobotIsCarryingKid(self):
        _, _, robot = self.RobotState
        return robot in (
            CellContent.RobotWithKid,
            CellContent.RobotCarryingKidInCorral,
            CellContent.RobotWithKidInDirt,
        )

    def __deliver(self, count=2):
        if count == 0:
            return
        x, y, _ = self.RobotState
        _, d, path = self.__getDistanceToGoal((x, y), CellContent.Corral)
        if d == inf:
            self.__clean_forever = True
            self.drop()
        elif d == 0:
            self.drop()
        else:
            xdir, ydir = path[0][0] - x, path[0][1] - y
            self.move((xdir, ydir))
            self.__deliver(count - 1)

    def __moveTowardsClosestDirt(self):
        x, y, _ = self.RobotState
        _, d, path = self.__getDistanceToGoal((x, y), CellContent.Dirt)
        if d == inf:
            pass
        elif d == 0:
            self.clean()
            self.__clean_forever = False
        else:
            xdir, ydir = path[0][0] - x, path[0][1] - y
            self.move((xdir, ydir))

    def __moveTowardsClosestKid(self):
        x, y, _ = self.RobotState
        _, d, path = self.__getDistanceToGoal((x, y), CellContent.Kid)
        if d == inf:
            self.__clean_forever = True
        elif d == 1:
            xdir, ydir = path[0][0] - x, path[0][1] - y
            self.move((xdir, ydir))
            self.carry()
        else:
            xdir, ydir = path[0][0] - x, path[0][1] - y

            self.move((xdir, ydir))

    def __getDistanceToGoal(
        self, origin: Tuple[int, int], goal: CellContent
    ):
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

        visited = {}

        while queue:
            pos, d, path = queue.pop(0)
            visited[pos] = True
            if self.environment[pos] in target:
                return pos, d, path
            for nextPos in around(pos):
                # If carrying
                if self.RobotIsCarryingKid:
                    if (
                        self.environment[nextPos]
                        in (
                            CellContent.Empty,
                            CellContent.Corral,
                            CellContent.Dirt,
                        )
                        and not visited.get(nextPos, False)
                    ):
                        queue.append((nextPos, d + 1, path + [nextPos]))
                else:
                    if self.environment[nextPos] in (
                        CellContent.Empty,
                        CellContent.Corral,
                        CellContent.Dirt,
                        CellContent.KidInCorral,
                        CellContent.Kid,
                        CellContent.RobotWithDirt,
                    ) and not visited.get(nextPos, False):
                        queue.append((nextPos, d + 1, path + [nextPos]))
        return origin, inf, []

    def __evalEnvironment(self):
        # Robot should prioritize not to get fired
        # so we must define a dirtiness threshold
        # to start cleaning. But we don't want to interrupt
        # so if Robot is carrying a Kid, it should deliver him
        # to the corral, before start cleaning or get another
        # kid.

        if not self.RobotIsCarryingKid:
            if (
                self.environment.Dirtiness >= 40
                or len(self.environment.Kids) == 0
                or self.__clean_forever
            ):
                return Action.Clean
            else:
                return Action.Hunt
        else:
            return Action.Deliver

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
            elif self.environment[nextPos] == CellContent.KidInCorral:
                self.environment[nextPos] = CellContent.RobotInCorralWithKid

        # Robot is moving with kid
        else:
            # If next cell is Empty, just Update it
            if self.environment[nextPos] == CellContent.Empty:
                self.environment[nextPos] = CellContent.RobotWithKid
            elif self.environment[nextPos] == CellContent.Corral:
                self.environment[nextPos] = CellContent.RobotCarryingKidInCorral
            elif self.environment[nextPos] == CellContent.Dirt:
                self.environment[nextPos] = CellContent.RobotWithKidInDirt

    def move(self, direction: Tuple[int, int]):
        x, y, cellType = self.RobotState
        xdir, ydir = direction
        if (xdir, ydir) == (0, 0):
            return
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
            elif cellType == CellContent.RobotWithDirt:
                self.environment[x, y] = CellContent.Dirt
            elif self.environment[x, y] == CellContent.RobotWithKidInDirt:
                self.environment[x, y] = CellContent.Dirt
        

    def carry(self):
        x, y, cellType = self.RobotState
        if cellType != CellContent.RobotInCellWithKid:
            pass
        else:
            self.environment[x, y] = CellContent.RobotWithKid

    def drop(self):
        x, y, cellType = self.RobotState
        if cellType == CellContent.RobotWithKid:
            self.environment[x, y] = CellContent.RobotInCellWithKid
        elif cellType == CellContent.RobotCarryingKidInCorral:
            self.environment[x, y] = CellContent.RobotInCorralWithKid
        else:
            pass

    def clean(self):
        x, y, cellType = self.RobotState
        if cellType != CellContent.RobotWithDirt:
            pass
        else:
            self.environment[x, y] = CellContent.Robot

    def decide(self):
        action = self.__evalEnvironment()

        if action == Action.Clean:
            self.__moveTowardsClosestDirt()
        elif action == Action.Hunt:
            self.__moveTowardsClosestKid()
        else:
            self.__deliver()