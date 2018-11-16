import logging
import heapq
from hlt import constants
from src.common.movement import Moves
from src.common.values import DirectionHomeMode
from src.common.points import FarthestShip, RetreatPoints
from hlt.positionals import Direction


class Retreat(Moves):
    def __init__(self, data, prev_data, command_queue, halite_stats):
        super().__init__(data, prev_data, halite_stats)

        self.command_queue = command_queue
        self.turn_number = data.game.turn_number
        self.turn_left = constants.MAX_TURNS - self.turn_number
        self.heap_dist = []
        self.farthest_ship = FarthestShip(0, 0, 0, None)

        self.check_retreat()

    def check_retreat(self):
        """
        POPULATE HEAP BASED ON DISTANCE FROM SHIPYARD
        CHECK IF WE NEED TO START RETREATING BACK TO SHIPYARD

        :return: COMMAND_QUEUE
        """
        self.populate_heap()
        logging.debug("Farthest ship is {}, with {} turns left".format(self.farthest_ship, self.turn_left))

        if self.farthest_ship.distance + 1 > self.turn_left:
            self.retreat_ships()


    def populate_heap(self):
        """
        GET DISTANCE FROM SHIPYARD

        NEED TO ADD GETTING CLOSEST DOCK LATER!!!!!!!!!!!11

        :return:
        """
        for ship in self.data.me.get_ships():
            distance = self.data.game_map.calculate_distance(ship.position, self.data.me.shipyard.position)
            directions = self.directions_home(ship, self.data.me.shipyard.position)
            num_directions = len(directions)
            s = FarthestShip(distance, num_directions, ship.id, directions)
            self.farthest_ship = max(s , self.farthest_ship)
            heapq.heappush(self.heap_dist, s)


    def retreat_ships(self):
        """
        MOVE ALL SHIPS TO RETREAT BACK TO SHIPYARD
        """

        while self.heap_dist:
            s = heapq.heappop(self.heap_dist)  ## MOVE CLOSEST SHIPS FIRST, TO PREVENT COLLISIONS
            logging.debug("Ship id: {} is retreating, with distance {}".format(s.ship_id, s.distance))

            ship = self.data.me.get_ship(s.ship_id)
            direction = self.best_direction_home(ship, s.directions, mode=DirectionHomeMode.RETREAT)

            self.move_mark_unsafe(ship, direction)


    def get_points_retreat(self, ship, directions):
        """
        GET POINTS FOR RETREATING

        :param ship:
        :param directions: CLEAN POSSIBLE DIRECTIONS
        :return:
        """
        ## IF OTHER ARE UNSAFE, PICK THIS DIRECTION (STILL)
        points = [RetreatPoints(shipyard=0, unsafe=1, potential_collision=-999, direction=Direction.Still)]

        for direction in directions:
            destination = self.get_destination(ship, direction)

            shipyard = self.data.matrix.myShipyard[destination.y][destination.x]
            unsafe = self.data.matrix.unsafe[destination.y][destination.x]
            potential_collision = self.data.matrix.potential_ally_collisions[destination.y][destination.x]

            logging.debug("shipyard: {} unsafe: {} potential_collision: {} direction: {}".format(shipyard,
                                                                                                 unsafe,
                                                                                                 potential_collision,
                                                                                                 direction))
            c = RetreatPoints(shipyard, unsafe, potential_collision, direction)
            points.append(c)

        return points


