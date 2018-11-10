
import random
from hlt.positionals import Direction, Position
from hlt.game_map import GameMap
from src.common.values import Constants, Matrix_val
from src.common.matrix import Section, print_matrix
import logging
import numpy as np


class Move():
    def __init__(self, data, prev_data):
        self.data = data
        self.prev_data = prev_data
        self.me = data.me
        self.game_map = data.game_map
        self.matrix = data.matrix
        self.command_queue = []


    def get_moves(self):

        for ship in self.me.get_ships():
            if self.matrix.cost[ship.position.y][ship.position.x] > ship.halite_amount:  ## NOT ENOUGH TO LEAVE
                logging.debug("Ship id: {} has not enough halite to move".format(ship.id))
                direction = Direction.Still

                self.isHarvesting(direction, ship.id)
                self.move_mark_unsafe(ship, direction)

        if self.prev_data:
            for id in self.prev_data.ships_returning:
                ship = self.me._ships.get(id)

                if ship and ship.position != self.me.shipyard.position:
                    self.returning(ship)

        for ship in self.me.get_ships():
            if ship.id in self.data.ships_moved:
                continue  ## GO TO THE NEXT FOR LOOP

            elif ship.is_full:
                self.returning(ship)

        for ship in self.me.get_ships():
            if ship.id in self.data.ships_moved:
                continue ## GO TO THE NEXT FOR LOOP
            else:
                direction = self.get_highest_harvest_move(ship)

            self.isHarvesting(direction, ship.id)
            self.move_mark_unsafe(ship, direction)

        return self.command_queue


    def isHarvesting(self, direction, ship_id):
        if direction == Direction.Still:
            self.data.ships_harvesting.add(ship_id)


    def move_mark_unsafe(self, ship, direction):
        new_position = ship.position + Position(direction[0], direction[1])
        self.data.mark_unsafe(new_position)

        logging.debug("Ship id: {} moving from {} to {}".format(ship.id, ship.position, new_position))
        self.command_queue.append(ship.move(direction))

        self.data.ships_moved.add(ship.id)


    def returning(self, ship):
        logging.debug("Ship id: {} is returning".format(ship.id))
        choices = GameMap._get_target_direction(ship.position, self.me.shipyard.position)  ## CAN HAVE A NONE
        clean_choices = [x for x in choices if x != None]
        logging.debug("ship position: {} shipyard position: {} clean_choices: {}".format(ship.position,
                                                                                         self.me.shipyard.position,
                                                                                         clean_choices))
        direction = random.choice(clean_choices)
        logging.debug("chose direction: {}".format(direction))

        direction = self.safeDirection(ship, direction)

        self.move_mark_unsafe(ship, direction)
        self.data.ships_returning.add(ship.id)


    def safeDirection(self, ship, direction):
        new_pos = ship.position + Position(direction[0], direction[1])
        x = new_pos.x % self.data.map_width
        y = new_pos.y % self.data.map_height
        verified_pos = Position(x, y)
        if self.matrix.unsafe[verified_pos.y][verified_pos.x] == Matrix_val.UNSAFE.value:
            return Direction.Still
        else:
            return direction


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
            return Direction.North

        elif max_index == (1, 2):
            return Direction.East

        elif max_index == (2, 1):
            return Direction.South

        elif max_index == (1, 0):
            return Direction.West
        else:
            return Direction.Still

