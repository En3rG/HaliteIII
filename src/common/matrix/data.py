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
#     CURRENTLY NOT USED (DELETE LATER!!!!!)
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
    """
    MAP DIVIDED INTO SECTIONS

    OBSOLETE????
    """
    def __init__(self, map_height, map_width):
        self.halite = np.zeros((map_height // MyConstants.SECTION_SIZE , map_width // MyConstants.SECTION_SIZE), dtype=np.int16)
        self.distances = {}  ## ONLY FILLED IN INIT


class Depletion():
    """
    USED TO ANALYZE HOW MANY TURNS TO DEPLETE THE HALITE IN THE ENTIRE MAP

    OBSOLETE????
    """
    def __init__(self, map_height, map_width):
        self.harvest_turns = np.zeros((map_height, map_width), dtype=np.int16)
        self.shipyard_distances = np.zeros((map_height, map_width), dtype=np.int16)
        self.total_turns = np.zeros((map_height, map_width), dtype=np.int16)
        self.max_matrix = np.zeros((map_height, map_width), dtype=np.int16)
        self.max_matrix.fill(1)
        self.harvest_area = np.zeros((map_height, map_width), dtype=np.int16)


class CellAverage():
    """
    USED TO GET THE AVERAGE HALITE PER CELL IN THE MAP
    BASED ON THE MANHATTAN DISTANCE DEFINED IN COMMON VALUES
    """
    def __init__(self, map_height, map_width):
        self.manhattan = np.zeros((map_height, map_width), dtype=np.float16)
        self.top_N = np.zeros((map_height, map_width), dtype=np.float16)


class Halite():
    def __init__(self, map_height, map_width):
        self.amount = np.zeros((map_height, map_width), dtype=np.int16)
        self.top_amount = np.zeros((map_height, map_width), dtype=np.int16)
        self.cost = None
        self.harvest = None


class Locations():
    def __init__(self, map_height, map_width):
        ## SHIPYARDS
        self.myShipyard = np.zeros((map_height, map_width), dtype=np.int16)
        self.enemyShipyard = np.zeros((map_height, map_width), dtype=np.int16)

        ## SHIPYARDS/DOCKS
        self.myDocks = np.zeros((map_height, map_width), dtype=np.int16)
        self.enemyDocks = np.zeros((map_height, map_width), dtype=np.int16)

        ## SHIPS
        self.myShips = np.zeros((map_height, map_width), dtype=np.int16)
        self.myShipsID = np.zeros((map_height, map_width), dtype=np.int16)
        self.myShipsID.fill(-1) ## CANT FIND SHIP ID 0 IF ZEROES
        self.enemyShips = np.zeros((map_height, map_width), dtype=np.int16)
        self.enemyShipsID = np.zeros((map_height, map_width), dtype=np.int16)
        self.enemyShipsID.fill(-1)  ## CANT FIND SHIP ID 0 IF ZEROES

        self.influenced = np.zeros((map_height, map_width), dtype=np.int16)

        self.stuck = np.zeros((map_height, map_width), dtype=np.int16)

        self.safe = np.zeros((map_height, map_width), dtype=np.int16)
        self.safe.fill(1)  ## FILLED WITH 1, -1 FOR UNSAFE

        self.occupied = np.zeros((map_height, map_width), dtype=np.int16)

        self.potential_ally_collisions = np.zeros((map_height, map_width), dtype=np.int16)
        self.potential_enemy_collisions = np.zeros((map_height, map_width), dtype=np.int16)

        self.dock_placement = np.zeros((map_height, map_width), dtype=np.int16)


class Matrix():
    """
    CONTAINS ALL THE MATRICES
    """
    def __init__(self, map_height, map_width):
        self.halite = Halite(map_height, map_width)
        self.distances = {} ## ONLY FILLED IN INIT
        self.locations = Locations(map_height, map_width)
        self.sectioned = Sectioned(map_height, map_width)
        self.cell_average = CellAverage(map_height, map_width)
        self.depletion = Depletion(map_height, map_width)


class MySets():
    def __init__(self, game):
        self.ships_all = set(game.me._ships.keys())        ## ALL SHIPS
        self.ships_to_move = set(game.me._ships.keys())    ## SHIPS TO MOVE
        self.ships_returning = set()                            ## SHIPS RETURNING HALITE
        self.ships_kicked = set()
        self.ships_died = set()
        self.ships_ally_collision = set()
        self.ships_enemy_collision = set()
        self.dock_positions = set()



class MyVars():
    def __init__(self):
        self.total_halite = 0
        self.average_halite = 0
        self.isBuilding = False
        self.canBuild = False
        self.canSpawn = False


class MyDicts():
    def __init__(self):
        self.players_halite = {}
        self.positions_taken = {}


class HaliteInfo():
    def __init__(self):
        self.halite_amount = 0
        self.halite_carried = 0


class Data(abc.ABC):
    def __init__(self, game):
        self.game = game
        self.myVars = MyVars()
        self.myDicts = MyDicts()
        self.mySets = MySets(game)
        self.myMatrix = Matrix(self.game.game_map.height, self.game.game_map.width)


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
        halites = [ [ cell.halite_amount for cell in row ] for row in self.game.game_map._cells ]
        self.myMatrix.halite.amount = np.array(halites, dtype=np.int16)

        self.myVars.total_halite = self.myMatrix.halite.amount.sum()


    def populate_myShipyard_docks(self):
        """
        POPULATE MY SHIPYARD POSITION AND ALL DOCKS POSITION
        """
        ## SHIPYARD
        myShipyard_position = self.game.me.shipyard.position
        self.myMatrix.locations.myShipyard[myShipyard_position.y][myShipyard_position.x] = Matrix_val.ONE

        ## DOCKS
        self.mySets.dock_positions.add((myShipyard_position.y, myShipyard_position.x))
        self.myMatrix.locations.myDocks[myShipyard_position.y][myShipyard_position.x] = Matrix_val.ONE

        for dropoff in self.game.me.get_dropoffs():
            self.mySets.dock_positions.add((dropoff.position.y, dropoff.position.x))
            self.myMatrix.locations.myDocks[dropoff.position.y][dropoff.position.x] = Matrix_val.ONE


    def populate_enemyShipyard_docks(self):
        """
        POPULATE ENEMY SHIPYARD POSITION AND ALL DOCKS POSITION
        """
        for id, player in self.game.players.items():
            if id != self.game.me.id:
                ## SHIPYARDS
                enemyShipyard_position = player.shipyard.position
                self.myMatrix.locations.enemyShipyard[enemyShipyard_position.y][enemyShipyard_position.x] = Matrix_val.ONE

                ## DOCKS
                self.myMatrix.locations.enemyDocks[enemyShipyard_position.y][enemyShipyard_position.x] = Matrix_val.ONE

                for dropoff in player.get_dropoffs():
                    self.myMatrix.locations.enemyDocks[dropoff.position.y][dropoff.position.x] = Matrix_val.ONE


    def populate_myShips(self):
        """
        POPULATE MATRIX LOCATIONS OF MY SHIP AND ITS IDs
        GATHER HALITE INFO AS WELL
        POPULATE POTENTIAL COLLISION MATRIX
        POPULATE STUCK SHIPS
        """
        self.myDicts.players_halite[self.game.my_id] = HaliteInfo()
        self.myDicts.players_halite[self.game.my_id].halite_amount = self.game.me.halite_amount

        for ship in self.game.me.get_ships():
            self.myDicts.players_halite[self.game.my_id].halite_carried += ship.halite_amount
            self.myMatrix.locations.myShips[ship.position.y][ship.position.x] = Matrix_val.ONE
            self.myMatrix.locations.myShipsID[ship.position.y][ship.position.x] = ship.id
            self.myMatrix.locations.occupied[ship.position.y][ship.position.x] = Matrix_val.OCCUPIED
            populate_manhattan(self.myMatrix.locations.potential_ally_collisions,
                               Matrix_val.POTENTIAL_COLLISION,
                               ship.position,
                               MyConstants.DIRECT_NEIGHBOR_RADIUS,
                               cummulative=True)

            ## POPULATE STUCK SHIPS
            if self.myMatrix.halite.cost[ship.position.y][ship.position.x] > ship.halite_amount:
                self.myMatrix.locations.stuck[ship.position.y][ship.position.x] = Matrix_val.ONE


    def populate_enemyShips_influenced(self):
        """
        POPULATE MATRIX LOCATION OF ENEMY SHIPS AND ITS IDs
        GATHER HALITE INFO AS WELL
        POPULATE MATRIX WITH ENEMY INFLUENCE
        POPULATE MATRIX WITH POTENTIAL ENEMY COLLISIONS
        """
        for id, player in self.game.players.items():
            if id != self.game.me.id:
                self.myDicts.players_halite[id] = HaliteInfo()
                self.myDicts.players_halite[id].halite_amount = player.halite_amount

                for ship in player.get_ships():
                    self.myDicts.players_halite[id].halite_carried += ship.halite_amount
                    self.myMatrix.locations.enemyShips[ship.position.y][ship.position.x] = Matrix_val.ONE
                    self.myMatrix.locations.enemyShipsID[ship.position.y][ship.position.x] = ship.id

                    ## CANT USE FILL CIRCLE.  DISTANCE 4 NOT TECHNICALLY CIRCLE
                    # self.myMatrix.locations.influenced = fill_circle(self.myMatrix.locations.influenced,
                    #                                     center=ship.position,
                    #                                     radius=constants.INSPIRATION_RADIUS,
                    #                                     value=Matrix_val.INFLUENCED.value,
                    #                                     cummulative=False, override_edges=0)

                    populate_manhattan(self.myMatrix.locations.influenced,
                                       Matrix_val.ONE,
                                       ship.position,
                                       constants.INSPIRATION_RADIUS,
                                       cummulative=True)
                    populate_manhattan(self.myMatrix.locations.potential_enemy_collisions,
                                       Matrix_val.POTENTIAL_COLLISION,
                                       ship.position,
                                       MyConstants.DIRECT_NEIGHBOR_RADIUS,
                                       cummulative=True)


    def populate_cost(self):
        """
        POPULATE MATRIX COST TO LEAVE EACH CELL
        """
        cost = self.myMatrix.halite.amount * 0.1
        #self.myMatrix.halite.cost = np.round(cost)           ## FYI, numpy.round IS UNBIASED FOR XX.5 (BY DESIGN)
        self.myMatrix.halite.cost = myRound(cost)


    def populate_harvest(self):
        """
        POPULATE MATRIX HARVEST, IF WE STAY STILL IN EACH CELL FOR A SINGLE TURN
        DOES NOT CONSIDER INFLUENCE
        """
        harvest = self.myMatrix.halite.amount * 0.25
        #self.myMatrix.halite.harvest = np.round(harvest)     ## FYI, numpy.round IS UNBIASED FOR XX.5 (BY DESIGN)
        self.myMatrix.halite.harvest = myRound(harvest)


    def populate_sectioned_halite(self):
        """
        POPULATE SECTIONED HALITE (MyConstants.SECTION_SIZE x MyConstants.SECTION_SIZE)

        RECORD AVERAGE OF EACH SECTION

        OBSOLETE???? NO LONGER USED
        """
        for y, row in enumerate(self.myMatrix.sectioned.halite):
            for x, col in enumerate(row):
                section = self.myMatrix.halite.amount[
                          y * MyConstants.SECTION_SIZE:y * MyConstants.SECTION_SIZE + MyConstants.SECTION_SIZE,
                          x * MyConstants.SECTION_SIZE:x * MyConstants.SECTION_SIZE + MyConstants.SECTION_SIZE]
                sum = section.sum()
                average_halite = sum // (MyConstants.SECTION_SIZE * 2)

                self.myMatrix.sectioned.halite[y][x] = average_halite

        print_matrix("sectioned halite", self.myMatrix.sectioned.halite)


    def populate_sectioned_distances(self):
        """
        POPULATE DISTANCES OF EACH SECTIONS TO ONE ANOTHER

        self.myMatrix.sectioned.distances[curr_section][y][x] = distance

        OBSOLETE????? NO LONGER USED
        """
        height = (self.game.game_map.height // MyConstants.SECTION_SIZE) + 1  ## + 1 TO COUNT LAST ITEM FOR RANGE
        width = (self.game.game_map.width // MyConstants.SECTION_SIZE) + 1

        for r in range(height):
            for c in range(width):
                curr_section = (r, c)
                self.myMatrix.sectioned.distances[curr_section] = get_distance_matrix(curr_section, height, width)

                #print_matrix("Distances on {}".format(curr_section), self.myMatrix.sectioned.distances[curr_section])


    def populate_cell_distances(self):
        """
        POPULATE DISTANCES OF EACH CELLS TO ONE ANOTHER

        self.myMatrix.distances[curr_section][y][x] = distance
        """
        height = self.game.game_map.height
        width = self.game.game_map.width

        curr_cell = (0, 0)
        base_matrix = get_distance_matrix(curr_cell, height, width)

        for r in range(height + 1):
            for c in range(width + 1):
                curr_cell = (r, c)
                ## THIS METHOD WILL TIME OUT (ALSO UNNECESSARY CALCULATIONS
                ## SINCE DISTANCE MATRIX IS PRETTY SIMILAR
                # self.myMatrix.distances[curr_cell] = get_distance_matrix(curr_cell, height, width)
                # print_matrix("Distances (1) on {}".format(curr_cell), self.myMatrix.distances[curr_cell])

                self.myMatrix.distances[curr_cell] = shift_matrix(r, c, base_matrix)
                # print_matrix("Distances (2) on {}".format(curr_cell), self.myMatrix.distances[curr_cell])


    def populate_cell_averages(self):
        """
        POPULATE AVERAGES OF EACH CELL BASED ON DISTANCE
        """
        ## THE AVERAGE MANHATTAN OF EACH MAP CELL, BASED ON AVERAGE MANHATTAN DISTANCE
        for r in range(self.game.game_map.height):
            for c in range(self.game.game_map.width):
                loc = Position(c, r) ## Position(x, y)
                self.myMatrix.cell_average.manhattan[r][c] = get_average_manhattan(self.myMatrix.halite.amount,
                                                                                 loc,
                                                                                 MyConstants.AVERAGE_MANHATTAN_DISTANCE)


    def populate_depletion(self):
        """
        POPULATE
        """
        ## POPULATE NUMBER OF TURNS TO HAVE HALITE <= DONT_HARVEST_BELOW
        self.myMatrix.depletion.harvest_turns =  myHarvestCounter(self.myMatrix.halite.amount)

        ## POPULATE SHIPYARD DISTANCES
        start_tuple = (self.game.me.shipyard.position.y, self.game.me.shipyard.position.x)
        self.myMatrix.depletion.shipyard_distances = get_distance_matrix(start_tuple, self.game.game_map.height, self.game.game_map.width)

        ## POPULATE TOTAL NUMBER OF TURNS TO DEPLETE HALITE, INCLUDING TRAVELING THERE BACK AND FORTH
        self.myMatrix.depletion.total_turns = myTurnCounter(self.myMatrix.depletion.harvest_turns, self.myMatrix.depletion.shipyard_distances)

        ## POPULATE IF A GOOD HARVEST AREA
        max_num = np.max(self.myMatrix.depletion.total_turns)
        max_matrix = self.myMatrix.depletion.max_matrix * max_num
        self.myMatrix.depletion.harvest_area = myHarvestArea(max_matrix, self.myMatrix.depletion.total_turns)


    def populate_top_halite(self):
        """
        POPULATE TOP HALITE CELLS
        LIMIT TO LOCAL AREA WITHIN THE FIRST 100 MOVES
        """
        ## ORIGINAL
        top_num_cells = int(MyConstants.TOP_N_HALITE * (self.game.game_map.height * self.game.game_map.width))
        top, ind = get_n_largest_values(self.myMatrix.halite.amount, top_num_cells)
        self.myMatrix.halite.top_amount[ind] = Matrix_val.TEN

        ## USED WHEN THE TOP HALITE PERCENTAGE IS LOW (< 2%)
        # top_num_cells = int(MyConstants.TOP_N_HALITE * (self.game.game_map.height * self.game.game_map.width))
        # if top_num_cells < len(self.mySets.ships_all):
        #     top_num_cells = len(self.mySets.ships_all)
        # top, ind = get_n_largest_values(self.myMatrix.halite.amount, top_num_cells)
        # self.myMatrix.halite.top_amount[ind] = Matrix_val.TEN

        ## LIMITING EARLY GAME TO STAY CLOSE BY
        ## SEEMS BETTER TO LIMIT BUILDING BASED NUMBER OF SHIPS
        # if self.game.turn_number < MyConstants.EARLY_GAME_TURNS:
        #     mask = np.zeros((self.game.game_map.height, self.game.game_map.width), dtype=np.int16)
        #     populate_manhattan(mask, 1, self.game.me.shipyard.position, MyConstants.MIN_DIST_BTW_DOCKS, cummulative=False)
        #     top_num_cells = int(MyConstants.TOP_N_HALITE_EARLY_GAME * (4 * MyConstants.MIN_DIST_BTW_DOCKS))
        #     matrix_halite = mask * self.myMatrix.halite.amount
        #     top, ind = get_n_largest_values(matrix_halite, top_num_cells)
        #     self.myMatrix.halite.top_amount[ind] = Matrix_val.TEN
        #     print_matrix("test", self.myMatrix.halite.top_amount)
        # else:
        #     top_num_cells = int(MyConstants.TOP_N_HALITE * (self.game.game_map.height * self.game.game_map.width))
        #     top, ind = get_n_largest_values(self.myMatrix.halite.amount, top_num_cells)
        #     self.myMatrix.halite.top_amount[ind] = Matrix_val.TEN


    def get_average_halite(self):
        self.myVars.average_halite = int(np.average(self.myMatrix.halite.amount))

        logging.debug("Average Halite: {} Average Harvest: {}".format(self.myVars.average_halite, self.myVars.average_halite * 0.25))


    def update_dock_placement(self):
        """
        UPDATE DOCK PLACEMENT TO EXCLUDE ENEMY DOCKS/SHIPYARDS
        """
        r, c = np.where(self.myMatrix.locations.enemyDocks == Matrix_val.ONE)
        self.init_data.myMatrix.locations.dock_placement[r, c] = 0


    def set_spawn_build_time(self):
        """
        SET SPAWNING TO TRUE IF TURN NUMBER IS BELOW THE MAX TURN PERCENT (BASED ON MAP SIZE AND NUM PLAYERS)
        ALSO BASED ON RATIO OF REMAINING HALITE FROM TOTAL STARTING VALUE
        """

        max_turn_percent = None

        if len(self.game.players) == 2:
            if self.game.game_map.height == 32:
                max_turn_percent = MyConstants.STOP_SPAWNING_2P_32
            elif self.game.game_map.height == 40:
                max_turn_percent = MyConstants.STOP_SPAWNING_2P_40
            elif self.game.game_map.height == 48:
                max_turn_percent = MyConstants.STOP_SPAWNING_2P_48
            elif self.game.game_map.height == 56:
                max_turn_percent = MyConstants.STOP_SPAWNING_2P_56
            elif self.game.game_map.height == 64:
                max_turn_percent = MyConstants.STOP_SPAWNING_2P_64

        else: ## 4 PLAYERS
            if self.game.game_map.height == 32:
                max_turn_percent = MyConstants.STOP_SPAWNING_4P_32
            elif self.game.game_map.height == 40:
                max_turn_percent = MyConstants.STOP_SPAWNING_4P_40
            elif self.game.game_map.height == 48:
                max_turn_percent = MyConstants.STOP_SPAWNING_4P_48
            elif self.game.game_map.height == 56:
                max_turn_percent = MyConstants.STOP_SPAWNING_4P_56
            elif self.game.game_map.height == 64:
                max_turn_percent = MyConstants.STOP_SPAWNING_4P_64

        ratio_left = self.myVars.total_halite / self.starting_halite

        self.myVars.canSpawn = self.game.turn_number <= constants.MAX_TURNS * max_turn_percent \
                        and ratio_left > MyConstants.STOP_SPAWNING_HALITE_LEFT

        self.myVars.canBuild = ratio_left > MyConstants.STOP_BUILDING_HALITE_LEFT






