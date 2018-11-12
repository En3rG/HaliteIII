import logging
import heapq
from hlt import constants
from src.common.movement import Moves


class Retreat(Moves):
    def __init__(self, data, prev_data, halite_stats):
        super().__init__(data, prev_data, halite_stats)

        self.command_queue = []
        self.turn_number = data.game.turn_number
        self.turn_left = constants.MAX_TURNS - self.turn_number
        self.heap_dist = []
        self.farthest_ship = (0, 0) ## FIRST NUMBER IS DISTANCE, SECOND IS SHIP ID


    def check_retreat(self):
        """
        POPULATE HEAP BASED ON DISTANCE FROM SHIPYARD
        CHECK IF WE NEED TO START RETREATING BACK TO SHIPYARD

        :return: COMMAND_QUEUE
        """
        self.populate_heap()
        logging.debug("Farthest ship is {}, with {} turns left".format(self.farthest_ship, self.turn_left))

        if self.farthest_ship[0] + 1 > self.turn_left:
            self.retreat_ships()

        return self.command_queue


    def populate_heap(self):
        """
        GET DISTANCE FROM SHIPYARD

        NEED TO ADD GETTING CLOSEST DOCK LATER!!!!!!!!!!!11

        :return:
        """
        for ship in self.data.me.get_ships():
            distance = self.data.game_map.calculate_distance(ship.position, self.data.me.shipyard.position)
            self.farthest_ship = max((distance, ship.id), self.farthest_ship)
            heapq.heappush(self.heap_dist, (distance, ship.id))


    def retreat_ships(self):
        """
        MOVE ALL SHIPS TO RETREAT BACK TO SHIPYARD
        """
        while self.heap_dist:
            distance, ship_id = heapq.heappop(self.heap_dist)  ## MOVE CLOSEST SHIPS FIRST, TO PREVENT COLLISIONS
            logging.debug("Ship id: {} is retreating, with distance {}".format(ship_id, distance))
            ship = self.data.me.get_ship(ship_id)
            direction = self.get_direction_home(ship.position, self.data.me.shipyard.position)

            self.move_mark_unsafe(ship, direction)




