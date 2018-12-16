from src.common.matrix.functions import get_coord_closest, get_n_closest_masked, populate_manhattan, get_coord_max_closest
from hlt.positionals import Direction
from src.common.points import ExploreShip, ExploreShip2, ExplorePoints
from hlt.positionals import Position
from src.common.values import MoveMode, MyConstants, Matrix_val, Inequality
import heapq
import numpy as np
import logging
from collections import deque

class Explores():
    def exploreNow(self, ship_id):
        """
        SHIP IS EXPLORING, PERFORM NECESSARY STEPS
        """
        ship = self.data.game.me._ships.get(ship_id)

        ## GET DIRECTION TO HIGHEST NEIGHBOR
        # direction = self.get_highest_harvest_move(ship)


        ## GET DIRECTION TO HIGHEST SECTION
        # destination = get_position_highest_section(self.data)
        # directions = self.get_directions_target(ship, destination)
        # direction = self.best_direction(ship, directions, mode=MoveMode.EXPLORE)
        # self.move_mark_unsafe(ship, direction)


        ## GET DIRECTION TO CLOSEST TOP HALITE
        # curr_cell = (ship.position.y, ship.position.x)
        # seek_val = Matrix_val.ZERO
        # coord, min_di, val = get_coord_closest(seek_val,
        #                                        self.data.myMatrix.halite.top_amount,
        #                                        self.data.init_data.myMatrix.distances.cell[curr_cell],
        #                                        Inequality.GREATERTHAN)
        # destination = Position(coord[1], coord[0])
        # directions = self.get_directions_target(ship, destination)
        # direction = self.best_direction(ship, directions, mode=MoveMode.EXPLORE)
        # self.move_mark_unsafe(ship, direction)


        ## GET DIRECTION TO CLOSEST TOP HARVEST PER TURN
        curr_cell = (ship.position.y, ship.position.x)
        distance_matrix = self.data.init_data.myMatrix.distances.cell[curr_cell]
        matrix_highest_ratio = self.get_highest_harvest(ship, curr_cell)
        max_ratio, coord = get_coord_max_closest(matrix_highest_ratio, distance_matrix)
        destination = Position(coord[1], coord[0])
        directions = self.get_directions_target(ship, destination)
        direction, points = self.best_direction(ship, directions, mode=MoveMode.EXPLORE)
        self.move_mark_unsafe(ship, direction, points)

    def get_untaken_destination(self, s):
        ## SAVING SORTED DISTANCES
        ## TIMING OUT (SORTING A BUNCH IS MUCH SLOWER THAN GETTING CLOSEST MAX MULTIPLE TIMES???)
        # if (s.destination.y, s.destination.x) in self.taken_destinations:
        #
        #     found_good_destination = False
        #
        #     while s.indices_deque:
        #         closest_ind = s.indices_deque.popleft()
        #         closest_dist = s.distances_deque.popleft()
        #         destination = Position(closest_ind[0], closest_ind[1])  ## INDICES ARE IN (y, x) FORMAT
        #
        #         if (destination.y, destination.x) not in self.taken_destinations:
        #             found_good_destination = True
        #             s.distance = closest_dist
        #             s.destination = destination
        #             heapq.heappush(self.heap_dist, s)
        #             break
        #
        #     if not(found_good_destination):
        #         ## NEED TO REPOPULATE HEAP
        #         self.heap_set.remove(s.ship_id)
        #         self.populate_heap(s.ship_id)
        #
        #     return None
        # else:
        #     return s.destination


        ## RECALCULATING TOP HALITE
        ## MUCH FASTER THAN ABOVE!
        if (s.destination.y, s.destination.x) in self.taken_destinations:
            self.heap_set.remove(s.ship_id)
            self.populate_heap(s.ship_id)

            return None
        else:
            return s.destination

    def mark_taken_udpate_top_halite(self, destination):
        """
        MARKING DESTINATION TAKEN AND REMOVING DESTINATION FROM TOP HALITE, FOR FUTURE CALCULATIONS
        """
        self.taken_destinations.add((destination.y, destination.x))
        self.top_halite[destination.y][destination.x] = Matrix_val.ZERO

        ## FOR HIGHEST HARVEST PER TURN RATIO
        self.taken_matrix[destination.y][destination.x] = Matrix_val.ZERO
        ## BY ONLY TAKING OUT ONE CELL, CAUSES A TRAFFIC JAM
        ## WHEN A BIG BULK OF TOP RATIO IS ALL TOGETHER (SAY 30 CELLS)
        ## THEN 30 SHIPS WILL BE SENT TO HERE (CAUSING BIG TRAFFIC JAM)
        # populate_manhattan(self.taken_matrix,
        #                    Matrix_val.ZERO,
        #                    destination,
        #                    MyConstants.DIRECT_NEIGHBOR_DISTANCE,
        #                    cummulative=False)

    def populate_heap(self, ship_id):
        ## SAVING SORTED DISTANCES
        ## TIMING OUT
        # if ship_id not in self.heap_set:
        #     self.heap_set.add(ship_id)
        #
        #     ship = self.data.game.me._ships.get(ship_id)
        #
        #     curr_cell = (ship.position.y, ship.position.x)
        #     seek_val = Matrix_val.TEN
        #
        #     indices, distances = get_n_closest_masked(self.top_halite,
        #                                               self.data.init_data.myMatrix.distances.cell[curr_cell],
        #                                               seek_val,
        #                                               15)
        #
        #     indices_deque = deque(indices)
        #     distances_deque = deque(distances)
        #
        #     closest_ind = indices_deque.popleft()
        #     closest_dist = distances_deque.popleft()
        #
        #     destination = Position(closest_ind[0], closest_ind[1]) ## INDICES ARE IN (y, x) FORMAT
        #     s = ExploreShip(closest_dist, ship_id, curr_cell, destination, indices_deque, distances_deque)
        #     heapq.heappush(self.heap_dist, s)


        ## JUST GETS CLOSEST TOP AMOUNT HALITE (BASED ON TOP HALITE COPIED)
        # if ship_id not in self.heap_set:
        #     self.heap_set.add(ship_id)
        #
        #     ship = self.data.game.me._ships.get(ship_id)
        #
        #     curr_cell = (ship.position.y, ship.position.x)
        #     seek_val = Matrix_val.ZERO
        #     coord, min_di, val = get_coord_closest(seek_val,
        #                                            self.top_halite,
        #                                            self.data.init_data.myMatrix.distances.cell[curr_cell],
        #                                            Inequality.GREATERTHAN)
        #     destination = Position(coord[1], coord[0])
        #     s = ExploreShip(min_di, ship_id, curr_cell, destination, None, None)
        #     heapq.heappush(self.heap_dist, s)


        ## FOR CLOSEST TOP HARVEST PER TURN
        if ship_id not in self.heap_set:
            self.heap_set.add(ship_id)

            ship = self.data.game.me._ships.get(ship_id)

            curr_cell = (ship.position.y, ship.position.x)
            distance_matrix = self.data.init_data.myMatrix.distances.cell[curr_cell]
            matrix_highest_ratio = self.get_highest_harvest(ship, curr_cell)
            max_ratio, coord = get_coord_max_closest(matrix_highest_ratio, distance_matrix)
            destination = Position(coord[1], coord[0])

            s = ExploreShip2(max_ratio, ship_id, destination)
            heapq.heappush(self.heap_dist, s)

    def get_highest_harvest(self, ship, curr_cell):
        """
        GET HIGHEST HARVEST PER TURN RATIO (MATRIX) FOR SPECIFIC SHIP
        """
        available_harvest = self.harvest_matrix * self.taken_matrix  ## REMOVES CELL THAT ARE ALREADY TAKEN
        distance_to = self.data.init_data.myMatrix.distances.cell[curr_cell]  ## WILL CONTAIN DISTANCES TO EACH CELL
        distances = distance_to + self.data.myMatrix.distances.closest_dock  ## DISTANCE TO THAT CELL + DISTANCE TO GO HOME

        # harvest_per_turn_matrix = available_harvest / distances                    ## RATIO: HARVEST PER TURN
        ## CAUSES AN ERROR WHEN DISTANCES HAS ZERO
        ## TO HANDLE ERROR (WILL BE REPLACED WITH ZERO)
        harvest_per_turn_ratio_matrix = np.divide(available_harvest, distances, out=np.zeros_like(available_harvest),
                                                  where=distances != 0)

        return harvest_per_turn_ratio_matrix

    def get_move_points_explore(self, ship, directions):
        """
        GET POINTS FOR MOVING EXPLORING SHIPS

        :param ship:
        :param directions: DIRECTIONS TO CONSIDER
        :return:
        """
        points = []

        for direction in directions:
            # for direction in MyConstants.DIRECTIONS:
            priority_direction = 1 if direction in directions else 0

            destination = self.get_destination(ship, direction)

            safe = self.data.myMatrix.locations.safe[destination.y][destination.x]
            occupied = self.data.myMatrix.locations.occupied[destination.y][destination.x]
            cost = self.data.myMatrix.halite.cost[destination.y][destination.x]
            potential_enemy_collision = self.data.myMatrix.locations.potential_enemy_collisions[destination.y][
                destination.x]

            c = ExplorePoints(priority_direction, safe, occupied, potential_enemy_collision, cost, direction)
            points.append(c)

        safe = self.data.myMatrix.locations.safe[ship.position.y][ship.position.x]
        occupied = 0 if self.data.myMatrix.locations.occupied[ship.position.y][ship.position.x] >= -1 else -1
        potential_enemy_collision = self.data.myMatrix.locations.potential_enemy_collisions[ship.position.y][
            ship.position.x]

        points.append(ExplorePoints(priority_direction=1,
                                    safe=safe,
                                    occupied=occupied,
                                    potential_enemy_collision=potential_enemy_collision,
                                    cost=999,
                                    direction=Direction.Still))

        logging.debug(points)

        return points