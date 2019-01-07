from src.common.orderedSet import OrderedSet
from src.common.values import MyConstants, Matrix_val, Inequality
from hlt.positionals import Position
from src.common.points import SupportShip, SupportPoints, AttackPoints
from src.common.matrix.functions import get_coord_closest
from hlt.positionals import Direction
import logging

class Attacks():
    def get_neighbor_IDs(self, ship):
        """
        GET NEXT NEIGHBORS IN THE GIVEN SHIP

        :return: SET OF IDs
        """
        ids = OrderedSet()
        for direction in MyConstants.DIRECTIONS:
            destination = self.get_destination(ship, direction)
            id = self.data.myMatrix.locations.myShipsID[destination.y][destination.x]
            if id > Matrix_val.ZERO: ids.add(id)

        return ids


    def get_enemy_ship(self, position):
        """
        GET ENEMY SHIP OBJECT GIVEN THE POSITION
        """
        player_id = self.data.myMatrix.locations.enemyShipsOwner[position.y][position.x]
        ship_id = self.data.myMatrix.locations.enemyShipsID[position.y][position.x]
        ship = self.data.game.players[player_id]._ships.get(ship_id)

        return ship, ship_id


    def get_enemy_position(self, ship):
        """
        GET DIRECTIONS AND POSITION OF THE CLOSEST ENEMY GIVEN THE SHIP
        """
        curr_cell = (ship.position.y, ship.position.x)
        coord, distance, val = get_coord_closest(Matrix_val.ONE,
                                                 self.data.myMatrix.locations.enemyShips,
                                                 self.data.init_data.myMatrix.distances.cell[curr_cell],
                                                 Inequality.EQUAL)
        enemy_position = Position(coord[1], coord[0])
        directions = self.get_directions_target(ship, enemy_position)

        return directions, enemy_position


    def get_move_points_attacking(self, ship, directions):
        """
        GET POINTS FOR ATTACKING

        :param ship:
        :param directions:
        :return: POINTS
        """
        points = []

        for direction in directions:
            destination = self.get_destination(ship, direction)
            safe = self.data.myMatrix.locations.safe[destination.y][destination.x]

            a = AttackPoints(safe, direction)
            points.append(a)

        ## POINTS FOR STAYING
        safe = self.data.myMatrix.locations.safe[ship.position.y][ship.position.x]
        points.append(AttackPoints(safe=safe, direction=Direction.Still))

        logging.debug(points)

        return points


    def get_move_points_supporting(self, ship, directions):
        """
        GET POINTS FOR SUPPORTING

        :param ship:
        :param directions:
        :return: POINTS
        """
        points = []

        for direction in directions:
            destination = self.get_destination(ship, direction)
            safe = self.data.myMatrix.locations.safe[destination.y][destination.x]
            potential_enemy_collision = -self.data.myMatrix.locations.potential_enemy_collisions[destination.y][destination.x]
            s = SupportPoints(safe, potential_enemy_collision, direction)
            points.append(s)

        ## POINTS FOR STAYING
        safe = self.data.myMatrix.locations.safe[ship.position.y][ship.position.x]
        potential_enemy_collision = -self.data.myMatrix.locations.potential_enemy_collisions[ship.position.y][ship.position.x]
        points.append(SupportPoints(safe=safe, potential_enemy_collision=potential_enemy_collision, direction=Direction.Still))

        logging.debug(points)

        return points