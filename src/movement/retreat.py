import logging
import heapq
from hlt import constants
from src.common.moves import Moves
from src.common.values import MoveMode, MyConstants, Matrix_val
from src.common.points import FarthestShip, RetreatPoints
from hlt.positionals import Direction
from src.common.print import print_heading
from src.common.matrix.functions import get_coord_closest
from hlt.positionals import Position


"""
TO DO!!!!!!!!!!!

IMPROVE MOVEMENT WHEN THERE ARE TONS OF SHIPS TRYING TO GO TO THE DOCK


"""

class Retreat(Moves):
    def __init__(self, data, prev_data):
        super().__init__(data, prev_data)

        self.turns_left = constants.MAX_TURNS - data.game.turn_number
        self.heap_dist = []
        self.farthest_ship = FarthestShip(0, 0, 0, None)

        self.check_retreat()


    def check_retreat(self):
        """
        POPULATE HEAP BASED ON DISTANCE FROM SHIPYARD/DOCKS
        CHECK IF WE NEED TO START RETREATING BACK
        """
        print_heading("Check retreat......")

        self.populate_heap()

        logging.debug("Farthest ship is {}, with {} turns left".format(self.farthest_ship, self.turns_left))

        if self.farthest_ship.distance + MyConstants.EXTRA_TURNS_RETREAT > self.turns_left:
            self.retreat_ships()


    def populate_heap(self):
        """
        GET DISTANCE FROM SHIPYARD/DOCKS
        """
        ## ONLY BASED ON SHIPYARD POSITION
        # for ship in self.data.game.me.get_ships():
        #     distance = self.data.game.game_map.calculate_distance(ship.position, self.data.game.me.shipyard.position)
        #     directions = self.get_directions_target(ship, self.data.game.me.shipyard.position)
        #     num_directions = len(directions)
        #     s = FarthestShip(distance, num_directions, ship.id, directions)
        #     self.farthest_ship = max(s , self.farthest_ship)
        #     heapq.heappush(self.heap_dist, s)


        ## TAKING DOCKS INTO ACCOUNT
        for ship in self.data.game.me.get_ships():
            curr_cell = (ship.position.y, ship.position.x)
            coord, distance, value = get_coord_closest(Matrix_val.ONE,
                                                       self.data.myMatrix.locations.myDocks,
                                                       self.data.init_data.myMatrix.distances[curr_cell])
            position = Position(coord[1], coord[0])
            directions = self.get_directions_target(ship, position)
            num_directions = len(directions)
            s = FarthestShip(distance, num_directions, ship.id, directions)
            self.farthest_ship = max(s , self.farthest_ship)
            heapq.heappush(self.heap_dist, s)


    def retreat_ships(self):
        """
        MOVE ALL SHIPS TO RETREAT BACK TO SHIPYARD/DOCKS
        """
        while self.heap_dist:
            s = heapq.heappop(self.heap_dist)   ## MOVE CLOSEST SHIPS FIRST, TO PREVENT COLLISIONS
            logging.debug(s)                    ## FARTHEST SHIP OBJECT

            ship = self.data.game.me.get_ship(s.ship_id)
            direction = self.best_direction(ship, s.directions, mode=MoveMode.RETREAT)

            self.move_mark_unsafe(ship, direction)


    def get_points_retreat(self, ship, directions):
        """
        GET POINTS FOR RETREATING

        :param ship:
        :param directions: CLEAN POSSIBLE DIRECTIONS
        :return:
        """
        ## IF OTHER ARE UNSAFE, PICK THIS DIRECTION (STILL)
        points = [ RetreatPoints(shipyard=0, safe=1, stuck=0, potential_ally_collision=-999, direction=Direction.Still) ]

        for direction in directions:
            destination = self.get_destination(ship, direction)

            shipyard = self.data.myMatrix.locations.myDocks[destination.y][destination.x]
            safe = self.data.myMatrix.locations.safe[destination.y][destination.x]
            potential_ally_collision = self.data.myMatrix.locations.potential_ally_collisions[destination.y][destination.x]
            stuck = self.data.myMatrix.locations.stuck[ship.position.y][ship.position.x] ## STUCK BASED ON SHIPS CURRENT POSITION

            c = RetreatPoints(shipyard, safe, stuck, potential_ally_collision, direction)
            points.append(c)

        logging.debug(points)

        return points



