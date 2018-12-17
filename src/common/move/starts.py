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
            harvest = self.data.myMatrix.halite.harvest[destination.y][destination.x]

            c = StartPoints(safe=0, harvest=harvest, direction=direction)
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
            harvest = self.data.myMatrix.halite.harvest[destination.y][destination.x]

            c = StartPoints(safe=0, harvest=harvest, direction=direction)  ## FLIP HARVEST
            points.append(c)

        logging.debug(points)

        return points