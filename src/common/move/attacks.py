from src.common.classes import OrderedSet
from src.common.values import MyConstants, Matrix_val, Inequality
from hlt.positionals import Position
from src.common.points import SupportShip, SupportPoints, AttackPoints
from src.common.move.harvests import Harvests
from src.common.matrix.functions import get_coord_closest
from hlt.positionals import Direction
import logging
import heapq

class Attacks(Harvests):
    def populate_heap(self, ship_id):
        """
        POPULATE HEAP, SHIP WITH LEAST SUPPORT WILL MOVE FIRST
        SO SHIPS WITH 2 SUPPORT WILL NOT TAKE A SUPPORT FOR ANOTHER

        WILL NOT BE ADDED TO HEAP IF IT HAS TOO MUCH HALITE CARGO
        """
        ship = self.data.game.me._ships.get(ship_id)
        neighbors = self.get_neighbor_IDs(ship)
        potential_support = neighbors - self.considered_already
        directions_to_enemy, enemy_position = self.get_enemy(ship)
        enemy_halite = self.data.myMatrix.locations.shipCargo[enemy_position.y][enemy_position.x]
        my_halite = ship.halite_amount

        if ship_id in self.data.mySets.ships_to_move: self.check_harvestNow(ship_id)
        if ship_id in self.data.mySets.ships_to_move: self.check_harvestLater(ship_id, MyConstants.DIRECTIONS)

        if ship_id in self.data.mySets.ships_to_move:
            support_ships = OrderedSet()
            for support_id in potential_support:
                if support_id in self.data.mySets.ships_to_move: self.check_harvestNow(ship_id)
                if support_id in self.data.mySets.ships_to_move: self.check_harvestLater(ship_id, MyConstants.DIRECTIONS)

                if support_id in self.data.mySets.ships_to_move:
                    support_ship = self.data.game.me._ships.get(support_id)
                    potental_harvest = (my_halite + enemy_halite) * 0.25  ## POTENTIAL HARVEST
                    real_gain = support_ship.halite_amount + potental_harvest % 1000  ## CAN ONLY GET MAX 1000
                    if real_gain > my_halite * MyConstants.SUPPORT_GAIN_RATIO:  ## MORE THAN 20% GAIN THAN WHAT WE LOST
                        support_ships.add(support_id)

            num_support = len(support_ships)

            # if my_halite < enemy_halite * MyConstants.ATTACK_ENEMY_HALITE_RATIO and num_support >= 1:
            if num_support >= 1:  ## ATTACK EVEN WHEN HAS HIGH CARGO
                s = SupportShip(num_support, ship.id, support_ships, directions_to_enemy)
                logging.debug(s)
                heapq.heappush(self.heap_support, s)

    def get_neighbor_IDs(self, ship):
        """
        GET NEXT NEIGHBORS IN THE GIVEN MATRIX

        :param matrix:
        :param position:
        :return: SET OF IDs
        """
        ids = OrderedSet()
        for direction in MyConstants.DIRECTIONS:
            destination = self.get_destination(ship, direction)
            id = self.data.myMatrix.locations.myShipsID[destination.y][destination.x]
            if id > Matrix_val.ZERO: ids.add(id)

        return ids

    def get_enemy(self, ship):
        """
        GET DIRECTIONS AND POSITION OF THE ENEMY
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
            # for direction in MyConstants.DIRECTIONS:
            ## POINTS FOR MOVING
            priority_direction = 1 if direction in directions else 0
            destination = self.get_destination(ship, direction)
            safe = self.data.myMatrix.locations.safe[destination.y][destination.x]

            a = AttackPoints(priority_direction, safe, direction)
            points.append(a)

        ## POINTS FOR STAYING
        safe = self.data.myMatrix.locations.safe[ship.position.y][ship.position.x]
        points.append(AttackPoints(priority_direction=1, safe=safe, direction=Direction.Still))

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
            # for direction in MyConstants.DIRECTIONS:
            ## POINTS FOR MOVING
            priority_direction = 1 if direction in directions else 0
            destination = self.get_destination(ship, direction)
            safe = self.data.myMatrix.locations.safe[destination.y][destination.x]

            s = SupportPoints(priority_direction, safe, direction)
            points.append(s)

        ## POINTS FOR STAYING
        safe = self.data.myMatrix.locations.safe[ship.position.y][ship.position.x]
        points.append(SupportPoints(priority_direction=1, safe=safe, direction=Direction.Still))

        logging.debug(points)

        return points