import logging
import random
from hlt.game_map import GameMap
from hlt.positionals import Position
from hlt.positionals import Direction
import abc
import itertools
from src.common.values import DirectionHomeMode, MyConstants, Matrix_val
from src.common.matrix import move_populate_area, print_matrix
from src.common.points import RetreatPoints

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


    def get_direction_home(self, ship, home_position, mode=""):
        """
        GET DIRECTION TOWARDS SHIPYARD

        :param ship_position:
        :param home_position:
        :return: DIRECTION TO SHIPYARD POSITION
        """

        clean_choices = self.directions_home(ship, home_position)
        direction = self.best_direction_home(ship, clean_choices, mode)

        return direction


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


    def best_direction(self, ship, directions, mode=""):
        """
        USE POINT SYSTEM

        :param ship:
        :param directions:
        :param mode:
        :return:
        """
        logging.debug("Ship id: {} finding best_direction".format(ship.id))

        if mode == DirectionHomeMode.RETREAT:
            choices = self.get_choices_retreat(ship, directions)

        if len(choices) == 0:
            return Direction.Still

        best = max(choices)

        logging.debug("best direction: {}".format(best.direction))

        return best.direction


    def get_choices_retreat(self, ship, directions):
        choices = []
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
            choices.append(c)

        return choices


    def best_direction_home(self, ship, clean_directions, mode):
        """
        GET BEST DIRECTION, GIVEN THE CHOICES

        :param ship:
        :param clean_choices: CHOICES OF DIRECTIONS
        :param mode:
        :return:
        """
        # try: direction = random.choice(clean_choices)
        # except: direction = Direction.Still

        if mode == DirectionHomeMode.RETREAT:
            direction = self.pick_direction_home(ship, clean_directions, self.data.matrix.potential_ally_collisions, mode)
        elif mode == DirectionHomeMode.DEPOSIT:
            direction = self.pick_direction_home(ship, clean_directions, self.data.matrix.cost, mode)

        logging.debug("chosen direction: {}".format(direction))

        return direction


    def pick_direction_home(self, ship, directions, matrix, mode):
        """
        SELECT BEST DIRECTION

        IF RETREATING AND GOING TOWARDS SHIPYARD, BREAK OUT LOOP

        :param ship:
        :param directions:
        :param matrix: MATRIX WHERE VALUE WILL BE BASED ON
        :return: BEST DIRECTION
        """
        lowest = 99999
        best_direction = Direction.Still

        for direction in directions:
            destination = self.get_destination(ship, direction)

            if mode == DirectionHomeMode.RETREAT and destination == self.data.me.shipyard.position:
                best_direction = direction
                break

            val = matrix[destination.y][destination.x]
            occupied = self.data.matrix.unsafe[destination.y][destination.x] == Matrix_val.UNSAFE
            logging.debug("val {} destination {}".format(val, destination))

            if not occupied and val < lowest:
                lowest = val
                best_direction = direction

        return best_direction


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

            :return: TUPLE OF LOCATIONS
            """
            if start.y > destination.y:
                ys = [destination.y, destination.y + size]
            else:
                ys = [destination.y, destination.y - size]

            if start.x > destination.x:
                xs = [destination.x, destination.x + size]
            else:
                xs = [destination.x, destination.x - size]

            return itertools.product(ys, xs)

        def get_closest_location(start, locations):
            """
            GET CLOSEST LOCATION
            BASED ON ALL MIRROR LOCATIONS

            :return: TUPLE OF BEST LOCATION
            """
            closest = 9999999
            closest_location = None

            for dest in locations:
                dist = abs(dest[0] - start.y) + abs(dest[1] - start.x)
                if dist < closest:
                    closest = dist
                    closest_location = dest

            return closest_location


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