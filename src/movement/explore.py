from src.common.moves import Moves
from src.common.values import MoveMode, MyConstants, Matrix_val
import logging
from src.common.print import print_heading, print_matrix
from src.common.matrix.functions import get_position_highest_section, get_coord_closest
from hlt.positionals import Direction
from src.common.points import ExplorePoints, ExploreShip
from hlt.positionals import Position
import heapq


"""
TO DO!!!!!!!!!!!

ADD HEAP TO AVOID COLLISIONS/KICKING

AVOID SWARMING INTO AN AREA WHERE OTHERS HAVE NO PLACE TO GO


"""

class Explore(Moves):
    def __init__(self, data, prev_data):
        super().__init__(data, prev_data)

        self.heap_set = set()  ## USED TO NOT HAVE DUPLICATE SHIP IDs IN THE HEAP DIST
        self.heap_dist = []
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
        ## THIS SEEMS TO PERFORM WORST THAN ABOVE, WHY???
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

        while self.heap_dist:
            s = heapq.heappop(self.heap_dist)   ## MOVE CLOSEST SHIPS FIRST, TO PREVENT COLLISIONS
            logging.debug(s)                    ## EXPLORE SHIP OBJECT

            ship = self.data.game.me._ships.get(s.ship_id)
            directions = self.get_directions_target(ship, s.destination)
            direction = self.best_direction(ship, directions, mode=MoveMode.EXPLORE)
            self.move_mark_unsafe(ship, direction)


    def populate_heap(self, ship_id):
        if ship_id not in self.heap_set:
            self.heap_set.add(ship_id)

            ship = self.data.game.me._ships.get(ship_id)

            curr_cell = (ship.position.y, ship.position.x)
            seek_val = Matrix_val.TEN
            coord, min_di, val = get_coord_closest(seek_val,
                                                   self.data.matrix.halite.top_amount,
                                                   self.data.init_data.matrix.distances[curr_cell])
            destination = Position(coord[1], coord[0])
            s = ExploreShip(min_di, ship_id, curr_cell, destination)
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
        coord, min_di, val = get_coord_closest(seek_val, self.data.matrix.halite.top_amount, self.data.init_data.matrix.distances[curr_cell])
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

            safe = self.data.matrix.locations.safe[destination.y][destination.x]
            occupied = self.data.matrix.locations.occupied[destination.y][destination.x]
            cost = self.data.matrix.halite.cost[destination.y][destination.x]
            potential_enemy_collision = self.data.matrix.locations.potential_enemy_collisions[destination.y][destination.x]

            c = ExplorePoints(safe, occupied, potential_enemy_collision, cost, direction)
            points.append(c)

        safe = self.data.matrix.locations.safe[ship.position.y][ship.position.x]
        occupied = 0 if self.data.matrix.locations.occupied[ship.position.y][ship.position.x] >= -1 else -1
        potential_enemy_collision = self.data.matrix.locations.potential_enemy_collisions[ship.position.y][ship.position.x]

        points.append(ExplorePoints(safe=safe,
                                    occupied=occupied,
                                    potential_enemy_collision=potential_enemy_collision,
                                    cost=999,
                                    direction=Direction.Still))

        logging.debug(points)

        return points