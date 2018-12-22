from src.common.points import FarthestShip, DepositPoints
from src.common.values import MoveMode, Matrix_val, Inequality, MyConstants
from hlt.positionals import Direction
from src.common.matrix.functions import get_coord_closest, pad_around, Section
from src.common.print import print_matrix
from src.common.functions import get_adjacent_directions, a_star
from hlt.positionals import Position
import logging
import heapq
import numpy as np

class Deposits():
    def depositNow(self, ship, dock_position, directions):
        """
        SHIP IS RETURNING/DEPOSITING.  PERFORM NECESSARY STEPS
        """
        logging.debug("Ship id: {} is returning".format(ship.id))

        # if len(directions) == 1:
        #     direction, points = self.best_direction(ship, directions, mode=MoveMode.DEPOSIT, avoid_enemy=False)
        # else:
        #     direction, points = self.best_direction(ship, directions, mode=MoveMode.DEPOSIT)
        #
        # self.move_mark_unsafe(ship, direction, points)
        # self.data.mySets.ships_returning.add(ship.id)


        if self.isEnemy_closeby(ship):
            ## PATH IS 1 LESS, SINCE WILL BE PADDED
            section = Section(self.data.myMatrix.locations.potential_enemy_collisions, ship.position, MyConstants.DEPOSIT_PERIMETER-1)
            matrix_path = pad_around(section.matrix)
            section = Section(self.data.myMatrix.halite.amount, ship.position, MyConstants.DEPOSIT_PERIMETER)
            matrix_cost = section.matrix
            goal_position = self.get_goal_in_section(matrix_path, section.center, ship.position, dock_position, directions)
            print_matrix("matrix path", matrix_path)
            print_matrix("matrix_cost", matrix_cost)
            logging.debug("ship id {} ship position {} dock position {} goal_position {}".format(ship.id, ship.position, dock_position, goal_position))
            path = a_star(matrix_path, matrix_cost, section.center, goal_position)
            logging.debug("path {}".format(path))

            if len(path) > 0:
                start_coord = path[-1]
                next_coord = path[-2]
                start = Position(start_coord[1], start_coord[0])
                destination = Position(next_coord[1], next_coord[0])
                directions = self.get_directions_start_target(start, destination)
                points = None
                logging.debug("Found path using A* directions {}".format(directions))
                direction, points = self.best_direction(ship, directions, mode=MoveMode.DEPOSIT, avoid_enemy=False)
            else:
                direction, points = self.best_direction(ship, directions, mode=MoveMode.DEPOSIT, avoid_enemy=True)
        else:
            direction, points = self.best_direction(ship, directions, mode=MoveMode.DEPOSIT, avoid_enemy=False)

        self.move_mark_unsafe(ship, direction, points)
        self.data.mySets.ships_returning.add(ship.id)


    def isEnemy_closeby(self, ship):
        section = Section(self.data.myMatrix.locations.enemyShips, ship.position, MyConstants.DEPOSIT_PERIMETER)
        perimeter = section.matrix
        r, c = np.where(perimeter == Matrix_val.ONE)

        return len(r) >= 1


    def get_goal_in_section(self, matrix_path, center, start, goal, directions):
        row = min(MyConstants.DEPOSIT_PERIMETER, abs(start.y - goal.y))
        col = min(MyConstants.DEPOSIT_PERIMETER, abs(start.x - goal.x))

        if Direction.North in directions:
            y = center.y - row
        else:
            y = center.y + row

        if Direction.West in directions:
            x = center.x - col
        else:
            x = center.x + col

        return Position(x, y)

    def get_move_points_returning(self, ship, directions, avoid_enemy):
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
                                direction=Direction.Still,
                                avoid_enemy=avoid_enemy)]

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
                              direction,
                              avoid_enemy=avoid_enemy)
            points.append(c)

        logging.debug(points)
        return points