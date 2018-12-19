
from src.common.print import print_heading
from src.common.move.moves import Moves
from src.common.values import MoveMode, MyConstants, Matrix_val
from src.common.move.harvests import Harvests
from src.common.move.explores import Explores
from src.common.points import ExploreShip, ExploreShip2, ExplorePoints
from hlt import constants
import copy
import numpy as np
import heapq
import logging

"""
TO DO!!!!!!!!!!!


"""

class Start(Moves, Harvests, Explores):
    def __init__(self, data, prev_data):
        Moves.__init__(self, data, prev_data)

        self.heap_set = set()  ## USED TO NOT HAVE DUPLICATE SHIP IDs IN THE HEAP DIST
        self.heap_dist = []

        self.taken_destinations = set()

        if self.data.game.turn_number <= constants.MAX_TURNS * MyConstants.EXPLORE_ENABLE_WITH_BONUS_TURNS_ABOVE:
            self.harvest_matrix = copy.deepcopy(self.data.myMatrix.halite.harvest)
        else:
            self.harvest_matrix = copy.deepcopy(
                self.data.myMatrix.halite.harvest_with_bonus)  ## WORST THAN JUST DOING HARVEST

        self.taken_matrix = np.zeros((self.data.game.game_map.height, self.data.game.game_map.width), dtype=np.int16)
        self.taken_matrix.fill(1)  ## ZERO WILL BE FOR TAKEN CELL
        r, c = np.where(self.data.myMatrix.locations.safe == Matrix_val.UNSAFE)
        self.taken_matrix[r, c] = Matrix_val.ZERO

        self.move_ships()

    def move_ships(self):
        print_heading("Moving start moves......")

        ships = (self.data.mySets.ships_all & self.data.mySets.ships_to_move)
        for ship_id in ships:
            self.populate_heap(ship_id)

        if self.data.game.turn_number <= 6:  ## SHIPS SHOULD MOVE OUT ON TURNS 2, 3, 4, 5, 6

            while self.heap_dist:
                ## MOVE KICKED SHIPS FIRST (IF ANY)
                while self.data.mySets.ships_kicked:
                    ship_kicked = self.data.mySets.ships_kicked.pop()
                    if ship_kicked in self.data.mySets.ships_to_move:
                        logging.debug("Moving kicked ship ({}) for start".format(ship_kicked))
                        #self.exploreNow(ship_kicked)
                        self.populate_heap(ship_kicked)

                s = heapq.heappop(self.heap_dist)  ## MOVE CLOSEST SHIPS FIRST, TO PREVENT COLLISIONS
                logging.debug(s)  ## EXPLORE SHIP OBJECT

                ship = self.data.game.me._ships.get(s.ship_id)
                explore_destination = self.isDestination_untaken(s)

                if s.ship_id in self.data.mySets.ships_to_move and explore_destination:
                    ## CHECK IF CAN HARVEST NOW/LATER
                    canHarvest, harvest_direction = self.check_harvestNow(s.ship_id, moveNow=False)
                    if not (canHarvest): canHarvest, harvest_direction = self.check_harvestLater(s.ship_id,
                                                                                                 MyConstants.DIRECTIONS,
                                                                                                 kicked=False,
                                                                                                 moveNow=False)

                    directions = self.get_directions_target(ship, explore_destination)
                    explore_direction, points = self.best_direction(ship, directions, mode=MoveMode.EXPLORE)

                    harvest_destination = self.get_destination(ship, harvest_direction)
                    harvest_ratio = s.matrix_ratio[harvest_destination.y][harvest_destination.x]

                    ## CHECK WHETHER IT'LL HARVEST OR EXPLORE
                    if s.ratio < harvest_ratio * MyConstants.HARVEST_RATIO_TO_EXPLORE:
                        destination = harvest_destination
                        direction = harvest_direction
                    else:
                        destination = explore_destination
                        direction = explore_direction

                    self.mark_taken_udpate_top_halite(destination)
                    self.move_mark_unsafe(ship, direction, points)


    def populate_heap(self, ship_id):
        if ship_id not in self.heap_set:
            self.heap_set.add(ship_id)

            ship = self.data.game.me._ships.get(ship_id)
            matrix_highest_ratio, max_ratio, destination = self.get_matrix_ratio(ship)
            s = ExploreShip2(-max_ratio, ship_id, destination, matrix_highest_ratio)
            heapq.heappush(self.heap_dist, s)

