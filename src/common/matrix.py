import numpy as np
import logging
from hlt.positionals import Position
from src.common.values import MyConstants, Matrix_val
from hlt import constants
import abc

def rounder(x):
    """
    SINCE np.round() DOESNT ALWAYS ROUND UP XX.5
    MAKING MY OWN FUNCTION THEN np.vectorize IT

    :param x: EACH NUMBER FROM THE ARRAY
    :return: CEIL OR FLOOR OF THAT NUMBEER
    """
    if (x - int(x) >= 0.5):
        return np.ceil(x)
    else:
        return np.floor(x)

myRound = np.vectorize(rounder)


class Section():
    """
    GET A SECTION OF THE MATRIX PROVIDED
    GIVEN THE CENTER (POSITION) AND SIZE OF SECTION
    SECTION IS A SQUARE MATRIX
    ACTUAL SIZE OF SECTION IS ACTUALLY SIZE * 2 + 1

    :param matrix: ORIGINAL MATRIX
    :param position: CENTER OF THE SECTION
    :param size: SIZE OF THE SECTION TO BE EXTRACTED (FROM POSITION)
    :return: A MATRIX REPRESENTING THE SECTION EXTRACTED
    """
    def __init__(self, matrix, position, size):
        self.a = matrix
        self.position = position
        self.size = size

        self.matrix = self.get_section()
        self.center = Position(size, size)

    def get_section(self):

        h, w = self.a.shape
        rows = [i % h for i in range(self.position.y - self.size, self.position.y + self.size + 1)]
        cols = [i % w for i in range(self.position.x - self.size, self.position.x + self.size + 1)]

        return self.a[rows, :][:, cols]


# def fill_circle(array, center, radius, value, cummulative=False, override_edges=None):
#     """
#     MASK A CIRCLE ON THE ARRAY
#
#     CURRENTLY NOT USED (DELETE LATER)
#
#     :param array: ORIGINAL ARRAY
#     :param center: CENTER OF THE CIRCLE
#     :param radius: RADIUS OF THE CIRCLE
#     :param value: VALUE TO BE PLACED IN THE CIRCLE
#     :param cummulative: IF VALUE WILL BE ADDED TO EXISTING VALUE IN THAT INDEX
#     :param override_edges: IF A VALUE IS GIVEN, IT WILL HELP MAKE THE CIRCLE ROUNDER
#     :return: UPDATED ARRAY
#     """
#
#     height = array.shape[0]
#     width = array.shape[1]
#
#     ## y IS JUST AN ARRAY OF 1xY (ROWS)
#     ## x IS JUST AN ARRAY OF 1xX (COLS)
#     y, x = np.ogrid[-center.y:height - center.y, -center.x:width - center.x]
#     ## MASKS IS A HEIGHTxWIDTH ARRAY WITH TRUE INSIDE THE CIRCLE SPECIFIED
#
#     if override_edges:
#         mask = x * x + y * y <= radius * radius + radius * override_edges
#     else:
#         ## WHEN WANT TO BE MORE CIRCLE (DUE TO ROUNDING)
#         mask = x * x + y * y <= radius * radius
#
#     if cummulative:  ## VALUE KEEPS GETTING ADDED
#         array[mask] += value
#     else:
#         array[mask] = value
#
#     return array


class Matrix_distances():
    def __init__(self, map_height, map_width):
        self.matrix = np.zeros((map_height, map_width), dtype=np.int16)
        self.center = None      ## set at update_matrix


class Matrix():
    """
    CONTAINS ALL THE MATRICES
    """
    def __init__(self, map_height, map_width):
        self.halite = np.zeros((map_height, map_width), dtype=np.int16)
        self.myShipyard = np.zeros((map_height, map_width), dtype=np.int16)
        self.enemyShipyard = np.zeros((map_height, map_width), dtype=np.int16)
        self.myShips = np.zeros((map_height, map_width), dtype=np.int16)
        self.myShipsID = np.zeros((map_height, map_width), dtype=np.int16)
        self.enemyShips = np.zeros((map_height, map_width), dtype=np.int16)
        self.cost = None
        self.harvest = None
        self.distances = Matrix_distances(map_height, map_width)
        self.influenced = np.zeros((map_height, map_width), dtype=np.int16)
        self.safe = np.zeros((map_height, map_width), dtype=np.int16)
        self.safe.fill(1)  ## FILLED WITH 1, -1 FOR UNSAFE
        self.potential_ally_collisions = np.zeros((map_height, map_width), dtype=np.int16)
        self.potential_enemy_collisions = np.zeros((map_height, map_width), dtype=np.int16)


class Matrices(abc.ABC):
    def __init__(self, game):
        self.game = game
        self.me = game.me               ## MY PLAYER OBJECT
        self.my_id = game.me.id
        self.players = game.players     ## DICTIONARY OF Players, BASE ON PLAYER IDs
        self.game_map = game.game_map
        self.map_width = self.game_map.width
        self.map_height = self.game_map.height

        self.matrix = Matrix(self.map_height, self.map_width)


    @abc.abstractmethod                 ## MUST BE DEFINED BY CHILD CLASS
    def update_matrix(self):
        pass


    def populate_halite(self):
        """
        POPULATE MATRIX WITH HALITE VALUES
        """
        halites = [ [ cell.halite_amount for cell in row ] for row in self.game_map._cells]
        self.matrix.halite = np.array(halites, dtype=np.int16)


    def populate_myShipyard(self):
        """
        POPULATE MATRIX WITH ALLY_SHIPYARD.value WHERE MY SHIPYARD IS LOCATED
        """
        myShipyard_position = self.me.shipyard.position
        self.matrix.myShipyard[myShipyard_position.y][myShipyard_position.x] = Matrix_val.OCCUPIED


    def populate_enemyShipyard(self):
        """
        POPULATE MATRIX WITH ENEMY_SHIPYARD.value WHERE ENEMY SHIPYARDS ARE LOCATED
        """
        for id, player in self.players.items():
            if id != self.my_id:
                enemyShipyard_position = player.shipyard.position
                self.matrix.enemyShipyard[enemyShipyard_position.y][enemyShipyard_position.x] = Matrix_val.OCCUPIED


    def populate_myShips(self):
        """
        POPULATE MATRIX WITH ALLY_SHIP.value WHERE MY SHIPS ARE LOCATED
        """
        for ship in self.me.get_ships():
            self.matrix.myShips[ship.position.y][ship.position.x] = Matrix_val.OCCUPIED
            self.matrix.myShipsID[ship.position.y][ship.position.x] = ship.id
            populate_area(self.matrix.potential_ally_collisions, Matrix_val.POTENTIAL_COLLISION, ship.position,
                          MyConstants.DIRECT_NEIGHBOR_RADIUS, cummulative=True)


    def populate_enemyShips_influenced(self):
        """
        POPULATE MATRIX WITH ENEMY_SHIP.value WHERE ENEMY SHIPS ARE LOCATED
        POPULATE MATRIX WITH ENEMY INFLUENCE
        POPULATE MATRIX WITH POTENTIAL ENEMY COLLISIONS
        """
        for id, player in self.players.items():
            if id != self.my_id:
                for ship in player.get_ships():
                    self.matrix.enemyShips[ship.position.y][ship.position.x] = Matrix_val.OCCUPIED

                    ## CANT USE FILL CIRCLE.  DISTANCE 4 NOT TECHNICALLY CIRCLE
                    # self.matrix.influenced = fill_circle(self.matrix.influenced,
                    #                                     center=ship.position,
                    #                                     radius=constants.INSPIRATION_RADIUS,
                    #                                     value=Matrix_val.INFLUENCED.value,
                    #                                     cummulative=False, override_edges=0)

                    populate_area(self.matrix.influenced, Matrix_val.OCCUPIED, ship.position,
                                  constants.INSPIRATION_RADIUS, cummulative=True)
                    populate_area(self.matrix.potential_enemy_collisions, Matrix_val.POTENTIAL_COLLISION, ship.position,
                                  MyConstants.DIRECT_NEIGHBOR_RADIUS, cummulative=True)


    def populate_distances(self):
        """
        POPULATE MATRIX DISTANCES FROM THE CENTER
        IF THE MAP IS AN EVEN LENGTH, SUBTRACT 1 SO THAT THE CENTER IS EXACT
        """
        if self.map_width % 2 == 0: ## EVEN
            width = self.map_width - 1
        else: ## ODD
            width = self.map_width

        center = width // 2
        self.matrix.distances.center = center
        start = Position(center, center)

        for y in range(width):
            for x in range(width):
                destination = Position(x, y)
                self.matrix.distances.matrix[y][x] = self.game_map.calculate_distance(start, destination)


    def populate_cost(self):
        """
        POPULATE MATRIX COST
        """
        cost = self.matrix.halite * 0.1
        #self.matrix.cost = np.round(cost)           ## FYI, numpy.round IS UNBIASED FOR XX.5 (BY DESIGN)
        self.matrix.cost = myRound(cost)


    def populate_harvest(self):
        """
        POPULATE MATRIX HARVEST
        """
        harvest = self.matrix.halite * 0.25
        #self.matrix.harvest = np.round(harvest)     ## FYI, numpy.round IS UNBIASED FOR XX.5 (BY DESIGN)
        self.matrix.harvest = myRound(harvest)


    def mark_unsafe(self, position):
        """
        MARK POSITION PROVIDED WITH UNSAFE
        """
        self.matrix.safe[position.y][position.x] = Matrix_val.UNSAFE


def get_coord_closest(seek_val, value_matrix, distance_matrix):
    """
    GET CLOSESTS seek_val FROM SECTION PROVIDED

    :param seek_val: VALUE WE ARE LOOKING FOR
    :param value_matrix: MATRIX WITH VALUES
    :param distance_matrix: MATRIX THAT REPRESENTS ITS DISTANCE
    :return: VALUES/DISTANCES PASSED, MIN DISTANCE, VALUE WITH MINIMUM DISTANCE
    """
    ## GET ROW, COL INDICES FOR THE CONDITION
    r, c = np.where(value_matrix == seek_val)

    ## EXTRACT CORRESPONDING VALUES OF DISTANCES
    di = distance_matrix[r, c]

    if len(di) >= 1:
        min_di = di.min()

        ## GET INDICES (INDEXABLE INTO r,c) CORRESPONDING TO LOWEST DISTANCE
        ld_indx = np.flatnonzero(di == min_di)

        ## GETTING CLOSEST seek_val, MAX NOT NECESSARY??
        ## GET MAX INDEX (BASED OFF v) OUT OF THE SELECTED INDICES
        max_idx = value_matrix[r[ld_indx], c[ld_indx]].argmax()

        ## INDEX INTO r,c WITH THE LOWEST DIST INDICES AND
        ## FROM THOSE SELECT MAXED ONE BASED OF VALUE
        return (r[ld_indx][max_idx], c[ld_indx][max_idx]), min_di, value_matrix[r[ld_indx][max_idx], c[ld_indx][max_idx]]

    else:
        ## NO seek_val FOUND
        return None, None, None


def populate_area(matrix, val, loc, dist, cummulative=False):
    """
    POPULATE AREA IN MATRIX PROVIDED (BASED ON DISTANCE FROM ORIGIN OR LOC)

    LOOPS THROUGH EACH OF THE LOCATION ONE BY ONE (BASED ON DISTANCE)
    NO EXTRA LOCATION IS PART OF THE LOOP

    :param matrix: MATRIX TO BE POPULATED
    :param val: VALUE TO ADD IN MATRIX
    :param loc: SHIP LOCATION
    :return:
    """
    size, size = matrix.shape
    for y in range(-dist, dist + 1):
        for x in range(-dist + abs(y), dist - abs(y) + 1):
            y_ = (y + loc.y) % size
            x_ = (x + loc.x) % size

            if cummulative:
                matrix[y_, x_] += val
            else:
                matrix[y_, x_] = val


def move_populate_area(matrix, old_loc, new_loc, dist):
    """
    MOVE POPULATE AREA IN MATRIX PROVIDED FROM OLD LOC TO NEW LOC

    LOOPS THROUGH EACH OF THE LOCATION ONE BY ONE (BASED ON DISTANCE)
    NO EXTRA LOCATION IS PART OF THE LOOP

    :param matrix: MATRIX TO BE POPULATED
    :param old_loc: OLD LOCATION TO BE DEPOPULATED
    :param new_loc: NEW LOCATION TO BE POPULATED
    :param dist:
    :param cummulative:
    :return:
    """
    ## REMOVE FROM OLD LOCATION
    size, size = matrix.shape
    for y in range(-dist, dist + 1):
        for x in range(-dist + abs(y), dist - abs(y) + 1):
            y_ = (y + old_loc.y) % size
            x_ = (x + old_loc.x) % size

            matrix[y_, x_] -= 1 ## REMOVE VALUE

    ## ADD TO NEW LOCATION
    size, size = matrix.shape
    for y in range(-dist, dist + 1):
        for x in range(-dist + abs(y), dist - abs(y) + 1):
            y_ = (y + new_loc.y) % size
            x_ = (x + new_loc.x) % size

            matrix[y_, x_] += 1 ## ADD VALUE


def get_index_highest_val(matrix):
    """
    GET INDEX OF HIGHEST VALUE IN MATRIX

    :param matrix:
    :return: INDEX OF HIGHEST VALUE
    """
    return np.unravel_index(np.argmax(matrix, axis=None), matrix.shape)