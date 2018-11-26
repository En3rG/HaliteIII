import numpy as np
import logging
from hlt.positionals import Position
from src.common.values import MyConstants, Matrix_val, Inequality
from hlt import constants
from src.common.print import print_matrix, print_heading
from src.common.matrix.functions import populate_manhattan, get_n_largest_values, get_distance_matrix, \
    get_average_manhattan, shift_matrix
from src.common.matrix.vectorized import myRound, myHarvestCounter, myHarvestArea, myTurnCounter
import abc
import copy
import sys


class Section():
    """
    GET A SECTION OF THE MATRIX PROVIDED
    GIVEN THE CENTER (POSITION) AND SIZE OF SECTION
    SECTION IS A SQUARE MATRIX
    ACTUAL SIZE OF SECTION IS ACTUALLY (SIZE * 2 + 1) by (SIZE * 2 + 1)

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


class Sectioned():
    def __init__(self, map_height, map_width):
        self.halite = np.zeros((map_height // MyConstants.SECTION_SIZE , map_width // MyConstants.SECTION_SIZE), dtype=np.int16)
        self.distances = {}  ## ONLY FILLED IN INIT


class Depletion():
    def __init__(self, map_height, map_width):
        self.harvest_turns = np.zeros((map_height, map_width), dtype=np.int16)
        self.shipyard_distances = np.zeros((map_height, map_width), dtype=np.int16)
        self.total_turns = np.zeros((map_height, map_width), dtype=np.int16)
        self.max_matrix = np.zeros((map_height, map_width), dtype=np.int16)
        self.max_matrix.fill(1)
        self.harvest_area = np.zeros((map_height, map_width), dtype=np.int16)


class Average():
    def __init__(self, map_height, map_width):
        self.manhattan = np.zeros((map_height, map_width), dtype=np.float16)
        self.top_10 = np.zeros((map_height, map_width), dtype=np.float16)


class Matrix():
    """
    CONTAINS ALL THE MATRICES
    """
    def __init__(self, map_height, map_width):
        self.halite = np.zeros((map_height, map_width), dtype=np.int16)
        self.top_halite = np.zeros((map_height, map_width), dtype=np.int16)
        self.distances = {} ## ONLY FILLED IN INIT
        self.myShipyard = np.zeros((map_height, map_width), dtype=np.int16)
        self.enemyShipyard = np.zeros((map_height, map_width), dtype=np.int16)
        self.myShips = np.zeros((map_height, map_width), dtype=np.int16)
        self.myShipsID = np.zeros((map_height, map_width), dtype=np.int16)
        self.enemyShips = np.zeros((map_height, map_width), dtype=np.int16)
        self.cost = None
        self.harvest = None
        self.influenced = np.zeros((map_height, map_width), dtype=np.int16)
        self.stuck = np.zeros((map_height, map_width), dtype=np.int16)
        self.safe = np.zeros((map_height, map_width), dtype=np.int16)
        self.safe.fill(1)  ## FILLED WITH 1, -1 FOR UNSAFE
        self.occupied = np.zeros((map_height, map_width), dtype=np.int16)
        self.potential_ally_collisions = np.zeros((map_height, map_width), dtype=np.int16)
        self.potential_enemy_collisions = np.zeros((map_height, map_width), dtype=np.int16)

        self.sectioned = Sectioned(map_height, map_width)

        self.average = Average(map_height, map_width)

        self.depletion = Depletion(map_height, map_width)


class Data(abc.ABC):
    def __init__(self, game):
        self.game = game
        self.me = game.me               ## MY PLAYER OBJECT
        self.my_id = game.me.id
        self.players = game.players     ## DICTIONARY OF Players, BASE ON PLAYER IDs
        self.game_map = game.game_map
        self.map_width = self.game_map.width
        self.map_height = self.game_map.height

        self.matrix = Matrix(self.map_height, self.map_width)


    @abc.abstractmethod  ## MUST BE DEFINED BY CHILD CLASS
    def update_matrix(self):
        """
        WILL CONTAIN WHICH MATRICES NEED TO BE UPDATED
        """
        pass


    def populate_halite(self):
        """
        POPULATE MATRIX WITH HALITE VALUES
        """
        halites = [ [ cell.halite_amount for cell in row ] for row in self.game_map._cells ]
        self.matrix.halite = np.array(halites, dtype=np.int16)


    def populate_myShipyard(self):
        """
        POPULATE MATRIX WITH ALLY_SHIPYARD.value WHERE MY SHIPYARD IS LOCATED
        """
        myShipyard_position = self.me.shipyard.position
        self.matrix.myShipyard[myShipyard_position.y][myShipyard_position.x] = Matrix_val.ONE


    def populate_enemyShipyard(self):
        """
        POPULATE MATRIX WITH ENEMY_SHIPYARD.value WHERE ENEMY SHIPYARDS ARE LOCATED
        """
        for id, player in self.players.items():
            if id != self.my_id:
                enemyShipyard_position = player.shipyard.position
                self.matrix.enemyShipyard[enemyShipyard_position.y][enemyShipyard_position.x] = Matrix_val.ONE


    def populate_myShips(self):
        """
        POPULATE MATRIX WITH ALLY_SHIP.value WHERE MY SHIPS ARE LOCATED
        """
        for ship in self.me.get_ships():
            self.matrix.myShips[ship.position.y][ship.position.x] = Matrix_val.ONE
            self.matrix.myShipsID[ship.position.y][ship.position.x] = ship.id
            self.matrix.occupied[ship.position.y][ship.position.x] = Matrix_val.OCCUPIED
            populate_manhattan(self.matrix.potential_ally_collisions, Matrix_val.POTENTIAL_COLLISION, ship.position,
                          MyConstants.DIRECT_NEIGHBOR_RADIUS, cummulative=True)

            if self.matrix.cost[ship.position.y][ship.position.x] > ship.halite_amount:
                self.matrix.stuck[ship.position.y][ship.position.x] = Matrix_val.ONE


    def populate_enemyShips_influenced(self):
        """
        POPULATE MATRIX WITH ENEMY_SHIP.value WHERE ENEMY SHIPS ARE LOCATED
        POPULATE MATRIX WITH ENEMY INFLUENCE
        POPULATE MATRIX WITH POTENTIAL ENEMY COLLISIONS
        """
        for id, player in self.players.items():
            if id != self.my_id:
                for ship in player.get_ships():
                    self.matrix.enemyShips[ship.position.y][ship.position.x] = Matrix_val.ONE

                    ## CANT USE FILL CIRCLE.  DISTANCE 4 NOT TECHNICALLY CIRCLE
                    # self.matrix.influenced = fill_circle(self.matrix.influenced,
                    #                                     center=ship.position,
                    #                                     radius=constants.INSPIRATION_RADIUS,
                    #                                     value=Matrix_val.INFLUENCED.value,
                    #                                     cummulative=False, override_edges=0)

                    populate_manhattan(self.matrix.influenced, Matrix_val.ONE, ship.position,
                                  constants.INSPIRATION_RADIUS, cummulative=True)
                    populate_manhattan(self.matrix.potential_enemy_collisions, Matrix_val.POTENTIAL_COLLISION, ship.position,
                                  MyConstants.DIRECT_NEIGHBOR_RADIUS, cummulative=True)


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


    def populate_sectioned_halite(self):
        """
        POPULATE SECTIONED HALITE (MyConstants.SECTION_SIZE x MyConstants.SECTION_SIZE)

        RECORD AVERAGE OF EACH SECTION
        """
        for y, row in enumerate(self.matrix.sectioned.halite):
            for x, col in enumerate(row):
                section = self.matrix.halite[
                          y * MyConstants.SECTION_SIZE:y * MyConstants.SECTION_SIZE + MyConstants.SECTION_SIZE,
                          x * MyConstants.SECTION_SIZE:x * MyConstants.SECTION_SIZE + MyConstants.SECTION_SIZE]
                sum = section.sum()
                average_halite = sum // (MyConstants.SECTION_SIZE * 2)

                self.matrix.sectioned.halite[y][x] = average_halite

        print_matrix("sectioned halite", self.matrix.sectioned.halite)


    def populate_sectioned_distances(self):
        """
        POPULATE DISTANCES OF EACH SECTIONS TO ONE ANOTHER

        self.matrix.sectioned.distances[curr_section][y][x] = distance

        :return:
        """
        height = (self.map_height // MyConstants.SECTION_SIZE) + 1  ## + 1 TO COUNT LAST ITEM FOR RANGE
        width = (self.map_width // MyConstants.SECTION_SIZE) + 1

        for r in range(height):
            for c in range(width):
                curr_section = (r, c)
                self.matrix.sectioned.distances[curr_section] = get_distance_matrix(curr_section, height, width)

                #print_matrix("Distances on {}".format(curr_section), self.matrix.sectioned.distances[curr_section])

    def populate_distances(self):
        """
        POPULATE DISTANCES OF EACH CELLS TO ONE ANOTHER

        self.matrix.distances[curr_section][y][x] = distance

        :return:
        """
        height = self.map_height + 1  ## + 1 TO COUNT LAST ITEM FOR RANGE
        width = self.map_width + 1

        curr_cell = (0, 0)
        base_matrix = get_distance_matrix(curr_cell, height, width)

        for r in range(height):
            for c in range(width):
                curr_cell = (r, c)
                ## THIS METHOD WILL TIME OUT (ALSO UNNECESSARY CALCULATIONS
                ## SINCE DISTANCE MATRIX IS PRETTY SIMILAR
                # self.matrix.distances[curr_cell] = get_distance_matrix(curr_cell, height, width)
                # print_matrix("Distances (1) on {}".format(curr_cell), self.matrix.distances[curr_cell])

                self.matrix.distances[curr_cell] = shift_matrix(r, c, base_matrix)
                # print_matrix("Distances (2) on {}".format(curr_cell), self.matrix.distances[curr_cell])


    def populate_average(self):
        """
        POPULATE AVERAGES
        """
        ## THE AVERAGE MANHATTAN OF EACH MAP CELL, BASED ON AVERAGE MANHATTAN DISTANCE
        for r in range(self.map_height):
            for c in range(self.map_width):
                loc = Position(c, r) ## Position(x, y)
                self.matrix.average.manhattan[r][c] = get_average_manhattan(self.matrix.halite, loc, MyConstants.AVERAGE_MANHATTAN_DISTANCE)

        ## POPULATE WHERE TOP N PLACES ARE BASED ON self.matrix.average.manhattan
        top_indexes = set()
        average_manhattan = copy.deepcopy(self.matrix.average.manhattan)
        for _ in range(MyConstants.TOP_N):  ## GET INDEXES OF TOP N
            top_1, ind = get_n_largest_values(average_manhattan, 1)
            loc = (ind[0][0], ind[1][0])
            position = Position(loc[1], loc[0]) ## Position(x, y)
            top_indexes.add(loc)
            populate_manhattan(average_manhattan, 0, position, MyConstants.AVERAGE_MANHATTAN_DISTANCE, cummulative=False)
        for ind in top_indexes:
            self.matrix.average.top_10[ind[0]][ind[1]] = self.matrix.average.manhattan[ind[0]][ind[1]]


    def populate_depletion(self):
        """
        POPULATE
        """
        ## POPULATE NUMBER OF TURNS TO HAVE HALITE <= DONT_HARVEST_BELOW
        self.matrix.depletion.harvest_turns =  myHarvestCounter(self.matrix.halite)

        ## POPULATE SHIPYARD DISTANCES
        start_tuple = (self.me.shipyard.position.y, self.me.shipyard.position.x)
        self.matrix.depletion.shipyard_distances = get_distance_matrix(start_tuple, self.map_height, self.map_width)

        ## POPULATE TOTAL NUMBER OF TURNS TO DEPLETE HALITE, INCLUDING TRAVELING THERE BACK AND FORTH
        self.matrix.depletion.total_turns = myTurnCounter(self.matrix.depletion.harvest_turns, self.matrix.depletion.shipyard_distances)

        ## POPULATE IF A GOOD HARVEST AREA
        max_num = np.max(self.matrix.depletion.total_turns)
        max_matrix = self.matrix.depletion.max_matrix * max_num
        self.matrix.depletion.harvest_area = myHarvestArea(max_matrix, self.matrix.depletion.total_turns)


    def populate_top_halite(self):
        """
        POPULATE TOP HALITE CELLS
        """
        num_cells = int(MyConstants.TOP_N_HALITE * (self.map_height * self.map_width))
        top, ind = get_n_largest_values(self.matrix.halite, num_cells)
        self.matrix.top_halite[ind] = 10


