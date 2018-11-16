import logging
from hlt.game_map import GameMap
from hlt.positionals import Position
from hlt.positionals import Direction
import abc
import itertools
from src.common.values import DirectionHomeMode, MyConstants, Matrix_val
from src.common.matrix import move_populate_area, Section, print_matrix, get_index_highest_val


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
        logging.debug("ship id: {} ship position: {} shipyard position: {} clean_choices: {}".format(ship.id,
                                                                                                     ship.position,
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


    def get_highest_harvest_move(self, ship):
        """
        ACTUAL HARVEST MATRIX IS THE NEIGHBORING HARVEST VALUE MINUS LEAVING CURRENT CELL

        :param ship:
        :param harvest:
        :param cost:
        :return:
        """
        logging.debug("Getting highest harvest move for ship id: {}".format(ship.id))
        harvest = Section(self.data.matrix.harvest, ship.position, size=1)  ## SECTION OF HARVEST MATRIX
        leave_cost = self.data.matrix.cost[ship.position.y][ship.position.x]  ## COST TO LEAVE CURRENT CELL
        cost_matrix = MyConstants.DIRECT_NEIGHBORS * leave_cost  ## APPLY COST TO DIRECT NEIGHBORS
        harvest_matrix = harvest.matrix * MyConstants.DIRECT_NEIGHBORS_SELF  ## HARVEST MATRIX OF JUST NEIGHBORS AND SELF, REST 0
        actual_harvest = harvest_matrix - cost_matrix  ## DEDUCT LEAVE COST TO DIRECT NEIGHBORS
        unsafe = Section(self.data.matrix.unsafe, ship.position, size=1)  ## SECTION UNSAFE
        safe_harvest = actual_harvest * unsafe.matrix  ## UNSAFE WILL BE NEGATIVE SO WIL BE LOW PRIORITY

        max_index = get_index_highest_val(safe_harvest)

        if max_index == (0, 1):
            return Direction.North

        elif max_index == (1, 2):
            return Direction.East

        elif max_index == (2, 1):
            return Direction.South

        elif max_index == (1, 0):
            return Direction.West
        else:
            return Direction.Still





