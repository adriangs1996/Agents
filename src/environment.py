from enum import Enum
from typing import List, Tuple
from random import choice, randint, sample


def around(pos: Tuple[int, int]) -> List[Tuple[int, int]]:
    x, y = pos
    return [
        (x + 1, y),
        (x + 1, y - 1),
        (x + 1, y + 1),
        (x, y + 1),
        (x, y - 1),
        (x - 1, y),
        (x - 1, y + 1),
        (x - 1, y - 1),
    ]


def kidAround(pos: Tuple[int, int]) -> List[Tuple[int, int]]:
    x, y = pos
    return [
        (x + 1, y),
        (x, y + 1),
        (x, y - 1),
        (x - 1, y),
    ]


class CellContent(Enum):
    Empty = 0
    Kid = 1
    Robot = 2
    Dirt = 3
    Obstacle = 4
    Corral = 5
    KidInCorral = 6
    RobotWithKid = 7
    NotACell = 8
    RobotWithDirt = 9
    RobotInCellWithKid = 10
    RobotInCorralWithKid = 11
    RobotCarryingKidInCorral = 12
    RobotInCorral = 13
    RobotWithKidInDirt = 14


TOSTR = {
    CellContent.Empty: "___",
    CellContent.Kid: "_K_",
    CellContent.Robot: "_R_",
    CellContent.Dirt: "_D_",
    CellContent.Obstacle: "_O_",
    CellContent.Corral: "_C_",
    CellContent.KidInCorral: "KC_",
    CellContent.RobotWithKid: "RK_",
    CellContent.RobotWithDirt: "RD_",
    CellContent.RobotInCellWithKid: "R&K",
    CellContent.RobotInCorralWithKid: "RCK",
    CellContent.RobotCarryingKidInCorral: "RKC",
    CellContent.RobotInCorral: "RC_",
    CellContent.RobotWithKidInDirt: "RKD",
}


class Environment:
    def __init__(
        self,
        N: int,
        M: int,
        dirtinessPercent: int,
        obstaclesPercent: int,
        kids: int,
        timeToChange: int,
    ):
        # Create an empty area
        self.area: List[List[CellContent]] = [
            [CellContent.Empty for _ in range(M)] for _ in range(N)
        ]

        # Place robot
        x, y = randint(0, N - 1), randint(0, M - 1)
        self[x, y] = CellContent.Robot

        self.totalArea = N * M
        self.t = timeToChange

        # Place corral first because it need to be in connected form
        self.__generateCorral(kids, N, M)

        # Place kids
        self.__initCellContent(kids, CellContent.Kid, N, M)

        # Compute amount of dirt needed

        obstacles = obstaclesPercent * self.EmptyCells // 100

        # Place obstacles
        self.__initCellContent(obstacles, CellContent.Obstacle, N, M)

        # Place dirty cells
        dirtiness = dirtinessPercent * self.EmptyCells // 100
        self.__initCellContent(dirtiness, CellContent.Dirt, N, M)

    def __getitem__(self, coords: Tuple[int, int]):
        x, y = coords
        try:
            if x < 0 or y < 0:
                raise IndexError
            return self.area[x][y]
        except IndexError:
            return CellContent.NotACell

    def __setitem__(self, coords: Tuple[int, int], val: CellContent):
        x, y = coords
        assert x >= 0 and y >= 0
        self.area[x][y] = val

    def __str__(self) -> str:
        result = ""
        for row in self.area:
            result += " ".join(TOSTR[x] for x in row) + "\n"
        return result

    # PROPERTIES

    @property
    def Kids(self):
        return [
            (x, y)
            for x, row in enumerate(self.area)
            for y, cell in enumerate(row)
            if cell == CellContent.Kid or cell == CellContent.RobotInCellWithKid
        ]

    @property
    def Obstacles(self):
        return [
            (x, y)
            for x, row in enumerate(self.area)
            for y, cell in enumerate(row)
            if cell == CellContent.Obstacle
        ]

    @property
    def Dirt(self):
        return [
            (x, y, cell)
            for x, row in enumerate(self.area)
            for y, cell in enumerate(row)
            if cell == CellContent.Dirt
            or cell == CellContent.RobotWithDirt
            or cell == CellContent.RobotWithKidInDirt
        ]

    @property
    def Robot(self) -> Tuple[int, int, CellContent]:
        try:
            return next(
                (x, y, cell)
                for x, row in enumerate(self.area)
                for y, cell in enumerate(row)
                if cell == CellContent.Robot
                or cell == CellContent.RobotWithKid
                or cell == CellContent.RobotInCellWithKid
                or cell == CellContent.RobotInCorralWithKid
                or cell == CellContent.RobotCarryingKidInCorral
                or cell == CellContent.RobotInCorral
                or cell == CellContent.RobotWithDirt
                or cell == CellContent.RobotWithKidInDirt
            )
        except StopIteration:
            exit()

    @property
    def Dirtiness(self):
        total = len(self.Dirt) + self.EmptyCells
        return len(self.Dirt) * 100 // total

    @property
    def EmptyCells(self):
        return sum(1 for row in self.area for cell in row if cell == CellContent.Empty)

    @property
    def IsClean(self):
        return self.Dirtiness < 60

    @property
    def JobDone(self):
        dirtiness = len(self.Dirt)
        kids = len(self.Kids)

        return kids == 0 and dirtiness == 0

    # PRIVATE METHODS

    def __initCellContent(self, count: int, cellType: CellContent, n: int, m: int):
        if self.EmptyCells < count:
            raise Exception(f"Cannot place {count} {cellType}")

        while count:
            x, y = randint(0, n - 1), randint(0, m - 1)
            if self[x, y] == CellContent.Empty:
                count -= 1
                self[x, y] = cellType
            elif self[x, y] == CellContent.Corral and cellType == CellContent.Kid:
                count -= 1
                self[x, y] = CellContent.KidInCorral

    def __generateCorral(self, count: int, n: int, m: int):
        x, y = randint(0, n - 1), randint(0, m - 1)
        while self[x, y] != CellContent.Empty:
            x, y = randint(0, n - 1), randint(0, m - 1)

        queue: List[Tuple[int, int]] = [(x, y)]

        while count and queue:
            x, y = queue.pop(0)
            count -= 1
            self[x, y] = CellContent.Corral
            for i, j in kidAround((x, y)):
                if self[i, j] == CellContent.Empty:
                    queue.append((i, j))

        if count:
            raise Exception("Not enough room for corral.")

    def __moveObstacleFrom(self, pos1: Tuple[int, int], currentPos: Tuple[int, int]):
        xdir, ydir = currentPos[0] - pos1[0], currentPos[1] - pos1[1]
        x, y = currentPos
        nextPos = x + xdir, y + ydir

        # Base Case, put obstacle in next position
        if self[nextPos] == CellContent.Empty:
            self[nextPos] = CellContent.Obstacle
            return

        # If obstacle was pushed by a kid, then free that cell
        if self[pos1] == CellContent.Kid or CellContent.RobotInCellWithKid:
            self[currentPos] = CellContent.Empty

        self.__moveObstacleFrom(currentPos, (x + xdir, y + ydir))

    def __canMoveObstacleFrom(self, pushedFrom: Tuple[int, int], pos: Tuple[int, int]):
        x1, y1 = pushedFrom
        x, y = pos
        # Compute the direction vector (arrow - origin)
        xdir, ydir = x - x1, y - y1

        if self[x + xdir, y + ydir] == CellContent.Empty:
            return True
        elif self[x + xdir, y + ydir] == CellContent.Obstacle:
            return self.__canMoveObstacleFrom(pos, (x + xdir, y + ydir))
        else:
            return False

    def __canMoveKidTo(self, kidPos: Tuple[int, int]):
        positions = [kidPos]
        for pos in kidAround(kidPos):
            if self[pos] == CellContent.Empty:
                positions.append(pos)
            elif self[pos] == CellContent.Obstacle and self.__canMoveObstacleFrom(
                kidPos, pos
            ):
                positions.append(pos)
        return positions

    def _playKid(self, kidPos: Tuple[int, int]):
        positions = self.__canMoveKidTo(kidPos)
        nextPos = choice(positions)

        if nextPos != kidPos:
            # Kid's gonna move
            if self[nextPos] == CellContent.Empty:
                self[nextPos] = CellContent.Kid
                if self[kidPos] == CellContent.RobotInCellWithKid:
                    self[kidPos] = CellContent.Robot
                else:
                    self[kidPos] = CellContent.Empty
            elif self[nextPos] == CellContent.Obstacle:
                self.__moveObstacleFrom(kidPos, nextPos)
                self[nextPos] = CellContent.Kid
                if self[kidPos] == CellContent.RobotInCellWithKid:
                    self[kidPos] = CellContent.Robot
                else:
                    self[kidPos] = CellContent.Empty

        return nextPos

    def __generateGarbage(self, center: Tuple[int, int]):
        square = around(center)
        kidsInSquare = len(list(filter(lambda kid: kid in square, self.Kids)))

        if kidsInSquare == 1:
            dirtiness = randint(0, 1)
        elif kidsInSquare == 2:
            dirtiness = randint(0, 3)
        else:
            dirtiness = randint(0, 6)

        available = [cell for cell in square if self[cell] == CellContent.Empty]

        for cell in sample(available, min(dirtiness, len(available))):
            self[cell] = CellContent.Dirt

    # PUBLIC METHODS

    def naturalChange(self):
        for kid in self.Kids:
            newKidPos = self._playKid(kid)
            if newKidPos != kid:
                self.__generateGarbage(kid)

    def randomChange(
        self, N: int, M: int, dirtinessPercent: int, obstaclesPercent: int, kids: int
    ):
        self.area = [[CellContent.Empty for _ in range(M)] for _ in range(N)]

        # Place robot
        x, y = randint(0, N - 1), randint(0, M - 1)
        self[x, y] = CellContent.Robot

        self.totalArea = N * M

        # Place corral first because it need to be in connected form
        self.__generateCorral(kids, N, M)

        # Place kids
        self.__initCellContent(kids, CellContent.Kid, N, M)

        # Place obstacles
        obstacles = obstaclesPercent * self.EmptyCells // 100
        self.__initCellContent(obstacles, CellContent.Obstacle, N, M)

        # Place dirty cells
        # Compute amount of dirt needed
        dirtiness = dirtinessPercent * self.EmptyCells // 100
        self.__initCellContent(dirtiness, CellContent.Dirt, N, M)
