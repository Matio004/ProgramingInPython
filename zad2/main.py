from enum import Enum
from math import sqrt
from random import choice

MAX_ROUNDS = 50
SHEEP_COUNT = 15
SHEEP_RANGE = 10.
SHEEP_MOVE_DISTANCE = .5
WOLF_MOVE_DISTANCE = 1.

class Direction(Enum):
    NORTH = (0, 1)
    SOUTH = (0, -1)
    EAST = (1, 0)
    WEST = (-1, 0)


def dist2(pos1, pos2):
    temp = 0
    for c1, c2 in zip(pos1, pos2):
        temp += (c1 - c2) ** 2
    return temp


class Herd:
    def __init__(self, *args):
        self._herd = list(args)

    def __getitem__(self, item):
        return list(filter(lambda s: s.alive, self._herd))[item]

    def __iter__(self):
        for sheep in self._herd:
            if sheep.alive:
                yield sheep

    def __repr__(self):
        return repr(self._herd)


    def __len__(self):
        return len(self[:])


class Wolf:
    def __init__(self, pos, attack_range):
        self.pos = pos
        self.attack_range = attack_range

    def __repr__(self):
        return f'Wolf(pos={self.pos}, attack_range={self.attack_range})'

    def move(self, herd: Herd):
        target, distance = self.get_closest_sheep(herd)

        if distance <= self.attack_range:
            self.pos = target.pos
            target.alive = False
        else:
            direction = target.pos[0] - self.pos[0], target.pos[1] - self.pos[1]

            length = sqrt(direction[0] * direction[0] + direction[1] * direction[1])
            self.pos = (self.pos[0] + (direction[0] / length) * self.attack_range,
                        self.pos[1] + (direction[1] / length) * self.attack_range)

    def get_closest_sheep(self, herd: Herd) -> tuple[Sheep, float]:
        closest_sheep = herd[0]
        closest_distance = dist2(self.pos, herd[0].pos)

        for sheep in herd[1:]:
            sheep_distance = dist2(self.pos, sheep.pos)
            if sheep.alive and sheep_distance < closest_distance:
                closest_distance = sheep_distance
                closest_sheep = sheep
        return closest_sheep, sqrt(closest_distance)



class Sheep:
    def __init__(self, pos, move_distance):
        self.pos = pos
        self.move_distance = move_distance
        self.alive = True

    def __repr__(self):
        return f'Sheep(pos={self.pos}, move_distance={self.move_distance}, alive={self.alive})'

    def move(self):
        direction = choice(list(Direction)).value
        self.pos = (self.pos[0] + direction[0] * self.move_distance,
                    self.pos[1] + direction[1] * self.move_distance)


h = Herd(Sheep((1, 1,), 1), Sheep((11, 11,), 1))
w = Wolf((0, 0), 2)
print(h)
print(w)
w.move(h)
for _ in range(10):
    w.move(h)
    print(h)
    print(w)
    print()