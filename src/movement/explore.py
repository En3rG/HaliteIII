from src.common.moves import Moves
from src.common.values import MoveMode, MyConstants, Matrix_val, Inequality
import logging
from src.common.print import print_heading, print_matrix
from src.common.matrix.functions import get_coord_closest, get_n_closest_masked, populate_manhattan
from hlt.positionals import Direction
from src.common.points import ExplorePoints, ExploreShip
from hlt.positionals import Position
import heapq
from collections import deque
import copy



"""
TO DO!!!!!!!!!!!

TOP HALITE DOESNT CONSIDER INFLUENCE

GET HIGHEST HALITE CLOSE BY (MAYBE WITH A GIVEN DISTANCE??)

"""

class Explore(Moves):
    def __init__(self, data, prev_data):
        super().__init__(data, prev_data)

        self.heap_set = set()  ## USED TO NOT HAVE DUPLICATE SHIP IDs IN THE HEAP DIST
        self.heap_dist = []
        self.top_halite = copy.deepcopy(self.data.myMatrix.halite.top_amount)
        self.taken_destinations = set()
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
            ## MOVE KICKED SHIPS FIRST (IF ANY)
            while self.data.mySets.ships_kicked:
                ship_kicked = self.data.mySets.ships_kicked.pop()
                logging.debug("Moving kicked ship ({}) for explore".format(ship_kicked))
                self.exploreNow(ship_kicked)

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


        ## SAVING SORTED DISTANCES
        ## OR JUST GETTING CLOSEST, USING TOP HALITE COPIED
        while self.heap_dist:
            s = heapq.heappop(self.heap_dist)  ## MOVE CLOSEST SHIPS FIRST, TO PREVENT COLLISIONS
            logging.debug(s)  ## EXPLORE SHIP OBJECT

            ship = self.data.game.me._ships.get(s.ship_id)

            destination = self.get_untaken_destination(s)

            if destination:
                directions = self.get_directions_target(ship, destination)
                direction = self.best_direction(ship, directions, mode=MoveMode.EXPLORE)
                self.mark_taken_udpate_top_halite(destination)
                self.move_mark_unsafe(ship, direction)


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
        #                                               self.data.init_data.myMatrix.distances[curr_cell],
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
        if ship_id not in self.heap_set:
            self.heap_set.add(ship_id)

            ship = self.data.game.me._ships.get(ship_id)

            curr_cell = (ship.position.y, ship.position.x)
            seek_val = Matrix_val.ZERO
            coord, min_di, val = get_coord_closest(seek_val,
                                                   self.top_halite,
                                                   self.data.init_data.myMatrix.distances[curr_cell],
                                                   Inequality.GREATERTHAN)
            destination = Position(coord[1], coord[0])
            s = ExploreShip(min_di, ship_id, curr_cell, destination, None, None)
            heapq.heappush(self.heap_dist, s)


    def exploreNow(self, ship_id):
        """
        SHIP IS EXPLORING, PERFORM NECESSARY STEPS
        """
        ship = self.data.game.me._ships.get(ship_id)

        ## GET DIRECTION TO HIGHEST NEIGHBOR
        #direction = self.get_highest_harvest_move(ship)


        ## GET DIRECTION TO HIGHEST SECTION
        # destination = get_position_highest_section(self.data)
        # directions = self.get_directions_target(ship, destination)
        # direction = self.best_direction(ship, directions, mode=MoveMode.EXPLORE)
        # self.move_mark_unsafe(ship, direction)


        ## GET DIRECTION TO CLOSEST TOP HALITE
        curr_cell = (ship.position.y, ship.position.x)
        seek_val = Matrix_val.TEN
        coord, min_di, val = get_coord_closest(seek_val,
                                               self.data.myMatrix.halite.top_amount,
                                               self.data.init_data.myMatrix.distances[curr_cell],
                                               Inequality.GREATERTHAN)
        destination = Position(coord[1], coord[0])
        directions = self.get_directions_target(ship, destination)
        direction = self.best_direction(ship, directions, mode=MoveMode.EXPLORE)
        self.move_mark_unsafe(ship, direction)


    def get_points_explore(self, ship, directions):
        """
        GET POINTS FOR EXPLORING

        :param ship:
        :param directions: DIRECTIONS TO CONSIDER
        :return:
        """
        points = []

        for direction in directions:
            destination = self.get_destination(ship, direction)

            safe = self.data.myMatrix.locations.safe[destination.y][destination.x]
            occupied = self.data.myMatrix.locations.occupied[destination.y][destination.x]
            cost = self.data.myMatrix.halite.cost[destination.y][destination.x]
            potential_enemy_collision = self.data.myMatrix.locations.potential_enemy_collisions[destination.y][destination.x]

            c = ExplorePoints(safe, occupied, potential_enemy_collision, cost, direction)
            points.append(c)

        safe = self.data.myMatrix.locations.safe[ship.position.y][ship.position.x]
        occupied = 0 if self.data.myMatrix.locations.occupied[ship.position.y][ship.position.x] >= -1 else -1
        potential_enemy_collision = self.data.myMatrix.locations.potential_enemy_collisions[ship.position.y][ship.position.x]

        points.append(ExplorePoints(safe=safe,
                                    occupied=occupied,
                                    potential_enemy_collision=potential_enemy_collision,
                                    cost=999,
                                    direction=Direction.Still))

        logging.debug(points)

        return points