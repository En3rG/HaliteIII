
from src.common.print import print_heading
from src.common.moves import Moves
from src.common.values import MoveMode, MyConstants
from src.common.points import StartPoints
import logging

"""
TO DO!!!!!!!!!!!


"""

class Start(Moves):
    def __init__(self, data, prev_data):
        super().__init__(data, prev_data)

        self.move_ships()

    def move_ships(self):
        print_heading("Moving early game......")

        if self.data.game.turn_number <= 6:  ## SHIPS SHOULD MOVE OUT ON TURNS 2, 3, 4, 5, 6
            if self.data.game.turn_number == 6:
                new_ship_id = list(sorted(self.data.mySets.ships_all))[-1]
                ship = self.data.game.me._ships.get(new_ship_id)
                direction = self.best_direction(ship, mode=MoveMode.MINSTART)
                self.move_mark_unsafe(ship, direction)
            elif len(self.data.mySets.ships_all) >= 1:
                out_ship_id = list(sorted(self.data.mySets.ships_all))[-1]
                ship = self.data.game.me._ships.get(out_ship_id)
                direction = self.best_direction(ship, mode=MoveMode.MAXSTART)
                self.move_mark_unsafe(ship, direction)


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
            harvest = self.data.myMatrix.halite.harvest[destination.y][destination.x]

            c = StartPoints(safe=0, hasShip=hasShip, harvest=-harvest, direction=direction) ## FLIP HARVEST
            points.append(c)

        logging.debug(points)

        return points
