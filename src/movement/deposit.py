import logging
import heapq
from src.common.moves import Moves
from src.common.points import FarthestShip, DepositPoints
from src.common.values import MoveMode, Matrix_val, Inequality
from hlt.positionals import Direction
from src.common.print import print_heading
from src.common.matrix.functions import get_coord_closest
from hlt.positionals import Position


"""
TO DO!!!!

IF DOCK IS BLOCKED, SHOULD GO AROUND OR COLLIDE WITH ENEMY


"""

class Deposit(Moves):
    def __init__(self, data, prev_data):
        super().__init__(data, prev_data)
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

                if ship and (ship.position.y, ship.position.x) not in self.data.mySets.dock_positions:
                    self.populate_heap(ship)

        ## MOVE KICKED SHIPS FIRST (IF ANY)
        while self.data.mySets.ships_kicked:
            ship_kicked = self.data.mySets.ships_kicked.pop()
            logging.debug("Moving kicked ship ({}) for deposit".format(ship_kicked))
            ship = self.data.game.me._ships.get(ship_kicked)
            directions = self.get_directions_target(ship, self.data.game.me.shipyard.position)
            self.returning(ship, directions)  ## CANNOT ASSUME SHIP KICKED BY DEPART IS RETURNING!!!!!!!!!1

        ## MOVE SHIPS, BASED ON HEAP
        while self.heap_dist:
            s = heapq.heappop(self.heap_dist)
            ship = self.data.game.me._ships.get(s.ship_id)
            self.returning(ship, s.directions)


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
                                                       self.data.init_data.myMatrix.distances[curr_cell],
                                                       Inequality.EQUAL)
            position = Position(coord[1], coord[0])
            directions = self.get_directions_target(ship, position)
            num_directions = len(directions)
            s = FarthestShip(distance, num_directions, ship.id, directions)
            heapq.heappush(self.heap_dist, s)


    def returning(self, ship, directions):
        """
        SHIP IS RETURNING/DEPOSITING.  PERFORM NECESSARY STEPS
        """
        logging.debug("Ship id: {} is returning".format(ship.id))
        direction = self.best_direction(ship, directions, mode=MoveMode.DEPOSIT)
        self.move_mark_unsafe(ship, direction)
        self.data.mySets.ships_returning.add(ship.id)


    def get_points_returning(self, ship, directions):
        """
        GET POINTS FOR RETURNING

        :param ship:
        :param directions: CLEAN POSSIBLE DIRECTIONS
        :return:
        """
        ## IF OTHER ARE UNSAFE, PICK THIS DIRECTION (STILL)
        potential_enemy_collision = self.data.myMatrix.locations.potential_enemy_collisions[ship.position.y][ship.position.x]
        potential_ally_collision = self.data.myMatrix.locations.potential_enemy_collisions[ship.position.y][ship.position.x]
        points = [ DepositPoints(safe=1,
                                 dock = 0,
                                 potential_enemy_collision=potential_enemy_collision,
                                 potential_ally_collision=potential_ally_collision,
                                 cost=999,
                                 direction=Direction.Still) ]

        for direction in directions:
            destination = self.get_destination(ship, direction)

            safe = self.data.myMatrix.locations.safe[destination.y][destination.x]
            dock = 1 if self.data.myMatrix.locations.myDocks[destination.y][destination.x] else 0
            cost = self.data.myMatrix.halite.cost[destination.y][destination.x]
            potential_enemy_collision = self.data.myMatrix.locations.potential_enemy_collisions[destination.y][destination.x]
            potential_ally_collision = self.data.myMatrix.locations.potential_enemy_collisions[destination.y][destination.x]

            c = DepositPoints(safe, dock, potential_enemy_collision, potential_ally_collision, cost, direction)
            points.append(c)

        logging.debug(points)
        return points