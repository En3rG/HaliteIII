
import random
from hlt.positionals import Direction, Position
from hlt.game_map import GameMap
from src.common.values import Constants
from src.common.matrix import Section, print_matrix
import logging
import numpy as np


class Move():
    def __init__(self, data):
        self.data = data
        self.me = data.me
        self.game_map = data.game_map
        self.matrix = data.matrix

    def get_moves(self):
        command_queue = []

        for ship in self.me.get_ships():
            if ship.is_full:
                choices = GameMap._get_target_direction(ship.position, self.me.shipyard.position) ## CAN HAVE A NONE
                clean_choices = [x for x in choices if x != None]
                command_queue.append(ship.move(random.choice(clean_choices)))
            else:
                str_move = self.get_highest_harvest_move(ship)
                command_queue.append(str_move)

        return command_queue


    def get_highest_harvest_move(self, ship):
        """
        ACTUAL HARVEST MATRIX IS THE NEIGHBORING HARVEST VALUE MINUS LEAVING CURRENT CELL

        :param ship:
        :param harvest:
        :param cost:
        :return:
        """
        harvest = Section(self.matrix.harvest, ship.position, size=1)           ## SECTION OF HARVEST MATRIX
        leave_cost = self.matrix.cost[ship.position.y][ship.position.x]         ## COST TO LEAVE CURRENT CELL
        cost_matrix = Constants.DIRECT_NEIGHBORS * leave_cost                   ## APPLY COST TO DIRECT NEIGHBORS
        harvest_matrix = harvest.matrix * Constants.DIRECT_NEIGHBORS_SELF
        actual_harvest = harvest_matrix - cost_matrix
        unsafe = Section(self.matrix.unsafe, ship.position, size=1)
        safe_harvest = actual_harvest * unsafe.matrix

        max_index = np.unravel_index(np.argmax(safe_harvest, axis=None), safe_harvest.shape)

        if max_index == (0,1):
            new_position = ship.position + Position(Direction.North[0], Direction.North[1])
            self.data.mark_unsafe(new_position)

            logging.debug("Ship id: {} moving to {}".format(ship.id, new_position))
            return ship.move(Direction.North)
        elif max_index == (1, 2):
            new_position = ship.position + Position(Direction.East[0], Direction.East[1])
            self.data.mark_unsafe(new_position)

            logging.debug("Ship id: {} moving to {}".format(ship.id, new_position))
            return ship.move(Direction.East)
        elif max_index == (2, 1):
            new_position = ship.position + Position(Direction.South[0], Direction.South[1])
            self.data.mark_unsafe(new_position)

            logging.debug("Ship id: {} moving to {}".format(ship.id, new_position))
            return ship.move(Direction.South)
        elif max_index == (1, 0):
            new_position = ship.position + Position(Direction.West[0], Direction.West[1])
            self.data.mark_unsafe(new_position)

            logging.debug("Ship id: {} moving to {}".format(ship.id, new_position))
            return ship.move(Direction.West)
        else:
            new_position = ship.position
            self.data.mark_unsafe(new_position)

            logging.debug("Ship id: {} moving to {}".format(ship.id, new_position))
            return ship.stay_still()

