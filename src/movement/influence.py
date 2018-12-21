from src.common.print import print_heading, print_matrix
from src.common.move.moves import Moves
from src.common.classes import OrderedSet
from src.common.move.explores import Explores
from src.common.move.harvests import Harvests
from src.common.values import MyConstants, Matrix_val, MoveMode, Inequality
from src.common.points import ExploreShip2
import numpy as np
import logging
import copy
import heapq

class Influence(Moves, Explores, Harvests):
    def __init__(self, data, prev_data):
        Moves.__init__(self, data, prev_data)

        self.heap_set = set()
        self.heap_dist = []

        self.taken_destinations = set()

        self.harvest_matrix = copy.deepcopy(self.data.myMatrix.halite.harvest_with_bonus)
        self.taken_matrix = np.zeros((self.data.game.game_map.height, self.data.game.game_map.width), dtype=np.int16)
        self.taken_matrix.fill(1)  ## ZERO WILL BE FOR TAKEN CELL
        r, c = np.where(self.data.myMatrix.locations.safe == Matrix_val.UNSAFE)
        self.taken_matrix[r, c] = Matrix_val.ZERO

        self.move_ships()

    def move_ships(self):
        print_heading("Moving influence ships......")

        matrixIDs = self.data.myMatrix.locations.engage_influence * self.data.myMatrix.locations.myShipsID
        r, c = np.where(matrixIDs > Matrix_val.ZERO)
        ships_engaging = OrderedSet(self.data.myMatrix.locations.myShipsID[r, c])
        ships_influencing = ships_engaging & self.data.mySets.ships_to_move

        for ship_id in ships_influencing:
            self.populate_heap(ship_id)

        while self.heap_dist:
            ## MOVE KICKED SHIPS FIRST (IF ANY)
            while self.data.mySets.ships_kicked:
                ship_kicked = self.data.mySets.ships_kicked.pop()
                if ship_kicked in self.data.mySets.ships_to_move:
                    logging.debug("Moving kicked ship ({}) for influence".format(ship_kicked))
                    #self.exploreNow(ship_kicked) ## WILL TAKE HIGHEST RATIO, PUT BACK TO HEAP
                    self.populate_heap(ship_kicked)

            s = heapq.heappop(self.heap_dist)   ## MOVE CLOSEST TO ENEMY?, TO PREVENT COLLISIONS
            logging.debug(s)                    ## EXPLORE SHIP OBJECT

            ship = self.data.game.me._ships.get(s.ship_id)
            explore_destination = self.isDestination_untaken(s)

            if s.ship_id in self.data.mySets.ships_to_move and explore_destination:
                canHarvest, harvest_direction = self.check_harvestNow(s.ship_id, moveNow=False)
                if not (canHarvest): canHarvest, harvest_direction = self.check_harvestLater(s.ship_id,
                                                                                             MyConstants.DIRECTIONS,
                                                                                             kicked=False,
                                                                                             moveNow=False)

                directions = self.get_directions_target(ship, explore_destination)
                explore_direction, points = self.best_direction(ship, directions, mode=MoveMode.EXPLORE)

                harvest_destination = self.get_destination(ship, harvest_direction)
                harvest_ratio = s.matrix_ratio[harvest_destination.y][harvest_destination.x]

                logging.debug("s.ratio {} harvest ratio {}".format(s.ratio, harvest_ratio))
                if canHarvest and -s.ratio < harvest_ratio * MyConstants.HARVEST_RATIO_TO_EXPLORE:
                    destination = harvest_destination
                    direction = harvest_direction
                else:
                    destination = explore_destination
                    direction = explore_direction

                # self.mark_unsafe(ship, explore_destination)
                self.mark_taken_udpate_top_halite(destination)
                self.move_mark_unsafe(ship, direction, points)


    def populate_heap(self, ship_id):
        """
        POPULATE HEAP BASED ON RATIO OF HARVEST WITH BONUS
        """
        if ship_id not in self.heap_set:
            self.heap_set.add(ship_id)

            ship = self.data.game.me._ships.get(ship_id)
            matrix_highest_ratio, max_ratio, destination = self.get_matrix_ratio(ship)

            logging.debug("ship id: {} max_ratio {} destination {}".format(ship_id, max_ratio, destination))
            s = ExploreShip2(max_ratio, ship.halite_amount, ship_id, destination, matrix_highest_ratio)
            heapq.heappush(self.heap_dist, s)