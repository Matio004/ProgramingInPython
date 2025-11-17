import logging
import os.path
import sys
from argparse import ArgumentParser
from configparser import ConfigParser
from enum import Enum
from math import sqrt
from random import choice, uniform

import json
import csv

logger = logging.getLogger(__name__)  #TODO INFO LOGGING

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
        logger.debug('Wolf determined the closest sheep: Sheep(id=%d, distance=%f)', target.index, distance)
        logger.info('Wolf moved')

        if distance <= self.move_distance:
            self.pos = target.pos
            target.alive = False
            logger.info('Wolf has eaten sheep #%d', target.index)
        else:
            direction = target.pos[0] - self.pos[0], target.pos[1] - self.pos[1]

            length = sqrt(direction[0] * direction[0] + direction[1] * direction[1])
            self.pos = (self.pos[0] + (direction[0] / length) * self.move_distance,
                        self.pos[1] + (direction[1] / length) * self.move_distance)
            logger.info('Wolf is chasing sheep #%d', target.index)
        logger.debug('Wolf moved to pos=(%f, %f))', *self.pos)
        return target

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
    def __init__(self, index, pos, move_distance):
        self.index = index
        self._pos = pos
        self.move_distance = move_distance
        self.alive = True

        logger.debug('Sheep #%d initialized (pos=(%f, %f))', self.index, *self._pos)

    def __repr__(self):
        return f'Sheep(pos={self._pos}, move_distance={self.move_distance}, alive={self.alive})'

    def move(self):
        direction = choice(list(Direction))
        direction_tuple = direction.value
        logger.debug('Sheep #%d has chosen to move to the %s', self.index, direction.name)  # todo zapyać czy może byc samo direction
        self._pos = (self._pos[0] + direction_tuple[0] * self.move_distance,
                     self._pos[1] + direction_tuple[1] * self.move_distance)
        logger.debug('Sheep #%d moved to pos=(%f, %f))', self.index, *self._pos)

    @property
    def pos(self):
        return self._pos if self.alive else None


if __name__ == '__main__':
    arg_parser = ArgumentParser("Chase")
    arg_parser.add_argument('-c', '--config', type=str)
    arg_parser.add_argument('-l', '--log', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
    arg_parser.add_argument('-r', '--rounds', type=int)
    arg_parser.add_argument('-s', '--sheep', type=int)
    arg_parser.add_argument('-w', '--wait', action='store_true')
    namespace = arg_parser.parse_args(sys.argv[1:])

    logging.basicConfig(filename='chase.log', level=namespace.log)

    config = ConfigParser()
    if namespace.config:
        if os.path.exists(namespace.config):
            config.read(namespace.config)

            SHEEP_RANGE = float(config['Sheep']['InitPosLimit'])
            SHEEP_MOVE_DISTANCE = float(config['Sheep']['MoveDist'])

            WOLF_MOVE_DISTANCE = float(config['Wolf']['MoveDist'])

            if SHEEP_RANGE <= 0:
                raise ValueError('Initial position of sheep must by positive number.')
            if SHEEP_MOVE_DISTANCE <= 0:
                raise ValueError('Distance of sheep movement must by positive number.')
            if WOLF_MOVE_DISTANCE <= 0:
                raise ValueError('Distance of sheep movement must by positive number.')

            logger.debug(
                'Config file loaded. SheepInitPosLimit: %f, SheepMoveDist: %f, WolfMoveDist: %f',
                SHEEP_RANGE, SHEEP_MOVE_DISTANCE, WOLF_MOVE_DISTANCE
            )

    if namespace.rounds is not None:
        if namespace.rounds <= 0:
            raise ValueError("Maximum number of rounds should be an integer greater than zero.")
        MAX_ROUNDS = namespace.rounds

    if namespace.sheep is not None:
        if namespace.sheep <= 0:
            raise ValueError("Maximum number of sheep should be an integer greater than zero.")
        SHEEP_COUNT = namespace.sheep

    sheep_list = [Sheep(i, (uniform(-SHEEP_RANGE, SHEEP_RANGE),
                            uniform(-SHEEP_RANGE, SHEEP_RANGE)), SHEEP_MOVE_DISTANCE) for i in range(SHEEP_COUNT)]
    logger.info('Initial position of all sheep determined')  # todo zapytać czy to może być przed
    herd = Herd(sheep_list)
    wolf = Wolf((0, 0), WOLF_MOVE_DISTANCE)

    json_list = []
    counts_alive_sheep = []

    for r in range(MAX_ROUNDS):
        logger.info('Round #%d started', r)
        print('Round', r)

        for sheep in herd:
            sheep.move()
        logger.info('All alive sheep moved')
        wolfs_target = wolf.move(herd)

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
        logger.info('Alive sheep at the end of round #%d: %d', r, len(herd))
        counts_alive_sheep.append(len(herd))
        if not herd:
            logger.info('Simulation terminated, cause: all sheep eaten')
            break
        if namespace.wait:
            input()
    else:
        logger.info('Simulation terminated, cause: predefined maximum number of rounds has been reached')
    with open('pos.json', 'w') as file:
        json.dump(json_list, file, indent=4)
    logger.debug('Information saved to pos.json')

    with open('alive.csv', 'w') as file:
        csv_writer = csv.writer(file, lineterminator='\n')
        csv_writer.writerows(enumerate(counts_alive_sheep))
    logger.debug('Information saved to alive.csv')