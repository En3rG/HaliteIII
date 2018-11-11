import logging
import random
from hlt.game_map import GameMap
from hlt.positionals import Position
from hlt.positionals import Direction
import abc

class Moves(abc.ABC):
    def __init__(self, data, prev_data):
        self.data = data
        self.prev_data = prev_data
        self.me = data.me
        self.game_map = data.game_map
        self.matrix = data.matrix


    def move_mark_unsafe(self, ship, direction):
        destination = self.get_destination(ship, direction)
        self.data.mark_unsafe(destination)

        logging.debug("Ship id: {} moving from {} to {}".format(ship.id, ship.position, destination))
        self.command_queue.append(ship.move(direction))

        self.data.ships_moved.add(ship.id)


    def get_direction_home(self, ship_position, home_position):

        choices = GameMap._get_target_direction(ship_position, home_position)   ## WILL GIVE LONGER PATH, IF WRAPPING
        clean_choices = [x for x in choices if x != None]                       ## CAN HAVE A NONE
        logging.debug("ship position: {} shipyard position: {} clean_choices: {}".format(ship_position,
                                                                                         home_position,
                                                                                         clean_choices))
        try: direction = random.choice(clean_choices)
        except: direction = Direction.Still
        logging.debug("chosen direction: {}".format(direction))

        return direction


    def get_destination(self, ship, direction):
        """
        GIVEN A SHIP AND DIRECTION, GET NORMALIZED (WRAP) POSITION

        :param ship:
        :param direction:
        :return: NORMALIZED POSITION
        """
        new_pos = ship.position + Position(direction[0], direction[1])
        x = new_pos.x % self.data.map_width
        y = new_pos.y % self.data.map_height
        return Position(x, y)