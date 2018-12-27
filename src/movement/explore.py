from src.common.move.moves import Moves
from src.common.move.explores import Explores
from src.common.move.harvests import Harvests
from src.common.values import MoveMode, MyConstants, Matrix_val, Inequality
import logging
from src.common.print import print_heading, print_matrix
from src.common.points import ExploreShip, ExplorePoints
from src.common.astar import a_star, get_goal_in_section
from src.common.matrix.functions import get_coord_closest, get_n_closest_masked, populate_manhattan, \
    get_coord_max_closest, pad_around, Section
from hlt.positionals import Position
from hlt import constants
import heapq
import copy
import numpy as np



"""
TO DO!!!!!!!!!!!

SHOULD NOT HARVEST WHEN THERE IS A MUCH BIGGER HALITE CLOSE BY
WHEN EXPLORE TARGET RATIO IS MORE THAN 3X THAN RATIO OF CURRENT HARVEST, DO NOT HARVEST NOW/LATER


"""

class Explore(Moves, Explores, Harvests):
    def __init__(self, data, prev_data):
        Moves.__init__(self, data, prev_data)

        self.heap_set = set()  ## USED TO NOT HAVE DUPLICATE SHIP IDs IN THE HEAP DIST
        self.heap_explore = []
        self.top_halite = copy.deepcopy(self.data.myMatrix.halite.top_amount)

        self.taken_destinations = set()
        if self.data.game.turn_number <= constants.MAX_TURNS * MyConstants.EXPLORE_ENABLE_WITH_BONUS_TURNS_ABOVE:
            self.harvest_matrix = copy.deepcopy(self.data.myMatrix.halite.harvest)
        else:
            self.harvest_matrix = copy.deepcopy(self.data.myMatrix.halite.harvest_with_bonus)                           ## WORST THAN JUST DOING HARVEST

        self.taken_matrix = np.zeros((self.data.game.game_map.height, self.data.game.game_map.width), dtype=np.int16)
        self.taken_matrix.fill(1)                                                                                       ## ZERO WILL BE FOR TAKEN CELL
        r, c = np.where(self.data.myMatrix.locations.safe == Matrix_val.UNSAFE)
        self.taken_matrix[r, c] = Matrix_val.ZERO

        self.move_ships()


    def move_ships(self):
        print_heading("Moving exploring ships......")

        ## MOVE REST OF THE SHIPS TO EXPLORE USING HEAP FIRST
        ships = (self.data.mySets.ships_all & self.data.mySets.ships_to_move)                                           ## SAVING SINCE ships_to_move WILL BE UPDATED DURING ITERATION
        for ship_id in ships:
            ## DOUBLE CHECK SHIP IS STILL IN SHIPS TO MOVE
            if ship_id in self.data.mySets.ships_to_move:
                self.populate_heap(ship_id)


        while self.heap_explore:
            ## MOVE KICKED SHIPS FIRST (IF ANY)
            while self.data.mySets.ships_kicked:
                ship_kicked = self.data.mySets.ships_kicked.pop()
                if ship_kicked in self.data.mySets.ships_to_move:
                    logging.debug("Moving kicked ship ({}) for explore".format(ship_kicked))
                    #self.exploreNow(ship_kicked) ## WILL TAKE HIGHEST RATIO, EVEN WHEN VERY FAR
                    self.populate_heap(ship_kicked)

            s = heapq.heappop(self.heap_explore)                                                                        ## MOVE CLOSEST SHIPS FIRST, TO PREVENT COLLISIONS
            logging.debug(s)                                                                                            ## EXPLORE SHIP OBJECT

            ship = self.data.game.me._ships.get(s.ship_id)
            explore_destination = self.isDestination_untaken(s)

            if s.ship_id in self.data.mySets.ships_to_move and explore_destination:
                canHarvest, harvest_direction = self.check_harvestNow(s.ship_id, moveNow=False)
                if not(canHarvest): canHarvest, harvest_direction = self.check_harvestLater(s.ship_id,
                                                                                            MyConstants.DIRECTIONS,
                                                                                            kicked=False,
                                                                                            moveNow=False)

                directions = self.get_directions_target(ship, explore_destination)
                ## OLD WAY
                explore_direction = self.best_direction(ship, directions, mode=MoveMode.EXPLORE)
                ## USING ASTAR
                #explore_direction = self.get_a_star_direction(ship, explore_destination, directions)

                harvest_destination = self.get_destination(ship, harvest_direction)
                harvest_ratio = s.matrix_ratio[harvest_destination.y][harvest_destination.x]

                if canHarvest and -s.ratio < harvest_ratio * MyConstants.HARVEST_RATIO_TO_EXPLORE:
                    destination = harvest_destination
                    direction = harvest_direction
                else:
                    destination = explore_destination
                    direction = explore_direction

                logging.debug("explore_destination {} -s.ratio {} harvest_destination {} harvest_ratio {}".format(explore_destination, -s.ratio, harvest_destination, harvest_ratio))
                # self.mark_unsafe(ship, explore_destination)
                self.mark_taken_udpate_top_halite(destination)
                self.move_mark_unsafe(ship, direction)


    def get_a_star_direction(self, ship, target_position, directions):
        ## PATH IS 1 LESS, SINCE WILL BE PADDED
        section = Section(self.data.myMatrix.locations.potential_enemy_collisions, ship.position, MyConstants.EXPLORE_SEARCH_PERIMETER - 1)
        matrix_path = pad_around(section.matrix)
        section = Section(self.data.myMatrix.halite.amount, ship.position, MyConstants.EXPLORE_SEARCH_PERIMETER)
        matrix_cost = section.matrix
        goal_position = get_goal_in_section(matrix_path, section.center, ship.position, target_position, directions)
        path = a_star(matrix_path, matrix_cost, section.center, goal_position, lowest_cost=False)

        logging.debug("path: {}".format(path))
        if len(path) > 1:
            start_coord = path[-1]
            next_coord = path[-2]
            start = Position(start_coord[1], start_coord[0])
            destination = Position(next_coord[1], next_coord[0])
            directions = self.get_directions_start_target(start, destination)
            direction = self.best_direction(ship, directions, mode=MoveMode.EXPLORE,
                                            avoid_enemy=True, avoid_potential_enemy=True)
        else:
            direction = self.best_direction(ship, directions, mode=MoveMode.EXPLORE,
                                            avoid_enemy=True, avoid_potential_enemy=False)

        return direction


    def populate_heap(self, ship_id):
        ## FOR CLOSEST TOP HARVEST PER TURN
        if ship_id not in self.heap_set:
            self.heap_set.add(ship_id)

            ship = self.data.game.me._ships.get(ship_id)
            matrix_highest_ratio, max_ratio, destination = self.get_matrix_ratio(ship)
            s = ExploreShip(max_ratio, ship.halite_amount, ship_id, destination, matrix_highest_ratio)
            heapq.heappush(self.heap_explore, s)





