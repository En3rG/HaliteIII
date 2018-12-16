from src.common.move.moves import Moves
from src.common.move.explores import Explores
from src.common.values import MoveMode, MyConstants, Matrix_val, Inequality
import logging
from src.common.print import print_heading, print_matrix
from hlt import constants
import heapq
import copy
import numpy as np



"""
TO DO!!!!!!!!!!!

TOP HALITE DOESNT CONSIDER INFLUENCE


"""

class Explore(Moves, Explores):
    def __init__(self, data, prev_data):
        Moves.__init__(self, data, prev_data)

        self.heap_set = set()  ## USED TO NOT HAVE DUPLICATE SHIP IDs IN THE HEAP DIST
        self.heap_dist = []
        self.top_halite = copy.deepcopy(self.data.myMatrix.halite.top_amount)
        self.taken_destinations = set()

        if self.data.game.turn_number <= constants.MAX_TURNS * MyConstants.EXPLORE_ENABLE_WITH_BONUS_TURNS_ABOVE:
            self.harvest_matrix = copy.deepcopy(self.data.myMatrix.halite.harvest)
        else:
            self.harvest_matrix = copy.deepcopy(self.data.myMatrix.halite.harvest_with_bonus)  ## WORST THAN JUST DOING HARVEST


        self.taken_matrix = np.zeros((self.data.game.game_map.height, self.data.game.game_map.width), dtype=np.int16)
        self.taken_matrix.fill(1)  ## ZERO WILL BE FOR TAKEN CELL
        ## MARK TAKEN CELLS AS TAKEN (FROM HARVEST, RETREAT, DEPOSIT, ETC)
        ## DOESNT SEEM TO BE BETTER, SINCE NOT SENDING BACKUPS/SUPPORT FOR ATTACK
        # r, c = np.where(self.data.myMatrix.locations.safe == Matrix_val.UNSAFE)
        # self.taken_matrix[r, c] = Matrix_val.ZERO

        self.move_ships()


    def move_ships(self):
        print_heading("Moving exploring ships......")

        ## MOVE REST OF THE SHIPS TO EXPLORE
        ## MOVE KICKED SHIPS FIRST
        # ships = (self.data.mySets.ships_all & self.data.mySets.ships_to_move)  ## SAVING SINCE ships_to_move WILL BE UPDATED DURING ITERATION
        # for ship_id in ships:
        #     ## MOVE KICKED SHIPS FIRST (IF ANY)
        #     while self.data.mySets.ships_kicked:
        #         ship_kicked = self.data.mySets.ships_kicked.pop()
        #         logging.debug("Moving kicked ship ({}) for explore".format(ship_kicked))
        #         self.exploreNow(ship_kicked)
        #
        #     ## DOUBLE CHECK SHIP IS STILL IN SHIPS TO MOVE
        #     if ship_id in self.data.mySets.ships_to_move:
        #         self.exploreNow(ship_id)


        ## MOVE REST OF THE SHIPS TO EXPLORE USING HEAP FIRST
        ships = (self.data.mySets.ships_all & self.data.mySets.ships_to_move)  ## SAVING SINCE ships_to_move WILL BE UPDATED DURING ITERATION
        for ship_id in ships:
            ## DOUBLE CHECK SHIP IS STILL IN SHIPS TO MOVE
            if ship_id in self.data.mySets.ships_to_move:
                self.populate_heap(ship_id)


        ## JUST GETS CLOSEST TOP AMOUNT HALITE
        # while self.heap_dist:
        #     s = heapq.heappop(self.heap_dist)   ## MOVE CLOSEST SHIPS FIRST, TO PREVENT COLLISIONS
        #     logging.debug(s)                    ## EXPLORE SHIP OBJECT
        #
        #     ship = self.data.game.me._ships.get(s.ship_id)
        #     directions = self.get_directions_target(ship, s.destination)
        #     direction = self.best_direction(ship, directions, mode=MoveMode.EXPLORE)
        #     self.move_mark_unsafe(ship, direction)


        while self.heap_dist:
            ## MOVE KICKED SHIPS FIRST (IF ANY)
            while self.data.mySets.ships_kicked:
                ship_kicked = self.data.mySets.ships_kicked.pop()
                if ship_kicked in self.data.mySets.ships_to_move:
                    logging.debug("Moving kicked ship ({}) for explore".format(ship_kicked))
                    self.exploreNow(ship_kicked)

            s = heapq.heappop(self.heap_dist)                       ## MOVE CLOSEST SHIPS FIRST, TO PREVENT COLLISIONS
            logging.debug(s)                                        ## EXPLORE SHIP OBJECT

            if s.ship_id in self.data.mySets.ships_to_move:
                ship = self.data.game.me._ships.get(s.ship_id)

                destination = self.get_untaken_destination(s)

                if destination:
                    directions = self.get_directions_target(ship, destination)
                    direction, points = self.best_direction(ship, directions, mode=MoveMode.EXPLORE)
                    self.mark_taken_udpate_top_halite(destination)
                    self.move_mark_unsafe(ship, direction, points)


