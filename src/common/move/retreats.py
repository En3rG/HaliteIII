
from hlt.positionals import Direction
import heapq
from src.common.values import MoveMode, MyConstants, Matrix_val, Inequality
from src.common.points import FarthestShip, RetreatPoints
import logging

class Retreats():
    def move_ships(self):
        """
        MOVE ALL SHIPS TO RETREAT BACK TO SHIPYARD/DOCKS
        """
        while self.heap_dist:
            s = heapq.heappop(self.heap_dist)  ## MOVE CLOSEST SHIPS FIRST, TO PREVENT COLLISIONS
            logging.debug(s)  ## FARTHEST SHIP OBJECT

            ship = self.data.game.me.get_ship(s.ship_id)
            direction = self.best_direction(ship, s.directions, mode=MoveMode.RETREAT)

            self.move_mark_unsafe(ship, direction)


    def get_move_points_retreat(self, ship, directions):
        """
        GET POINTS FOR RETREATING

        :param ship:
        :param directions: CLEAN POSSIBLE DIRECTIONS
        :return:
        """
        ## IF OTHER ARE UNSAFE, PICK THIS DIRECTION (STILL)
        points = [RetreatPoints(shipyard=0,
                                safe=1,
                                stuck=0,
                                potential_ally_collision=-999,
                                direction=Direction.Still)]

        for direction in directions:
            # for direction in MyConstants.DIRECTIONS:

            destination = self.get_destination(ship, direction)

            shipyard = self.data.myMatrix.locations.myDocks[destination.y][destination.x]
            safe = self.data.myMatrix.locations.safe[destination.y][destination.x]
            potential_ally_collision = self.data.myMatrix.locations.potential_ally_collisions[destination.y][destination.x]
            stuck = self.data.myMatrix.locations.stuck[ship.position.y][ship.position.x]  ## STUCK BASED ON SHIPS CURRENT POSITION

            c = RetreatPoints(shipyard, safe, stuck, potential_ally_collision, direction)
            points.append(c)

        logging.debug(points)

        return points