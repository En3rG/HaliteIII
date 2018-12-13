import logging
from hlt.game_map import GameMap
from hlt.positionals import Position
from hlt.positionals import Direction
import abc
import itertools
from src.common.values import MoveMode, MyConstants, Matrix_val
from src.common.matrix.functions import move_populate_manhattan, get_index_highest_val
from src.common.matrix.data import Section
from src.movement.collision_prevention import avoid_collision_direction
from src.common.print import print_matrix



class Moves(abc.ABC):
    """
    BASE CLASS USED FOR MOVEMENT (RETREAT, DEPOSIT, HARVEST, EXPLORE, ETC)
    """
    def __init__(self, data, prev_data):
        self.data = data
        self.prev_data = prev_data


    def move_mark_unsafe(self, ship, direction):
        """
        GIVEN THE SHIP AND DIRECTION,
        POPULATE SAFE MATRIX, TAKING WRAPPING INTO ACCOUNT
        MOVE OCCUPIED TO DESTINATION
        UPDATE POTENTIAL ALLY COLLISION MATRIX (MOVE AREA TO DIRECTION)
        RECORD HALITE STAT
        REMOVE SHIP ID TO SHIP TO MOVE
        APPEND MOVE TO COMMAND QUEUE
        CHECK IF ANY SHIPS ARE BEING KICKED OUT
        REMOVE CURRENT SHIP FROM KICKED SHIPS (IF APPLICABLE)

        :param ship: SHIP OBJECT
        :param direction: MOVE DIRECTION
        :return: NONE
        """
        destination = self.get_destination(ship, direction)

        self.mark_unsafe(ship, destination)

        self.move_occupied(ship, direction)

        move_populate_manhattan(self.data.myMatrix.locations.potential_ally_collisions, ship.position, destination, MyConstants.DIRECT_NEIGHBOR_DISTANCE)

        self.data.halite_stats.record_data(ship, destination, self.data)

        if ship.id in self.data.mySets.ships_to_move: self.data.mySets.ships_to_move.remove(ship.id) ## PREVENT POTENTIAL KEY ERROR

        self.check_kicked(ship, direction)

        self.remove_kicked(ship)

        self.data.command_queue.append(ship.move(direction))
        logging.debug("=======>>>> Ship id: <<< {} >>> moving {} from {} to {}".format(ship.id, direction, ship.position, destination))


    def mark_unsafe(self, ship, position):
        """
        MARK POSITION PROVIDED WITH UNSAFE
        """
        self.data.myDicts.positions_taken.setdefault((position.y, position.x), set()).add(ship.id) ## KEY AS COORD, VALUE SHIP ID
                                                                                                   ## USED TO DETERMINE ALLY COLLISIONS
                                                                                                   ## IF MULTIPLE SHIP IDs WENT HERE
        self.data.myMatrix.locations.safe[position.y][position.x] = Matrix_val.UNSAFE


    def check_kicked(self, ship, direction):
        """
        CHECK IF THE SHIP WITH DIRECTION GIVEN WILL TAKE A SPOT WHERE ANOTHER SHIP IS ALREADY RESIDING
        THE OTHER SHIP MAY OR MAY NOT HAVE MOVE YET

        :param ship:
        :param direction:
        :return:
        """
        destination = self.get_destination(ship, direction)
        occupied = self.data.myMatrix.locations.occupied[destination.y][destination.x]
        if occupied < -1:
            shipID_kicked = self.data.myMatrix.locations.myShipsID[destination.y][destination.x]

            if shipID_kicked in self.data.mySets.ships_to_move:
                logging.debug("ship id {} added to ships kicked, by ship {}".format(shipID_kicked, ship.id))
                self.data.mySets.ships_kicked.add(shipID_kicked)
            else:
                logging.debug("ship id {} will not be added to ships kicked (moved already), by ship {}".format(shipID_kicked, ship.id))


    def remove_kicked(self, ship):
        """
        REMOVE SHIP ID FROM ships_kicked

        :param ship: SHIP OBJECT
        :return: NONE
        """
        if ship.id in self.data.mySets.ships_kicked:
            self.data.mySets.ships_kicked.remove(ship.id)


    def move_occupied(self, ship, direction):
        """
        MOVE OCCUPIED POSITION TOWARDS DIRECTION

        :param ship:
        :param direction:
        :return:
        """
        self.data.myMatrix.locations.occupied[ship.position.y][ship.position.x] += Matrix_val.ONE
        destination = self.get_destination(ship, direction)
        self.data.myMatrix.locations.occupied[destination.y][destination.x] += Matrix_val.OCCUPIED


    def best_direction(self, ship, directions=None, mode=""):
        """
        USING POINT SYSTEM
        GET BEST DIRECTION GIVEN CLEAN POSSIBLE DIRECTIONS TOWARD HOME/TARGET

        :param ship:
        :param directions: CHOICES OF DIRECTIONS
        :param mode:
        :return: BEST DIRECTION
        """
        logging.debug("Ship id: {} finding best_direction".format(ship.id))

        if mode == MoveMode.RETREAT:
            points = self.get_move_points_retreat(ship, directions)
        elif mode == MoveMode.DEPOSIT:
            points = self.get_move_points_returning(ship, directions)
        elif mode == MoveMode.HARVEST:
            points = self.get_move_points_harvest(ship)
        elif mode == MoveMode.EXPLORE:
            points = self.get_move_points_explore(ship, directions)
        elif mode == MoveMode.DEPART:
            points = self.get_move_points_depart(ship, directions)
        elif mode == MoveMode.BUILDING:
            points = self.get_move_points_building(ship, directions)
        elif mode == MoveMode.ATTACKING:
            points = self.get_move_points_attacking(ship, directions)
        elif mode == MoveMode.SUPPORTING:
            points = self.get_move_points_supporting(ship, directions)
        else:
            raise NotImplemented

        if len(points) == 0:
            return Direction.Still

        best = max(points)

        logging.debug("best direction: {}".format(best.direction))

        if best.safe == -1 and mode != MoveMode.RETREAT:
            logging.debug("Avoiding collision for ship {}!!!!!!! ships kicked: {}".format(ship.id, self.data.mySets.ships_kicked))
            #return self.get_highest_harvest_move(ship)
            return avoid_collision_direction(self, ship, directions)

        return best.direction


    def get_directions_target(self, ship, destination):
        """
        GET DIRECTIONS TOWARDS TARGET, TAKE WRAPPING INTO ACCOUNT

        :param ship:
        :param destination:
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

        start = ship.position
        size = self.data.game.game_map.width

        all_locations = get_mirror_locations(start, destination, size)
        closest_location = get_closest_location(start, all_locations)

        x, y = closest_location[1], closest_location[0]
        directions = GameMap._get_target_direction(start, Position(x, y))

        clean_directions = [x for x in directions if x != None]  ## CAN HAVE A NONE

        return clean_directions


    def get_destination(self, ship, direction):
        """
        GIVEN A SHIP AND DIRECTION, GET NORMALIZED (WRAP) POSITION

        :param ship:
        :param direction:
        :return: NORMALIZED POSITION
        """
        new_pos = ship.position + Position(direction[0], direction[1])
        x = new_pos.x % self.data.game.game_map.width
        y = new_pos.y % self.data.game.game_map.height
        return Position(x, y)


    ## NO LONGER USED
    # def get_highest_harvest_move(self, ship):
    #     """
    #     ACTUAL HARVEST MATRIX IS THE NEIGHBORING HARVEST VALUE MINUS LEAVING CURRENT CELL
    #
    #     :param ship:
    #     :param harvest:
    #     :param cost:
    #     :return:
    #     """
    #     logging.debug("Getting highest harvest move for ship id: {}".format(ship.id))
    #     harvest = Section(self.data.myMatrix.halite.harvest, ship.position, size=1)         ## SECTION OF HARVEST MATRIX
    #     leave_cost = self.data.myMatrix.halite.cost[ship.position.y][ship.position.x]       ## COST TO LEAVE CURRENT CELL
    #     cost_matrix = MyConstants.DIRECT_NEIGHBORS * leave_cost                             ## APPLY COST TO DIRECT NEIGHBORS
    #     harvest_matrix = harvest.matrix * MyConstants.DIRECT_NEIGHBORS_SELF                 ## HARVEST MATRIX OF JUST NEIGHBORS AND SELF, REST 0
    #     actual_harvest = harvest_matrix - cost_matrix                                       ## DEDUCT LEAVE COST TO DIRECT NEIGHBORS
    #     safe = Section(self.data.myMatrix.locations.safe, ship.position, size=1)            ## SECTION SAFE
    #     safe_harvest = actual_harvest * safe.matrix                                         ## UNSAFE WILL BE NEGATIVE SO WIL BE LOW PRIORITY
    #
    #     max_index = get_index_highest_val(safe_harvest)
    #
    #     if max_index == (0, 1):
    #         return Direction.North
    #
    #     elif max_index == (1, 2):
    #         return Direction.East
    #
    #     elif max_index == (2, 1):
    #         return Direction.South
    #
    #     elif max_index == (1, 0):
    #         return Direction.West
    #     else:
    #         return Direction.Still










