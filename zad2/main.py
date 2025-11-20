from enum import Enum
from math import sqrt
from random import choice, uniform

import json
import csv

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
    def __init__(self, herd):
        self._herd = herd

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

    def __bool__(self):
        return len(self) != 0

    @property
    def positions(self):
        return [sheep.pos for sheep in self._herd]


class Wolf:
    def __init__(self, pos, move_distance):
        self.pos = pos
        self.move_distance = move_distance

    def __repr__(self):
        return f'Wolf(pos={self.pos}, move_distance={self.move_distance})'

    def __str__(self):
        return f'Wolf(x={self.pos[0]:.3f}, y={self.pos[1]:.3f})'

    def move(self, herd: Herd) -> Sheep:
        target, distance = self.get_closest_sheep(herd)

        if distance <= self.move_distance:
            self.pos = target._pos
            target.alive = False
        else:
            direction = target._pos[0] - self.pos[0], target._pos[1] - self.pos[1]

            length = sqrt(direction[0] * direction[0] + direction[1] * direction[1])
            self.pos = (self.pos[0] + (direction[0] / length) * self.move_distance,
                        self.pos[1] + (direction[1] / length) * self.move_distance)
        return target

    def get_closest_sheep(self, herd: Herd) -> tuple[Sheep, float]:
        closest_sheep = herd[0]
        closest_distance = dist2(self.pos, herd[0].pos)

        for sheep in herd[1:]:
            sheep_distance = dist2(self.pos, sheep._pos)
            if sheep.alive and sheep_distance < closest_distance:
                closest_distance = sheep_distance
                closest_sheep = sheep
        return closest_sheep, sqrt(closest_distance)



class Sheep:
    def __init__(self, index, pos, move_distance):
        self.index = index
        self._pos = pos
        self.move_distance = move_distance
        self.alive = True

    def __repr__(self):
        return f'Sheep(pos={self._pos}, move_distance={self.move_distance}, alive={self.alive})'

    def move(self):
        direction = choice(list(Direction)).value
        self._pos = (self._pos[0] + direction[0] * self.move_distance,
                     self._pos[1] + direction[1] * self.move_distance)

    @property
    def pos(self):
        return self._pos if self.alive else None


if __name__ == '__main__':
    sheep_list = [Sheep(i, (uniform(-SHEEP_RANGE, SHEEP_RANGE),
                            uniform(-SHEEP_RANGE, SHEEP_RANGE)), SHEEP_MOVE_DISTANCE) for i in range(SHEEP_COUNT)]
    herd = Herd(sheep_list)
    wolf = Wolf((0, 0), 2)

    json_list = []
    counts_alive_sheep = []

    for r in range(MAX_ROUNDS):
        for sheep in herd:
            sheep.move()
        wolfs_target = wolf.move(herd)

        print('Round', r)
        print(wolf)
        print('Alive sheep:', len(herd))
        if wolfs_target.alive:
            print(f'Wolf is chasing sheep {wolfs_target.index}')
        else:
            print(f'Wolf has eaten sheep {wolfs_target.index}')
        print()
        json_list.append({
            'round_no': r,
            'wolf_pos': wolf.pos,
            'sheep_pos': herd.positions
        })
        counts_alive_sheep.append(len(herd))
        if not herd:
            break
    with open('pos.json', 'w') as file:
        json.dump(json_list, file, indent=4)

    with open('alive.csv', 'w') as file:
        csv_writer = csv.writer(file, lineterminator='\n')
        csv_writer.writerows(enumerate(counts_alive_sheep))