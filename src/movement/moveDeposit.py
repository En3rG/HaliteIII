import logging
import heapq
from src.common.move.moves import Moves
from src.common.move.deposits import Deposits
from src.common.move.explores import Explores
from src.common.print import print_heading
from src.movement.collision_prevention import avoid_collision_direction
from src.common.points import FarthestShip, DepositPoints, ExploreShip
from src.common.values import MoveMode, Matrix_val, Inequality, MyConstants
from hlt.positionals import Direction
from src.common.matrix.functions import get_coord_closest, count_manhattan
from hlt.positionals import Position
from hlt import constants
import copy
import numpy as np


class MoveDeposit(Moves, Deposits, Explores):
    def __init__(self, data, prev_data):
        Moves.__init__(self, data, prev_data)

        self.move_ships()

    def move_ships(self):
        print_heading("Moving depositing ships......")

        for s in self.data.myLists.deposit_ships:
            while self.data.mySets.ships_kicked:
                ship_kicked = self.data.mySets.ships_kicked.pop()
                logging.debug("Moving kicked ship ({}) by a depositing ship".format(ship_kicked))
                ship = self.data.game.me._ships.get(ship_kicked)

                self.move_kicked_ship(ship)

            ship = self.data.game.me._ships.get(s.ship_id)
            self.depositNow(ship, s.dock_position, s.directions)


    def move_kicked_ship(self, ship):
        """
        GO TOWARDS EXPLORE TARGET FIRST
        IT THAT IS NOT SAFE, GO ANYWHERE SAFE
        """
        direction = avoid_collision_direction(self, ship, directions=None)
        self.move_mark_unsafe(ship, direction)
