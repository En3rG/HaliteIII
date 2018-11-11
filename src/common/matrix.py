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
    :param x:
    :return:
    """
    if (x - int(x) >= 0.5):
        return np.ceil(x)
    else:
        return np.floor(x)

myRound = np.vectorize(rounder)


def print_matrix(name, matrix):
    np.set_printoptions(threshold=np.inf, linewidth=np.inf)  ## SET NUMPY PRINT THRESHOLD TO INFINITY
    logging.debug("Print matrix {}: {}".format(name, matrix))
    np.set_printoptions(threshold=10)  ## SET NUMPY PRINT THRESHOLD TO 10


class Section():
    """
    GET A SECTION OF THE MATRIX PROVIDED
    GIVEN THE CENTER (POSITION) AND SIZE OF SECTION
    SECTION IS A SQUARE MATRIX
    ACTUAL SIZE OF SECTION IS ACTUALLY SIZE * 2 + 1

    :param matrix: ORIGINAL MATRIX
    :param position: CENTER OF THE SECTION
    :param size: SIZE OF THE SECTION TO BE EXTRACTED
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


def fill_circle(array, center, radius, value, cummulative=False, override_edges=None):
    """
    MASK A CIRCLE ON THE ARRAY SPECIFIED WITH center, radius, and value PROVIDED
    """
    height = array.shape[0]
    width = array.shape[1]

    ## y IS JUST AN ARRAY OF 1xY (ROWS)
    ## x IS JUST AN ARRAY OF 1xX (COLS)
    y, x = np.ogrid[-center.y:height - center.y, -center.x:width - center.x]
    ## MASKS IS A HEIGHTxWIDTH ARRAY WITH TRUE INSIDE THE CIRCLE SPECIFIED

    if override_edges:
        mask = x * x + y * y <= radius * radius + radius * override_edges
    else:
        ## WHEN WANT TO BE MORE CIRCLE (DUE TO ROUNDING)
        mask = x * x + y * y <= radius * radius

    if cummulative:  ## VALUE KEEPS GETTING ADDED
        array[mask] += value
    else:
        array[mask] = value

    return array


class Matrix_distances():
    def __init__(self, map_height, map_width):
        self.matrix = np.zeros((map_height, map_width), dtype=np.int16)
        self.center = None      ## set at update_matrix


class Matrix():
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
        self.unsafe = np.zeros((map_height, map_width), dtype=np.int16)
        self.unsafe.fill(1)  ## FILLED WITH 1, -1 FOR UNSAFE


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
        self.matrix.myShipyard[myShipyard_position.y][myShipyard_position.x] = Matrix_val.OCCUPIED.value


    def populate_enemyShipyard(self):
        """
        POPULATE MATRIX WITH ENEMY_SHIPYARD.value WHERE ENEMY SHIPYARDS ARE LOCATED
        """
        for id, player in self.players.items():
            if id != self.my_id:
                enemyShipyard_position = player.shipyard.position
                self.matrix.enemyShipyard[enemyShipyard_position.y][enemyShipyard_position.x] = Matrix_val.OCCUPIED.value


    def populate_myShips(self):
        """
        POPULATE MATRIX WITH ALLY_SHIP.value WHERE MY SHIPS ARE LOCATED
        """
        for ship in self.me.get_ships():
            self.matrix.myShips[ship.position.y][ship.position.x] = Matrix_val.OCCUPIED.value
            self.matrix.myShipsID[ship.position.y][ship.position.x] = ship.id


    def populate_enemyShips_influenced(self):
        """
        POPULATE MATRIX WITH ENEMY_SHIP.value WHERE ENEMY SHIPS ARE LOCATED
        POPULATE MATRIX WITH ENEMY INFLUENCE
        """
        def populate_influence(matrix, loc):
            """
            POPULATE MATRIX INFLUENCE

            LOOPS THROUGH EACH OF THE LOCATION ONE BY ONE (BASED ON DISTANCE)
            NO EXTRA LOCATION IS PART OF THE LOOP

            :param matrix: self.matrix.influenced
            :param loc: ENEMY SHIP LOCATION
            :return:
            """
            dist = constants.INSPIRATION_RADIUS
            size, size = matrix.shape
            for y in range(-dist, dist + 1):
                for x in range(-dist + abs(y), dist - abs(y) + 1):
                    y_ = (y + loc.y) % size
                    x_ = (x + loc.x) % size
                    matrix[y_, x_] = 1

        for id, player in self.players.items():
            if id != self.my_id:
                for ship in player.get_ships():
                    self.matrix.enemyShips[ship.position.y][ship.position.x] = Matrix_val.OCCUPIED.value

                    ## CANT USE FILL CIRCLE.  DISTANCE 4 NOT TECHNICALLY CIRCLE
                    # self.matrix.influenced = fill_circle(self.matrix.influenced,
                    #                                     center=ship.position,
                    #                                     radius=constants.INSPIRATION_RADIUS,
                    #                                     value=Matrix_val.INFLUENCED.value,
                    #                                     cummulative=False, override_edges=0)

                    populate_influence(self.matrix.influenced, ship.position)


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
        self.matrix.unsafe[position.y][position.x] = Matrix_val.UNSAFE.value

