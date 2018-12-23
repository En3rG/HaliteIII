import logging
import heapq
from src.common.move.moves import Moves
from src.common.move.deposits import Deposits
from src.common.print import print_heading
from src.movement.collision_prevention import avoid_collision_direction
from src.common.points import FarthestShip, DepositPoints
from src.common.values import MoveMode, Matrix_val, Inequality, MyConstants
from hlt.positionals import Direction
from src.common.matrix.functions import get_coord_closest
from hlt.positionals import Position

"""
TO DO!!!!

IF DOCK IS BLOCKED, SHOULD GO AROUND OR COLLIDE WITH ENEMY
USE Concurrent Dijkstra's Algorithm

"""

class Deposit(Moves, Deposits):
    def __init__(self, data, prev_data):
        Moves.__init__(self, data, prev_data)
        self.heap_dist = []
        self.heap_set = set()   ## USED TO NOT HAVE DUPLICATE SHIP IDs IN THE HEAP DIST

        self.move_ships()


    def move_ships(self):
        print_heading("Moving depositing ships......")

        ## SHIPS JUST HIT MAX
        for ship_id in (self.data.mySets.ships_all & self.data.mySets.ships_to_move):
            ship = self.data.game.me._ships.get(ship_id)

            if ship.is_full:
                self.populate_heap(ship)

        ## SHIPS RETURNING PREVIOUSLY (HIT MAX)
        if self.prev_data:
            for ship_id in (self.prev_data.ships_returning & self.data.mySets.ships_to_move):
                ship = self.data.game.me._ships.get(ship_id)

                if ship and (ship.position.y, ship.position.x) not in self.data.mySets.dock_coords: ## SHIP ALREADY IN DOCK
                    self.populate_heap(ship)

        ## MOVE SHIPS, BASED ON HEAP
        while self.heap_dist:
            ## MOVE KICKED SHIPS FIRST (MAYBE BY BUILDING)
            while self.data.mySets.ships_kicked:
                ship_kicked = self.data.mySets.ships_kicked.pop()
                logging.debug("Moving kicked ship ({}) by a depositing ship".format(ship_kicked))
                ship = self.data.game.me._ships.get(ship_kicked)
                direction = avoid_collision_direction(self, ship, directions=None)
                self.move_mark_unsafe(ship, direction)

            s = heapq.heappop(self.heap_dist)
            if s.ship_id in self.data.mySets.ships_to_move:    ## MEANS IT HAS MOVED BEFORE (MAYBE KICKED)
                ship = self.data.game.me._ships.get(s.ship_id)
                self.depositNow(ship, s.dock_position, s.directions)

    def populate_heap(self, ship):
        """
        GET DISTANCE FROM SHIPYARD/DOCKS
        """
        ## ONLY TAKING SHIPYARD INTO ACCOUNT
        # if ship.id not in self.heap_set:
        #     self.heap_set.add(ship.id)
        #
        #     distance = self.data.game.game_map.calculate_distance(ship.position, self.data.game.me.shipyard.position)
        #     directions = self.get_directions_target(ship, self.data.game.me.shipyard.position)
        #     num_directions = len(directions)
        #     s = FarthestShip(distance, num_directions, ship.id, directions)
        #     heapq.heappush(self.heap_dist, s)

        ## TAKING DOCKS INTO ACCOUNT
        if ship.id not in self.heap_set:
            self.heap_set.add(ship.id)

            curr_cell = (ship.position.y, ship.position.x)
            coord, distance, value = get_coord_closest(Matrix_val.ONE,
                                                       self.data.myMatrix.locations.myDocks,
                                                       self.data.init_data.myMatrix.distances.cell[curr_cell],
                                                       Inequality.EQUAL)
            dock_position = Position(coord[1], coord[0])
            directions = self.get_directions_target(ship, dock_position)
            num_directions = len(directions)
            s = FarthestShip(distance, num_directions, ship.id, directions, dock_position)
            heapq.heappush(self.heap_dist, s)