import logging
import heapq
from src.common.movement import Moves
from src.common.points import FarthestShip, DepositPoints
from src.common.values import MoveMode
from hlt.positionals import Direction
from src.common.print import print_heading


class Deposit(Moves):
    def __init__(self, data, prev_data, command_queue, halite_stats,):
        super().__init__(data, prev_data, halite_stats)
        self.command_queue = command_queue
        self.heap_dist = []
        self.heap_set = set()

        self.move_ships()

    def move_ships(self):
        print_heading("Moving depositing ships......")

        ## SHIPS JUST HIT MAX
        for ship_id in (self.data.all_ships & self.data.ships_to_move):
            ship = self.data.me._ships.get(ship_id)

            if ship.is_full:
                self.populate_heap(ship)

        ## SHIPS RETURNING PREVIOUSLY (HIT MAX)
        if self.prev_data:
            for ship_id in (self.prev_data.ships_returning & self.data.ships_to_move):
                ship = self.data.me._ships.get(ship_id)

                if ship and ship.position != self.data.me.shipyard.position:
                    self.populate_heap(ship)

        ## MOVE SHIPS RETURNING (JUST HIT MAX AND PREVIOUSLY RETURNING)
        while self.heap_dist:
            s = heapq.heappop(self.heap_dist)
            ship = self.data.me._ships.get(s.ship_id)
            self.returning(ship, s.directions)


    def populate_heap(self, ship):
        """
        GET DISTANCE FROM SHIPYARD

        NEED TO ADD GETTING CLOSEST DOCK LATER!!!!!!!!!!!11

        :return:
        """
        if ship.id not in self.heap_set:
            self.heap_set.add(ship.id)

            distance = self.data.game_map.calculate_distance(ship.position, self.data.me.shipyard.position)
            directions = self.get_directions_target(ship, self.data.me.shipyard.position)
            num_directions = len(directions)
            s = FarthestShip(distance, num_directions, ship.id, directions)
            heapq.heappush(self.heap_dist, s)


    def returning(self, ship, directions):
        logging.debug("Ship id: {} is returning".format(ship.id))
        direction = self.best_direction(ship, directions, mode=MoveMode.DEPOSIT)
        self.move_mark_unsafe(ship, direction)
        self.data.ships_returning.add(ship.id)


    def get_points_returning(self, ship, directions):
        """
        GET POINTS FOR RETURNING

        :param ship:
        :param directions: CLEAN POSSIBLE DIRECTIONS
        :return:
        """
        ## IF OTHER ARE UNSAFE, PICK THIS DIRECTION (STILL)
        points = [ DepositPoints(safe=1, cost=-999, direction=Direction.Still) ]

        for direction in directions:
            destination = self.get_destination(ship, direction)

            safe = self.data.matrix.safe[destination.y][destination.x]
            cost = self.data.matrix.cost[destination.y][destination.x]

            logging.debug("safe: {} cost: {} direction: {}".format(safe, cost, direction))
            c = DepositPoints(safe, cost, direction)
            points.append(c)

        return points