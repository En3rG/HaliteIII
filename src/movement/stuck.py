import logging
from hlt.positionals import Direction
from src.common.move.moves import Moves
from src.common.print import print_heading, print_matrix
from src.common.values import Inequality, Matrix_val
from src.common.move.builds import Builds
import numpy as np

class Stuck(Moves, Builds):
    def __init__(self, data, prev_data):
        Moves.__init__(self, data, prev_data)

        self.move_ships()

    def move_ships(self):
        print_heading("Moving stuck ships......")

        self.build_on_high_halite()

        ## MOVE SHIPS THAT CANNOT MOVE YET
        for ship_id in (self.data.mySets.ships_all & self.data.mySets.ships_to_move):
            ship = self.data.game.me._ships.get(ship_id)

            if self.data.myMatrix.locations.stuck[ship.position.y][ship.position.x] == Matrix_val.ONE:
                logging.debug("Ship id: {} has not enough halite to move".format(ship.id))
                self.move_mark_unsafe(ship, Direction.Still)