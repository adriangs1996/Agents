from typing import Tuple
from environment import around, Environment, CellContent


LEFT = 0, -1
RIGHT = 0, 1
UP = -1, 0
DOWN = 1, 0
UPRIGHT = -1, 1
UPLEFT = -1, -1
DOWNLEFT = 1, -1
DOWNRIGHT = 1, 1


class Robot:
    def __init__(self, environment: Environment) -> None:
        self.environment = environment

    def _moveToNextCell(self, currentCell: CellContent, nextPos: Tuple[int, int]):
        # Robot is moving alone
        if (
            currentCell == CellContent.Robot
            or currentCell == CellContent.RobotInCellWithKid
            or currentCell == CellContent.RobotInCorralWithKid
            or CellContent.RobotWithDirt == currentCell
            or CellContent.RobotInCorral == currentCell
        ):
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
        elif (
            currentCell == CellContent.RobotWithKid
            or currentCell == CellContent.RobotCarryingKidInCorral
        ):
            # If next cell is Empty, just Update it
            if self.environment[nextPos] == CellContent.Empty:
                self.environment[nextPos] = CellContent.RobotWithKid
            elif self.environment[nextPos] == CellContent.Corral:
                self.environment[nextPos] = CellContent.RobotCarryingKidInCorral

    def move(self, direction: Tuple[int, int]):
        x, y, cellType = self.environment.Robot
        xdir, ydir = direction
        nextCell = self.environment[x + xdir, y + ydir]
        if nextCell != CellContent.NotACell:
            self._moveToNextCell(cellType, (x + xdir, y + ydir))

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
        x, y, cellType = self.position
        if cellType != CellContent.RobotInCellWithKid:
            print("No kid to carry in this cell.")
        else:
            self.environment[x, y] = CellContent.RobotWithKid
            self.position = x, y, CellContent.RobotWithKid
        return self.position

    def drop(self):
        x, y, cellType = self.position
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
        x, y, cellType = self.position
        if cellType != CellContent.RobotWithDirt:
            print("No dirt to clean.")
        else:
            self.environment[x, y] = CellContent.Robot
            self.position = x, y, CellContent.Robot
        return self.position
