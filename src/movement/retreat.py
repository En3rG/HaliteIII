import logging
from hlt import constants
from src.common.move.moves import Moves
from src.common.move.retreats import Retreats
from src.common.values import MoveMode, MyConstants, Matrix_val, Inequality
from src.common.points import FarthestShip, RetreatPoints
from src.common.print import print_heading


"""
TO DO!!!!!!!!!!!

IMPROVE MOVEMENT WHEN THERE ARE TONS OF SHIPS TRYING TO GO TO THE DOCK


"""

class Retreat(Moves, Retreats):
    def __init__(self, data, prev_data):
        Moves.__init__(self, data, prev_data)

        self.turns_left = constants.MAX_TURNS - data.game.turn_number
        self.heap_dist = []
        self.farthest_ship = FarthestShip(0, 0, 0, None)

        self.check_retreat()


    def check_retreat(self):
        """
        POPULATE HEAP BASED ON DISTANCE FROM SHIPYARD/DOCKS
        CHECK IF WE NEED TO START RETREATING BACK
        """
        print_heading("Check retreat......")

        self.populate_heap()

        logging.debug("Farthest ship is {}, with {} turns left".format(self.farthest_ship, self.turns_left))

        if self.farthest_ship.distance + MyConstants.RETREAT_EXTRA_TURNS > self.turns_left:
            self.move_ships()







