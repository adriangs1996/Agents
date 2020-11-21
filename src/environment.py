from typing import List, Tuple
from cells import Cell, CellState
from random import randint
from robots import Robot


def around(coord: Tuple[int, int]):
    x, y = coord
    return [
        (x + 1, y),
        (x - 1, y),
        (x, y + 1),
        (x, y - 1),
        (x + 1, y + 1),
        (x - 1, y + 1),
        (x + 1, y - 1),
        (x - 1, y - 1),
    ]


class Environment:
    def __init__(
        self,
        N: int,
        M: int,
        dirty: int,
        obstacles: int,
        children: int,
        time: int,
    ):
        self.area: List[List[Cell]] = [[Cell() for _ in range(N)] for _ in range(M)]
        self.time = time
        self.dirtyness = dirty
        self.childs = children
        self._obstacles = obstacles

        self.robotPosition = (-1, -1)
        self._h = N
        self._w = M

        self._initializeEnvironment()

    def __str__(self) -> str:
        result = ""
        for row in self.area:
            result += " ".join(str(x) for x in row) + "\n"
        return result

    def countEmpty(self):
        return sum(
            [1 for row in self.area for cell in row if cell.state == CellState.Empty]
        )

    def _initializeEnvironment(self):
        # First set the robot
        x, y = randint(self._h, self._w), randint(self._h, self._w)
        # This always succed because area is currently empty
        robot = Robot()
        self.area[x][y].setCellContentRobot(robot)
        self.robotPosition = x, y

        # Compute necesary value since all are given in percentages
        totalCells = self._h * self._w
        obstacle = self._obstacles * totalCells // 100
        dirt = self.dirtyness * totalCells // 100

        # Place the corral
        self._createCorral()
        # Place dirty
        self._createObstacles(obstacle)
        self._createDirty(dirt)

    def _createCorral(self):
        x, y = randint(self._h, self._w), randint(self._h, self._w)
        while (x, y) == self.robotPosition:
            x, y = randint(self._h, self._w), randint(self._h, self._w)

        # Traverse grid in BFS
        queue: List[Tuple[int, int]] = [(x, y)]
        count = self.childs

        while queue and count:
            count -= 1
            nextPos = queue.pop(0)
            x, y = nextPos
            self.area[x][y].setCellContentCorral()
            for x, y in around(nextPos):
                try:
                    if self.area[x][y].state == CellState.Empty:
                        queue.append((x, y))
                except IndexError:
                    pass

        if count:
            raise Exception("Cannot create corral.")

    def _createObstacles(self, dirty):
        if self.countEmpty() < dirty:
            raise Exception(f"Cannot put {dirty} dirty cells.")
        count = dirty
        while count:
            x, y = randint(self._h, self._w), randint(self._h, self._w)
            if self.area[x][y].state == CellState.Empty:
                count -= 1
                self.area[x][y].setCellContentObstacle("obstacle")

    def _createDirty(self, dirty):
        if self.countEmpty() < dirty:
            raise Exception(f"Cannot put {dirty} dirty cells.")
        count = dirty
        while count:
            x, y = randint(self._h, self._w), randint(self._h, self._w)
            if self.area[x][y].state == CellState.Empty:
                count -= 1
                self.area[x][y].setCellContentDirt("dirty")
