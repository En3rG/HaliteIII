import logging
from hlt.positionals import Direction
from src.common.moves import Moves
from src.common.print import print_heading, print_matrix
from src.common.values import Inequality, Matrix_val
import numpy as np

class Stuck(Moves):
    def __init__(self, data, prev_data):
        super().__init__(data, prev_data)

        self.move_ships()

    def move_ships(self):
        print_heading("Moving stuck ships......")

        ## MOVE SHIPS THAT CANNOT MOVE YET
        for ship_id in (self.data.mySets.ships_all & self.data.mySets.ships_to_move):
            ship = self.data.game.me._ships.get(ship_id)

            #if self.data.myMatrix.halite.cost[ship.position.y][ship.position.x] > ship.halite_amount:  ## NOT ENOUGH TO LEAVE
            if self.data.myMatrix.locations.stuck[ship.position.y][ship.position.x] == Matrix_val.ONE:
                logging.debug("Ship id: {} has not enough halite to move".format(ship.id))
                direction = Direction.Still

                self.move_mark_unsafe(ship, direction)


        ## USING NP.WHERE
        ## PROBLEM IS AFTER RETREATING, STILL TRIES TO MOVE STUCK SHIP, WHICH WAS HANDLED IN RETREAT
        # r, c = np.where(self.data.myMatrix.locations.stuck == Matrix_val.ONE)
        # ship_ids = self.data.myMatrix.locations.myShipsID[r, c]
        #
        # for ship_id in ship_ids:
        #     ship = self.data.game.me._ships.get(ship_id)
        #
        #     logging.debug("Ship id: {} has not enough halite to move".format(ship.id))
        #     direction = Direction.Still
        #
        #     self.move_mark_unsafe(ship, direction)