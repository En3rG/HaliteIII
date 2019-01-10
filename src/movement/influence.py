from src.common.print import print_heading, print_matrix
from src.common.move.moves import Moves
from src.common.orderedSet import OrderedSet
from src.common.move.explores import Explores
from src.common.move.harvests import Harvests
from src.common.values import MyConstants, Matrix_val, MoveMode, Inequality
from src.common.astar import a_star, get_goal_in_section
from src.common.points import ExploreShip
from src.common.matrix.functions import get_coord_closest, pad_around, Section
from hlt.positionals import Position
from hlt.positionals import Direction
import numpy as np
import logging
import copy
import heapq

class Influence(Moves, Explores, Harvests):
    def __init__(self, data, prev_data):
        Moves.__init__(self, data, prev_data)

        self.heap_set = set()
        self.heap_explore = []

        self.taken_destinations = set()

        self.harvest_matrix = copy.deepcopy(self.data.myMatrix.halite.harvest_with_bonus)
        self.taken_matrix = np.zeros((self.data.game.game_map.height, self.data.game.game_map.width), dtype=np.int16)
        self.taken_matrix.fill(1)                                                                                       ## ZERO WILL BE FOR TAKEN CELL
        r, c = np.where(self.data.myMatrix.locations.safe == Matrix_val.UNSAFE)
        self.taken_matrix[r, c] = Matrix_val.ZERO

        self.move_ships()

    def move_ships(self):
        print_heading("Moving influence ships......")

        matrixIDs = self.data.myMatrix.locations.engage_influence * self.data.myMatrix.locations.myShipsID
        r, c = np.where(matrixIDs > Matrix_val.ZERO)
        ships_engaging = OrderedSet(self.data.myMatrix.locations.myShipsID[r, c])
        ships_influenced = ships_engaging & self.data.mySets.ships_to_move

        for ship_id in sorted(ships_influenced):
            self.populate_heap(ship_id)

        while self.heap_explore:
            ## MOVE KICKED SHIPS FIRST (IF ANY)
            while self.data.mySets.ships_kicked:
                ship_kicked = self.data.mySets.ships_kicked.pop()
                if ship_kicked in self.data.mySets.ships_to_move:
                    logging.debug("Moving kicked ship ({}) for influence".format(ship_kicked))
                    #self.exploreNow(ship_kicked) ## WILL TAKE HIGHEST RATIO, PUT BACK TO HEAP
                    self.populate_heap(ship_kicked)

            s = heapq.heappop(self.heap_explore)                                                                        ## MOVE CLOSEST TO ENEMY?, TO PREVENT COLLISIONS
            logging.debug(s)                                                                                            ## EXPLORE SHIP OBJECT

            ship = self.data.game.me._ships.get(s.ship_id)
            explore_destination = self.isDestination_untaken(s)

            if s.ship_id in self.data.mySets.ships_to_move and explore_destination:
                canHarvest, harvest_direction = self.check_harvestNow(s.ship_id, moveNow=False)
                if not (canHarvest): canHarvest, harvest_direction = self.check_harvestLater(s.ship_id,
                                                                                             MyConstants.DIRECTIONS,
                                                                                             kicked=False,
                                                                                             moveNow=False)

                directions = self.get_directions_target(ship, explore_destination)
                ## OLD WAY
                explore_direction = self.best_direction(ship, directions, mode=MoveMode.EXPLORE)
                ## A STAR WAY (TIMED OUT)
                #explore_direction = self.get_Astar_direction(ship, explore_destination, directions)

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
                self.move_mark_unsafe(ship, direction)


    def get_Astar_direction(self, ship, target_position, directions):
        ## PATH IS 1 LESS, SINCE WILL BE PADDED
        # section_enemy = Section(self.data.myMatrix.locations.potential_enemy_collisions, ship.position,
        #                         MyConstants.RETREAT_SEARCH_PERIMETER - 1)
        # section_ally = Section(self.data.myMatrix.locations.safe, ship.position,
        #                        MyConstants.RETREAT_SEARCH_PERIMETER - 1)
        # section = section_enemy.matrix + section_ally.matrix
        # matrix_path = pad_around(section)
        section = Section(self.data.myMatrix.locations.potential_enemy_collisions, ship.position,
                          MyConstants.DEPOSIT_SEARCH_PERIMETER - 1)
        matrix_path = pad_around(section.matrix)
        section = Section(self.data.myMatrix.halite.amount, ship.position, MyConstants.DEPOSIT_SEARCH_PERIMETER)
        matrix_cost = section.matrix
        goal_position = get_goal_in_section(matrix_path, section.center, ship.position, target_position, directions)
        path = a_star(matrix_path, matrix_cost, section.center, goal_position, lowest_cost=False)

        if len(path) == 1:
            direction = Direction.Still
        elif len(path) > 1:
            start_coord = path[-1]
            next_coord = path[-2]
            start = Position(start_coord[1], start_coord[0])
            destination = Position(next_coord[1], next_coord[0])
            directions = self.get_directions_start_target(start, destination)
            direction = self.best_direction(ship, directions, mode=MoveMode.EXPLORE)
        else:
            direction = self.best_direction(ship, directions, mode=MoveMode.EXPLORE)

        return direction


    def populate_heap(self, ship_id):
        """
        POPULATE HEAP BASED ON RATIO OF HARVEST WITH BONUS
        """
        if ship_id not in self.heap_set:
            self.heap_set.add(ship_id)

            ship = self.data.game.me._ships.get(ship_id)
            matrix_highest_ratio, max_ratio, destination, harvest_value = self.get_matrix_ratio(ship)

            s = ExploreShip(max_ratio, ship.halite_amount, ship_id, destination, harvest_value, matrix_highest_ratio)
            heapq.heappush(self.heap_explore, s)