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

"""
TO DO!!!!!!!!


ADD COLLISION PREVENTION


IF BEST IS TO STAY AND HARVEST IS 0, MUST DO SOMETHING ELSE


"""

class Harvest(Moves, Harvests, Explores):
    """
    HARVEST
    """
    def __init__(self, data, prev_data):
        Moves.__init__(self, data, prev_data)

        self.heap_set = set()
        self.heap_explore = []
        self.ships_kicked_temp = OrderedSet()

        if self.data.game.turn_number <= constants.MAX_TURNS * MyConstants.explore.enable_bonus_turns_above:
            self.harvest_matrix = copy.deepcopy(self.data.myMatrix.halite.harvest)
        else:
            self.harvest_matrix = copy.deepcopy(self.data.myMatrix.halite.harvest_with_bonus)

        self.taken_matrix = np.zeros((self.data.game.game_map.height, self.data.game.game_map.width), dtype=np.int16)
        self.taken_matrix.fill(1)                                                                                       ## ZERO WILL BE FOR TAKEN CELL
        r, c = np.where(self.data.myMatrix.locations.safe == Matrix_val.UNSAFE)
        self.taken_matrix[r, c] = Matrix_val.ZERO

        self.taken_destinations = set()

        self.move_ships()


    ## NOT RECALCULATING EXPLORE TARGETS
    def move_ships(self):
        print_heading("Moving harvesting (now) ships......")
        ## MOVE SHIPS (THAT WILL HARVEST NOW)
        for target in self.data.myLists.explore_target:
            ship_id = target.ship_id
            ship = self.data.game.me._ships.get(ship_id)

            if ship_id in self.data.mySets.ships_to_move:
                explore_destination = target.destination

                canHarvest, harvest_direction = self.check_harvestNow(ship_id, moveNow=False)

                directions = self.get_directions_target(ship, explore_destination)
                explore_direction = self.best_direction(ship, directions, mode=MoveMode.EXPLORE)

                harvest_destination = self.get_destination(ship, harvest_direction)
                harvest_ratio = target.matrix_ratio[harvest_destination.y][harvest_destination.x]

                if canHarvest and -target.ratio < harvest_ratio * self.data.myVars.harvest_ratio_to_explore:
                    destination = harvest_destination
                    direction = harvest_direction

                    self.mark_taken_udpate_top_halite(destination)
                    self.move_mark_unsafe(ship, direction)









