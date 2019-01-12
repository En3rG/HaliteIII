import logging
import heapq
from src.common.move.moves import Moves
from src.common.move.deposits import Deposits
from src.common.move.explores import Explores
from src.common.print import print_heading
from src.movement.collision_prevention import move_kicked_ship
from src.common.points import FarthestShip, DepositPoints, ExploreShip
from src.common.values import MoveMode, Matrix_val, Inequality, MyConstants
from src.common.matrix.functions import get_coord_closest, pad_around, Section
from src.common.astar import a_star, get_goal_in_section
from hlt.positionals import Direction
from src.common.matrix.functions import get_coord_closest, count_manhattan
from hlt.positionals import Position
from hlt import constants
import copy
import numpy as np


class Deposit(Moves, Deposits, Explores):
    def __init__(self, data, prev_data):
        Moves.__init__(self, data, prev_data)

        self.move_ships()

    def move_ships(self):
        print_heading("Moving depositing ships......")

        for id in self.data.mySets.deposit_ships:
            while self.data.mySets.ships_kicked:
                ship_kicked = self.data.mySets.ships_kicked.pop()
                logging.debug("Moving kicked ship ({}) by a depositing ship".format(ship_kicked))
                ship = self.data.game.me._ships.get(ship_kicked)
                if ship.id in self.data.mySets.ships_to_move: self.data.mySets.ships_to_move.remove(ship.id)

                move_kicked_ship(self, ship)

            ship = self.data.game.me._ships.get(id)
            s = self.data.myDicts.deposit_ship[id]

            if ship.id in self.data.mySets.ships_to_move:
                self.data.mySets.ships_to_move.remove(ship.id)
                self.depositNow(ship, s.dock_position, s.directions, harvest=True)
            #self.depositNow(ship, s.dock_position, s.directions)






