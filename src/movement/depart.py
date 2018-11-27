from src.common.print import print_heading
from src.common.moves import Moves
from src.common.values import MoveMode, Matrix_val
from hlt.positionals import Position
from hlt.positionals import Direction
from src.common.matrix.functions import get_coord_closest
from src.common.points import DepartPoints
import logging

class Depart(Moves):
    def __init__(self, data, prev_data):
        super().__init__(data, prev_data)

        self.move_ships()

    def move_ships(self):
        print_heading("Moving depart ships......")

        docks_position = self.get_positions_docks()

        for position in docks_position:
            ship_id = self.data.matrix.myShipsID[position.y][position.x]
            if ship_id != 0:
                logging.debug("Ship departing: {}".format(ship_id))
                self.departNow(ship_id)


    def get_positions_docks(self):
        """
        :return: A LIST OF POSITIONS OF THE DOCKS/SHIPYARD
        """
        docks_position = [self.data.me.shipyard.position]
        for dropoff in self.data.me.get_dropoffs():
            docks_position.append(dropoff.position)

        return docks_position


    def departNow(self, ship_id):
        ship = self.data.me._ships.get(ship_id)
        curr_cell = (ship.position.y, ship.position.x)
        seek_val = Matrix_val.TEN
        coord, min_di, val = get_coord_closest(seek_val, self.data.matrix.top_halite,
                                               self.data.init_data.matrix.distances[curr_cell])
        destination = Position(coord[1], coord[0])
        directions = self.get_directions_target(ship, destination)
        direction = self.best_direction(ship, directions, mode=MoveMode.DEPART)
        self.move_mark_unsafe(ship, direction)


    def get_points_depart(self, ship, directions):
        """
        GET POINTS FOR DEPARTING

        :param ship:
        :param directions: DIRECTIONS TO CONSIDER
        :return:
        """
        points = []

        for direction in directions:
            destination = self.get_destination(ship, direction)

            safe = self.data.matrix.safe[destination.y][destination.x]
            cost = self.data.matrix.cost[destination.y][destination.x]

            c = DepartPoints(safe, cost, direction)
            points.append(c)

        logging.debug(points)

        return points