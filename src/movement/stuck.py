import logging
from hlt.positionals import Direction
from src.common.moves import Moves
from src.common.print import print_heading, print_matrix
from src.common.matrix.functions import get_values_matrix
from src.common.values import Inequality


class Stuck(Moves):
    def __init__(self, data, prev_data):
        super().__init__(data, prev_data)

        self.move_ships()

    def move_ships(self):
        print_heading("Moving stuck ships......")

        # ## USING STUCK MATRIX
        # matrix = self.data.matrix.stuck * self.data.matrix.myShipsID
        # ship_ids = get_values_matrix(0, matrix, Inequality.GREATERTHAN)
        #
        # for ship_id in ship_ids:
        #     ship = self.data.me._ships.get(ship_id)
        #
        #     logging.debug("Ship id: {} has not enough halite to move".format(ship.id))
        #     direction = Direction.Still
        #
        #     self.move_mark_unsafe(ship, direction)

        ## THIS MIGHT BE FASTER THAN ABOVE, SINCE LOOPING THROUGH <300 SHIPS COULD BE FASTER THAN
        ## PERFORMING MATRIX MULTIPLICATION AND LOOKING FOR THE VALUES IN A 64x64 MATRIX
        ## MOVE SHIPS THAT CANNOT MOVE YET
        for ship_id in (self.data.all_ships & self.data.ships_to_move):
            ship = self.data.me._ships.get(ship_id)

            if self.data.matrix.cost[ship.position.y][ship.position.x] > ship.halite_amount:  ## NOT ENOUGH TO LEAVE
                logging.debug("Ship id: {} has not enough halite to move".format(ship.id))
                direction = Direction.Still

                self.move_mark_unsafe(ship, direction)


