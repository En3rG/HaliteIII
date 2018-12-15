from src.common.print import print_heading
from src.common.moves import Moves
from hlt.positionals import Position
from src.common.values import MyConstants, Matrix_val, MoveMode, Inequality
from src.common.matrix.functions import get_coord_closest
from src.common.points import SupportShip, SupportPoints, AttackPoints
from hlt.positionals import Direction
from src.common.classes import OrderedSet
import numpy as np
import logging
import heapq

"""
TO DO!!!!!!!!!!!!

BLOCK ENEMY DOCKS

ONLY ATTACK WHEN THERES SUPPORT
DONT ATTACK WHEN HAVE HIGH CARGO


TRY TO NOT INFLUENCE ENEMY IF POSSIBLE


"""


class Attack(Moves):
    def __init__(self, data, prev_data):
        super().__init__(data, prev_data)

        self.heap_support = []
        self.considered_already = OrderedSet()
        self.move_ships()


    def move_ships(self):
        print_heading("Moving attack ships......")

        ## MOVE SHIPS CLOSEST TO ENEMY FIRST (WITH ITS SUPPORT SHIP)
        if self.data.myVars.allowAttack:
            for i in range(1, MyConstants.ENGAGE_ENEMY_DISTANCE):  ## DONT NEED TO MOVE FURTHEST ONES (WILL BE MOVED AS SUPPORT)
                matrix = self.data.myMatrix.locations.engage_enemy[i] * self.data.myMatrix.locations.myShipsID
                r, c = np.where(matrix > Matrix_val.ZERO)
                matrixIDs = OrderedSet(self.data.myMatrix.locations.myShipsID[r, c])
                ships_attacking = matrixIDs & self.data.mySets.ships_to_move
                self.considered_already.update(ships_attacking)

                self.heap_support = [] ## RESET PER ITERATION
                for ship_id in ships_attacking:
                    self.populate_heap(ship_id)

                while self.heap_support:
                    s = heapq.heappop(self.heap_support)
                    logging.debug(s)

                    first_ship = self.data.game.me._ships.get(s.ship_id)
                    direction, points = self.best_direction(first_ship, s.directions, mode=MoveMode.ATTACKING)

                    if direction != Direction.Still:
                    ## IF STAYING STILL, NO NEED TO MOVE
                    ## FIRST SHIP WILL JUST HARVEST/EXPLORE
                    ## SUPPORT SHIP MOVE WILL BE DETERMINED LATER
                        self.move_mark_unsafe(first_ship, direction, points)

                        logging.debug("Attacking ship id: {} support ships: {}".format(first_ship.id, s.support_ships))

                        for support_id in sorted(s.support_ships):                      ## ADD SORTED TO HAVE SAME ORDER ONLINE
                            if support_id in self.data.mySets.ships_to_move:            ## DONT MOVE SHIPS THAT ALREADY MOVED
                                support_ship = self.data.game.me._ships.get(support_id)
                                support_directions = self.get_directions_target(support_ship, first_ship.position)
                                direction, points = self.best_direction(support_ship, support_directions, mode=MoveMode.SUPPORTING)
                                self.move_mark_unsafe(support_ship, direction, points)


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

        support_ships = OrderedSet()
        for support_id in potential_support:
            if support_id in self.data.mySets.ships_to_move:
                support_ship = self.data.game.me._ships.get(support_id)
                if support_ship.halite_amount < enemy_halite * (MyConstants.ATTACK_ENEMY_HALITE_RATIO * MyConstants.ATTACK_ENEMY_HALITE_RATIO):
                    support_ships.add(support_id)

        num_support = len(support_ships)

        if my_halite < enemy_halite * MyConstants.ATTACK_ENEMY_HALITE_RATIO and num_support >= 1:
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
        #for direction in MyConstants.DIRECTIONS:
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
        #for direction in MyConstants.DIRECTIONS:
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