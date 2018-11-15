import logging
import random
from hlt.game_map import GameMap
from hlt.positionals import Position
from hlt.positionals import Direction
import abc
import itertools
from src.common.values import DirectionHomeMode, MyConstants, Matrix_val
from src.common.matrix import move_populate_area, print_matrix
from src.common.points import RetreatPoints, DepositPoints

class Moves(abc.ABC):
    """
    BASE CLASS USED FOR MOVEMENT LIKE RETREAT AND SHIPS
    """
    def __init__(self, data, prev_data, halite_stats):
        self.data = data
        self.prev_data = prev_data
        self.halite_stats = halite_stats


    def move_mark_unsafe(self, ship, direction):
        """
        GIVEN THE SHIP AND DIRECTION,
        POPULATE UNSAFE MATRIX, TAKING WRAPPING INTO ACCOUNT

        UPDATE POTENTIAL ALLY COLLISION MATRIX (MOVE AREA TO DIRECTION)

        APPEND MOVE TO COMMAND QUEUE

        REMOVE SHIP ID TO SHIP TO MOVE

        :param ship: SHIP OBJECT
        :param direction: MOVE DIRECTION
        :return:
        """
        destination = self.get_destination(ship, direction)
        self.data.mark_unsafe(destination)

        move_populate_area(self.data.matrix.potential_ally_collisions,
                           ship.position, destination, MyConstants.DIRECT_NEIGHBOR_RADIUS)

        self.halite_stats.record_data(ship, destination, self.data)

        self.data.ships_to_move.remove(ship.id)

        logging.debug("Ship id: {} moving {} from {} to {}".format(ship.id, direction, ship.position, destination))
        self.command_queue.append(ship.move(direction))


    def directions_home(self, ship, home_position):
        """
        GET DIRECTIONS TOWARDS HOME

        :param ship:
        :param home_position:
        :return:
        """
        # directions = GameMap._get_target_direction(ship_position, home_position)   ## WILL GIVE LONGER PATH, IF WRAPPING
        directions = self.get_directions_target(ship.position, home_position, self.data.map_width)

        clean_choices = [x for x in directions if x != None]  ## CAN HAVE A NONE
        logging.debug("ship position: {} shipyard position: {} clean_choices: {}".format(ship.position,
                                                                                         home_position,
                                                                                         clean_choices))

        return clean_choices


    def best_direction_home(self, ship, directions, mode=""):
        """
        USING POINT SYSTEM
        GET BEST DIRECTION GIVEN CLEAN POSSIBLE DIRECTIONS TOWARD HOME/TARGET

        :param ship:
        :param directions: CHOICES OF DIRECTIONS
        :param mode:
        :return: BEST DIRECTION
        """
        logging.debug("Ship id: {} finding best_direction".format(ship.id))

        if mode == DirectionHomeMode.RETREAT:
            points = self.get_points_retreat(ship, directions)
        elif mode == DirectionHomeMode.DEPOSIT:
            points = self.get_points_returning(ship, directions)

        if len(points) == 0:
            return Direction.Still

        best = max(points)

        logging.debug("best direction: {}".format(best.direction))

        return best.direction


    def get_points_retreat(self, ship, directions):
        """
        GET POINTS FOR RETREATING

        :param ship:
        :param directions: CLEAN POSSIBLE DIRECTIONS
        :return:
        """
        ## IF OTHER ARE UNSAFE, PICK THIS DIRECTION (STILL)
        points = [ RetreatPoints(shipyard=0, unsafe=1, potential_collision=-999, direction=Direction.Still) ]

        for direction in directions:
            destination = self.get_destination(ship, direction)

            shipyard = self.data.matrix.myShipyard[destination.y][destination.x]
            unsafe = self.data.matrix.unsafe[destination.y][destination.x]
            potential_collision = self.data.matrix.potential_ally_collisions[destination.y][destination.x]

            logging.debug("shipyard: {} unsafe: {} potential_collision: {} direction: {}".format(shipyard,
                                                                                                 unsafe,
                                                                                                 potential_collision,
                                                                                                 direction))
            c = RetreatPoints(shipyard, unsafe, potential_collision, direction)
            points.append(c)

        return points

    def get_points_returning(self, ship, directions):
        """
        GET POINTS FOR RETURNING

        :param ship:
        :param directions: CLEAN POSSIBLE DIRECTIONS
        :return:
        """
        ## IF OTHER ARE UNSAFE, PICK THIS DIRECTION (STILL)
        points = [ DepositPoints(unsafe=1, cost=-999, direction=Direction.Still) ]

        for direction in directions:
            destination = self.get_destination(ship, direction)

            unsafe = self.data.matrix.unsafe[destination.y][destination.x]
            cost = self.data.matrix.cost[destination.y][destination.x]

            logging.debug("unsafe: {} cost: {} direction: {}".format(unsafe, cost, direction))
            c = DepositPoints(unsafe, cost, direction)
            points.append(c)

        return points


    def get_directions_target(self, start, destination, size):
        """
        GET DIRECTION TOWARDS TARGET, TAKE WRAPPING INTO ACCOUNT

        :param start: START POSITION
        :param destination: DESTINATION POSITION
        :param size: MATRIX SIZE
        :return: LIST OF POSSIBLE DIRECTIONS TOWARD TARGET
        """

        def get_mirror_locations(start, destination, size):
            """
            GET MIRROR LOCATIONS, SHOULD BE 4 ALWAYS WITH WRAPPING

            :return: TUPLE OF LOCATIONS (PRODUCTS OF YS, XS)
            """
            if start.y > destination.y:
                ys = [destination.y, destination.y + size]
            elif start.y == destination.y:
                ys = [destination.y]
            else:
                ys = [destination.y, destination.y - size]

            if start.x > destination.x:
                xs = [destination.x, destination.x + size]
            elif start.x == destination.x:
                xs = [destination.x]
            else:
                xs = [destination.x, destination.x - size]

            return itertools.product(ys, xs)

        def get_closest_location(start, locations):
            """
            GET CLOSEST LOCATION
            BASED ON ALL MIRROR LOCATIONS

            :return: A TUPLE OF BEST LOCATION
            """
            closest = (9999, start)

            for dest in locations:
                dist = abs(dest[0] - start.y) + abs(dest[1] - start.x)
                closest = min((dist, dest), closest)

            return closest[1] ## THE BEST LOCATION


        all_locations = get_mirror_locations(start, destination, size)
        best_location = get_closest_location(start, all_locations)

        x, y = best_location[1], best_location[0]
        return GameMap._get_target_direction(start, Position(x, y))


    def get_destination(self, ship, direction):
        """
        GIVEN A SHIP AND DIRECTION, GET NORMALIZED (WRAP) POSITION

        :param ship:
        :param direction:
        :return: NORMALIZED POSITION
        """
        new_pos = ship.position + Position(direction[0], direction[1])
        x = new_pos.x % self.data.map_width
        y = new_pos.y % self.data.map_height
        return Position(x, y)