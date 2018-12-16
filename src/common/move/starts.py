from src.common.points import StartPoints
import logging
from src.common.values import MoveMode, MyConstants

class Starts():
    def get_move_points_maxstart(self, ship):
        """
        GET POINTS FOR MOVING FIRST 4 SHIPS
        GET HIGHEST FREE HARVEST
        """
        points = []

        for direction in MyConstants.DIRECTIONS:
            destination = self.get_destination(ship, direction)

            hasShip = self.data.myMatrix.locations.myShips[destination.y][destination.x]
            harvest = self.data.myMatrix.halite.harvest[destination.y][destination.x]

            c = StartPoints(safe=0, hasShip=hasShip, harvest=harvest, direction=direction)
            points.append(c)

        logging.debug(points)

        return points

    def get_move_points_minstart(self, ship):
        """
        GET MOVE FOR FIFTH SHIP.  WILL KICK SHIP
        """
        points = []

        for direction in MyConstants.DIRECTIONS:
            destination = self.get_destination(ship, direction)

            hasShip = self.data.myMatrix.locations.myShips[destination.y][destination.x]
            canMove = 0 if self.data.myMatrix.locations.stuck[destination.y][destination.x] == 1 else 1
            harvest = self.data.myMatrix.halite.harvest[destination.y][destination.x]

            c = StartPoints(safe=0, hasShip=hasShip, harvest=harvest, direction=direction,
                            canMove=canMove)  ## FLIP HARVEST
            points.append(c)

        logging.debug(points)

        return points