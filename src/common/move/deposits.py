from src.common.points import FarthestShip, DepositPoints
from src.common.values import MoveMode, Matrix_val, Inequality, MyConstants
from hlt.positionals import Direction
from src.common.matrix.functions import get_coord_closest
from hlt.positionals import Position
import logging
import heapq

class Deposits():
    def populate_heap(self, ship):
        """
        GET DISTANCE FROM SHIPYARD/DOCKS
        """
        ## ONLY TAKING SHIPYARD INTO ACCOUNT
        # if ship.id not in self.heap_set:
        #     self.heap_set.add(ship.id)
        #
        #     distance = self.data.game.game_map.calculate_distance(ship.position, self.data.game.me.shipyard.position)
        #     directions = self.get_directions_target(ship, self.data.game.me.shipyard.position)
        #     num_directions = len(directions)
        #     s = FarthestShip(distance, num_directions, ship.id, directions)
        #     heapq.heappush(self.heap_dist, s)

        ## TAKING DOCKS INTO ACCOUNT
        if ship.id not in self.heap_set:
            self.heap_set.add(ship.id)

            curr_cell = (ship.position.y, ship.position.x)
            coord, distance, value = get_coord_closest(Matrix_val.ONE,
                                                       self.data.myMatrix.locations.myDocks,
                                                       self.data.init_data.myMatrix.distances.cell[curr_cell],
                                                       Inequality.EQUAL)
            position = Position(coord[1], coord[0])
            directions = self.get_directions_target(ship, position)
            num_directions = len(directions)
            s = FarthestShip(distance, num_directions, ship.id, directions)
            heapq.heappush(self.heap_dist, s)

    def depositNow(self, ship, directions):
        """
        SHIP IS RETURNING/DEPOSITING.  PERFORM NECESSARY STEPS
        """
        logging.debug("Ship id: {} is returning".format(ship.id))
        direction, points = self.best_direction(ship, directions, mode=MoveMode.DEPOSIT)
        self.move_mark_unsafe(ship, direction, points)
        self.data.mySets.ships_returning.add(ship.id)

    def get_move_points_returning(self, ship, directions):
        """
        GET POINTS FOR RETURNING

        :param ship:
        :param directions: CLEAN POSSIBLE DIRECTIONS
        :return:
        """
        ## IF OTHER ARE UNSAFE, PICK THIS DIRECTION (STILL)
        potential_enemy_collision = self.data.myMatrix.locations.potential_enemy_collisions[ship.position.y][ship.position.x]
        potential_ally_collision = self.data.myMatrix.locations.potential_ally_collisions[ship.position.y][ship.position.x]
        points = [DepositPoints(priority_direction=1,
                                safe=1,
                                dock=0,
                                enemy_occupied=0,
                                potential_enemy_collision=potential_enemy_collision,
                                potential_ally_collision=potential_ally_collision,
                                cost=999,
                                direction=Direction.Still)]

        for direction in directions:
            # for direction in MyConstants.DIRECTIONS:
            priority_direction = 1 if direction in directions else 0

            destination = self.get_destination(ship, direction)

            safe = self.data.myMatrix.locations.safe[destination.y][destination.x]
            dock = 1 if self.data.myMatrix.locations.myDocks[destination.y][destination.x] else 0
            enemy_occupied = self.data.myMatrix.locations.enemyShips[destination.y][destination.x]
            cost = self.data.myMatrix.halite.cost[destination.y][destination.x]
            potential_enemy_collision = self.data.myMatrix.locations.potential_enemy_collisions[destination.y][destination.x]
            potential_ally_collision = self.data.myMatrix.locations.potential_ally_collisions[destination.y][destination.x]

            c = DepositPoints(priority_direction,
                              safe,
                              dock,
                              enemy_occupied,
                              potential_enemy_collision,
                              potential_ally_collision,
                              cost,
                              direction)
            points.append(c)

        logging.debug(points)
        return points