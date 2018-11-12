import random
from hlt.positionals import Direction, Position
from hlt.game_map import GameMap
from src.common.values import MyConstants, Matrix_val
from src.common.matrix import Section, print_matrix
import logging
import numpy as np
from src.common.movement import Moves


class MoveShips(Moves):
    def __init__(self, data, prev_data, halite_stats, command_queue):
        super().__init__(data, prev_data, halite_stats)

        self.command_queue = command_queue


    def get_moves(self):
        ## SHIPS THAT CANNOT MOVE YET
        for ship_id in (self.data.all_ships & self.data.ships_to_move):
            ship = self.data.me._ships.get(ship_id)

            if self.data.matrix.cost[ship.position.y][ship.position.x] > ship.halite_amount:  ## NOT ENOUGH TO LEAVE
                logging.debug("Ship id: {} has not enough halite to move".format(ship.id))
                direction = Direction.Still

                self.isHarvesting(direction, ship.id)
                self.move_mark_unsafe(ship, direction)


        ## SHIPS RETURNING PREVIOUSLY (HIT MAX)
        if self.prev_data:
            for ship_id in (self.prev_data.ships_returning & self.data.ships_to_move):
                ship = self.data.me._ships.get(ship_id)

                if ship and ship.position != self.data.me.shipyard.position:
                    self.returning(ship)


        ## SHIPS JUST HIT MAX
        for ship_id in (self.data.all_ships & self.data.ships_to_move):
            ship = self.data.me._ships.get(ship_id)

            if ship.is_full:
                self.returning(ship)


        ## REST OF THE SHIPS
        for ship_id in (self.data.all_ships & self.data.ships_to_move):
            ship = self.data.me._ships.get(ship_id)

            direction = self.get_highest_harvest_move(ship)
            self.isHarvesting(direction, ship.id)
            self.move_mark_unsafe(ship, direction)


        return self.command_queue


    def isHarvesting(self, direction, ship_id):
        if direction == Direction.Still:
            self.data.ships_harvesting.add(ship_id)
            logging.debug("Ship id: {} is harvesting".format(ship_id))


    def returning(self, ship):
        logging.debug("Ship id: {} is returning".format(ship.id))
        direction = self.get_direction_home(ship.position, self.data.me.shipyard.position)
        direction = self.stay_or_go(ship, direction)

        self.move_mark_unsafe(ship, direction)
        self.data.ships_returning.add(ship.id)


    def stay_or_go(self, ship, direction):
        destination = self.get_destination(ship, direction)
        if self.data.matrix.unsafe[destination.y][destination.x] == Matrix_val.UNSAFE.value:
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
        logging.debug("Getting highest harvest move for ship id: {}".format(ship.id))
        harvest = Section(self.data.matrix.harvest, ship.position, size=1)           ## SECTION OF HARVEST MATRIX
        leave_cost = self.data.matrix.cost[ship.position.y][ship.position.x]         ## COST TO LEAVE CURRENT CELL
        cost_matrix = MyConstants.DIRECT_NEIGHBORS * leave_cost                   ## APPLY COST TO DIRECT NEIGHBORS
        harvest_matrix = harvest.matrix * MyConstants.DIRECT_NEIGHBORS_SELF
        actual_harvest = harvest_matrix - cost_matrix
        unsafe = Section(self.data.matrix.unsafe, ship.position, size=1)
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

