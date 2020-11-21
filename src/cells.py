from enum import Enum
from typing import Optional, Union
from children import Child

from robots import Robot


class CellState(Enum):
    Empty = 0
    Ocupied = 1


class Cell:
    """
    This is the basic unit in the environment. A cell can either be occupied
    or empty. If the cell is ocupied, then it can have an obstacle, dirt, a child or
    a robot.
    """

    def __init__(self):
        self.state: CellState = CellState.Empty
        self.content = None

    def __str__(self) -> str:
        if self.state == CellState.Empty:
            return "_"
        if isinstance(self.content, Robot):
            return "R"
        if isinstance(self.content, Child):
            return "X"
        if self.content == "corral":
            return "C"
        if self.content == "dirty":
            return "D"
        if self.content == "obstacle":
            return "O"
        return ""

    def __repr__(self) -> str:
        return str(self)

    def setCellContentChild(self, child):
        self.state = CellState.Ocupied
        self.content = child

    def setCellContentDirt(self, dirt):
        self.state = CellState.Ocupied
        self.content = dirt

    def setCellContentRobot(self, robot):
        self.state = CellState.Ocupied
        self.content = robot

    def setCellContentObstacle(self, obstacle):
        self.state = CellState.Ocupied
        self.content = obstacle

    def setCellContentCorral(self):
        self.state = CellState.Ocupied
        self.content = "corral"

    def cleanCell(self):
        self.state = CellState.Empty
        self.content = None