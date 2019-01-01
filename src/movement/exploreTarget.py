from src.common.move.moves import Moves
from src.common.move.harvests import Harvests
from src.common.print import print_heading
from src.common.orderedSet import OrderedSet
from src.common.values import MyConstants
from src.common.points import ExploreShip
from src.common.values import MoveMode, Matrix_val
from src.common.move.explores import Explores
from hlt import constants
import heapq
import logging
import copy
import numpy as np


class Target():
    def __init__(self, ratio, ship_id, destination, matrix_ratio):
        self.ratio = ratio
        self.ship_id = ship_id
        self.destination = destination
        self.matrix_ratio = matrix_ratio

class ExploreTarget(Moves, Harvests, Explores):
    def __init__(self, data, prev_data):
        Moves.__init__(self, data, prev_data)

        self.heap_set = set()
        self.heap_explore = []
        self.ships_kicked_temp = OrderedSet()

        if self.data.game.turn_number <= constants.MAX_TURNS * MyConstants.EXPLORE_ENABLE_WITH_BONUS_TURNS_ABOVE:
            self.harvest_matrix = copy.deepcopy(self.data.myMatrix.halite.harvest)
            #self.harvest_matrix = self.data.myMatrix.halite.updated_harvest
        else:
            self.harvest_matrix = copy.deepcopy(self.data.myMatrix.halite.harvest_with_bonus)
            #self.harvest_matrix = self.data.myMatrix.halite.updated_harvest_with_bonus

        self.taken_matrix = np.zeros((self.data.game.game_map.height, self.data.game.game_map.width), dtype=np.int16)
        self.taken_matrix.fill(1)                                                                                       ## ZERO WILL BE FOR TAKEN CELL
        r, c = np.where(self.data.myMatrix.locations.safe == Matrix_val.UNSAFE)
        self.taken_matrix[r, c] = Matrix_val.ZERO

        self.taken_destinations = set()

        self.move_ships()


    def move_ships(self):
        print_heading("Populate Explore targets......")
        for ship_id in (self.data.mySets.ships_all & self.data.mySets.ships_to_move):
            self.populate_heap(ship_id)

        while self.heap_explore:
            s = heapq.heappop(self.heap_explore)
            logging.debug(s)

            ## OLD WAY (MARK TAKEN)
            explore_destination = self.isDestination_untaken(s)
            ## NEW WAY
            #explore_destination = self.isDestination_updated(s)

            if s.ship_id in self.data.mySets.ships_to_move and explore_destination:
                self.data.myDicts.explore_ship.setdefault(s.ship_id, None)
                self.data.myDicts.explore_ship[s.ship_id] = s
                self.data.myLists.explore_target.append(Target(s.ratio, s.ship_id, s.destination, s.matrix_ratio))

                ## OLD WAY (MARK TAKEN)
                self.mark_taken_udpate_top_halite(explore_destination)
                ## NEW WAY (DEDUCT HALITE TO BE HARVESTED)
                #self.update_harvest_matrix(s.ship_id, explore_destination)


    def populate_heap(self, ship_id):
        if ship_id not in self.heap_set:
            self.heap_set.add(ship_id)

            ship = self.data.game.me._ships.get(ship_id)
            matrix_highest_ratio, max_ratio, destination, harvest_value = self.get_matrix_ratio(ship)
            s = ExploreShip(max_ratio, ship.halite_amount, ship_id, destination, harvest_value, matrix_highest_ratio)
            heapq.heappush(self.heap_explore, s)








