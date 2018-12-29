import numpy as np
import logging
from hlt.positionals import Position
from src.common.values import MyConstants, Matrix_val, Inequality
from hlt import constants
from src.common.matrix.functions import populate_manhattan, get_n_largest_values, get_distance_matrix, \
    get_average_manhattan, shift_matrix
from src.common.matrix.vectorized import myRound, myBonusArea, myMinDockDistances
from src.common.orderedSet import OrderedSet
from src.common.print import print_matrix
import copy
import abc


class CellAverage():
    """
    USED TO GET THE AVERAGE HALITE PER CELL IN THE MAP
    BASED ON THE MANHATTAN DISTANCE DEFINED IN COMMON VALUES
    USED FOR DOCK PLACEMENT
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
        self.bonus = np.zeros((map_height, map_width), dtype=np.int16)
        self.harvest_with_bonus = None


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
        self.myShipsID.fill(-1)                                                                                         ## CANT FIND SHIP ID 0 IF ZEROES
        self.enemyShips = np.zeros((map_height, map_width), dtype=np.int16)
        self.enemyShipsID = np.zeros((map_height, map_width), dtype=np.int16)
        self.enemyShipsID.fill(-1)
        self.enemyShipsOwner = np.zeros((map_height, map_width), dtype=np.int16)
        self.enemyShipsOwner.fill(-1)
        self.shipCargo = np.zeros((map_height, map_width), dtype=np.int16)
        self.enemyCargo = np.zeros((map_height, map_width), dtype=np.int16)

        ## ATTACK
        self.engage_enemy = {}
        for i in range(1, MyConstants.ENGAGE_ENEMY_DISTANCE + 1):                                                       ## WHEN i IS 1, MEANS RIGHT NEXT TO ENEMY
            self.engage_enemy[i] = np.zeros((map_height, map_width), dtype=np.int16)

        self.engage_influence = np.zeros((map_height, map_width), dtype=np.int16)

        self.influenced = np.zeros((map_height, map_width), dtype=np.int16)

        self.stuck = np.zeros((map_height, map_width), dtype=np.int16)

        self.safe = np.zeros((map_height, map_width), dtype=np.int16)
        self.safe.fill(1)                                                                                               ## FILLED WITH 1, -1 FOR UNSAFE

        ## OCCUPIED IS DIFFERENT FROM MYSHIPS LOCATIONS BECAUSE IT GETS UPDATED
        ## AS THE SHIP MOVES, WHERE AS MYSHIPS IS THE STARTING LOCATIONS OF THE SHIPS
        self.occupied = np.zeros((map_height, map_width), dtype=np.int16)

        self.potential_ally_collisions = np.zeros((map_height, map_width), dtype=np.int16)
        self.potential_enemy_collisions = np.zeros((map_height, map_width), dtype=np.int16)

        self.dock_placement = np.zeros((map_height, map_width), dtype=np.int16)


class Distances():
    """
    CONTAINS DISTANCES MATRIXES
    """
    def __init__(self, map_height, map_width):
        self.cell = {}                                                                                                  ## ONLY FILLED IN INIT
        self.closest_dock = None


class Matrix():
    """
    CONTAINS ALL THE MATRICES
    """
    def __init__(self, map_height, map_width):
        self.halite = Halite(map_height, map_width)
        self.distances = Distances(map_height, map_width)
        self.locations = Locations(map_height, map_width)
        self.cell_average = CellAverage(map_height, map_width)
        self.dock_averages = np.zeros((map_height, map_width), dtype=np.int16)

        ## NO LONGER USED
        # self.sectioned = Sectioned(map_height, map_width)
        # self.depletion = Depletion(map_height, map_width)


class MySets():
    def __init__(self, game):
        self.ships_all = OrderedSet(game.me._ships.keys())                                                              ## ALL SHIPS
        self.ships_to_move = OrderedSet(sorted(game.me._ships.keys()))                                                  ## SHIPS TO MOVE (SORTING TO MATCH ORDER ONLINE)
        self.ships_returning = OrderedSet()                                                                             ## SHIPS RETURNING HALITE
        self.ships_kicked = OrderedSet()
        self.ships_died = set()
        self.ships_ally_collision = set()
        self.ships_enemy_collision = set()
        self.ships_building = set()
        self.dock_coords = set()


class MyVars():
    def __init__(self, data, game):
        self.ratio_left_halite = 0
        self.total_halite = 0
        self.average_halite = 0
        self.median_halite = 0
        self.harvest_percentile = 0
        self.isBuilding = False
        self.dontSpawn = False
        self.support_gain_ratio = 1.20 if (len(game.players) == 2) else 1.20                                            ## RATIO OF GAIN BEFORE SUPPORTING


class MyDicts():
    def __init__(self):
        self.players_halite = {}
        self.positions_taken = {}
        self.explore_ship = {}
        self.explore_enemy_ship = {}
        self.ships_building_dock = {}

class MyLists():
    def __init__(self):
        self.explore_target = []
        self.enemy_target = []


class HaliteInfo():
    def __init__(self):
        self.halite_amount = 0
        self.halite_carried = 0


class Data(abc.ABC):
    def __init__(self, game):
        self.game = game
        self.mySets = MySets(game)
        self.myVars = MyVars(self, game)
        self.myDicts = MyDicts()
        self.myLists = MyLists()
        self.myMatrix = Matrix(self.game.game_map.height, self.game.game_map.width)


    @abc.abstractmethod                                                                                                 ## MUST BE DEFINED BY CHILD CLASS
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

        if getattr(self, 'init_data', None):                                                                            ## IF THIS IS NONE, ITS AT GETINITDATA
            self.myVars.ratio_left_halite = self.myVars.total_halite / self.starting_halite


    def populate_myShipyard_docks(self):
        """
        POPULATE MY SHIPYARD POSITION AND ALL DOCKS POSITION
        """
        ## SHIPYARD
        myShipyard_position = self.game.me.shipyard.position
        self.myMatrix.locations.myShipyard[myShipyard_position.y][myShipyard_position.x] = Matrix_val.ONE

        ## DOCKS
        self.mySets.dock_coords.add((myShipyard_position.y, myShipyard_position.x))
        self.myMatrix.locations.myDocks[myShipyard_position.y][myShipyard_position.x] = Matrix_val.ONE

        for dropoff in self.game.me.get_dropoffs():
            self.mySets.dock_coords.add((dropoff.position.y, dropoff.position.x))
            self.myMatrix.locations.myDocks[dropoff.position.y][dropoff.position.x] = Matrix_val.ONE

        ## POPULATE CLOSSEST DOCKS
        self.populate_distance_docks()


    def populate_distance_docks(self):
        """
        POPULATE DISTANCE MATRIX TO ALL DOCKS
        RETURNS DISTANCES OF EACH CELLS TO DOCKS (BEST SCENARIO, BASED ON CLOSEST DOCK)
        """
        if getattr(self, 'init_data', None):                                                                            ## IF THIS IS NONE, ITS AT GETINITDATA
            distance_matrixes = []

            ## GATHER EACH OF THE DOCK DISTANCES MATRIX
            for dock_coord in self.mySets.dock_coords:
                distance_matrixes.append(copy.deepcopy(self.init_data.myMatrix.distances.cell[dock_coord]))

            self.myMatrix.distances.closest_dock = myMinDockDistances(*distance_matrixes)                               ## COMBINE AND GET LEAST DISTANCE


    def forecast_distance_docks(self):
        """
        UPDATE DISTANCE DOCKS (USED TO FORECAST THAT A DOCK IS GETTING BUILT THERE)
        """
        ## FORECASTS
        distance_matrixes = [self.myMatrix.distances.closest_dock]

        for dock_coord in self.myDicts.ships_building_dock.keys():
            if dock_coord:
                distance_matrixes.append(copy.deepcopy(self.init_data.myMatrix.distances.cell[dock_coord]))

        self.myMatrix.distances.closest_dock = myMinDockDistances(*distance_matrixes)

        ## PRETENDS DOCKS ARE ALL THERE
        # distance_matrixes = [self.myMatrix.distances.closest_dock]
        #
        # indexes = np.argwhere(self.init_data.myMatrix.locations.dock_placement == MyConstants.DOCK_MANHATTAN)
        # for y, x in indexes:
        #     dock_coord = (y, x)
        #     distance_matrixes.append(copy.deepcopy(self.init_data.myMatrix.distances.cell[dock_coord]))
        #
        # self.myMatrix.distances.closest_dock = myMinDockDistances(*distance_matrixes)


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
        POPULATE SHIP CARGO
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
            self.myMatrix.locations.shipCargo[ship.position.y][ship.position.x] = ship.halite_amount
            populate_manhattan(self.myMatrix.locations.potential_ally_collisions,
                               Matrix_val.POTENTIAL_COLLISION,
                               ship.position,
                               MyConstants.DIRECT_NEIGHBOR_DISTANCE,
                               cummulative=True)

            ## POPULATE STUCK SHIPS
            if self.myMatrix.halite.cost[ship.position.y][ship.position.x] > ship.halite_amount:
                self.myMatrix.locations.stuck[ship.position.y][ship.position.x] = Matrix_val.ONE


    def populate_enemyShips_influenced(self):
        """
        POPULATE MATRIX LOCATION OF ENEMY SHIPS AND ITS IDs
        GATHER HALITE INFO AS WELL
        POPULATE MATRIX WITH ENEMY CARGO
        POPULATE MATRIX WITH ENEMY INFLUENCE
        POPULATE MATRIX WITH POTENTIAL ENEMY COLLISIONS
        POPULATE MATRIX WITH ENGAGE ENEMY (CLOSE TO ENEMY)
        """
        for id, player in self.game.players.items():
            if id != self.game.me.id:
                self.myDicts.players_halite[id] = HaliteInfo()
                self.myDicts.players_halite[id].halite_amount = player.halite_amount

                for ship in player.get_ships():
                    self.myDicts.players_halite[id].halite_carried += ship.halite_amount
                    self.myMatrix.locations.enemyShips[ship.position.y][ship.position.x] = Matrix_val.ONE
                    self.myMatrix.locations.enemyShipsID[ship.position.y][ship.position.x] = ship.id
                    self.myMatrix.locations.enemyShipsOwner[ship.position.y][ship.position.x] = id
                    self.myMatrix.locations.shipCargo[ship.position.y][ship.position.x] = ship.halite_amount
                    self.myMatrix.locations.enemyCargo[ship.position.y][ship.position.x] = ship.halite_amount

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
                                       MyConstants.DIRECT_NEIGHBOR_DISTANCE,
                                       cummulative=True)

                    populate_manhattan(self.myMatrix.locations.engage_influence,
                                       Matrix_val.ONE,
                                       ship.position,
                                       MyConstants.ENGAGE_INFLUENCE_DISTANCE,
                                       cummulative=False)

                    for dist in range(1, MyConstants.ENGAGE_ENEMY_DISTANCE + 1):
                        populate_manhattan(self.myMatrix.locations.engage_enemy[dist],
                                           Matrix_val.ONE,
                                           ship.position,
                                           dist,
                                           cummulative=False)


    def populate_cost(self):
        """
        POPULATE MATRIX COST TO LEAVE EACH CELL
        """
        cost = self.myMatrix.halite.amount * 0.1
        #self.myMatrix.halite.cost = np.round(cost)                                                                     ## FYI, numpy.round IS UNBIASED FOR XX.5 (BY DESIGN)
        self.myMatrix.halite.cost = myRound(cost)                                                                       ## THUS MAKING MY OWN SO IT WILL ROUND UP FOR XX.5


    def populate_harvest(self):
        """
        POPULATE MATRIX HARVEST, IF WE STAY STILL IN EACH CELL FOR A SINGLE TURN
        DOES NOT CONSIDER INFLUENCE
        """
        harvest = self.myMatrix.halite.amount * 0.25
        #self.myMatrix.halite.harvest = np.round(harvest)                                                               ## FYI, numpy.round IS UNBIASED FOR XX.5 (BY DESIGN)
        self.myMatrix.halite.harvest = myRound(harvest)

        self.myMatrix.halite.bonus = myBonusArea(self.myMatrix.halite.harvest, self.myMatrix.locations.influenced)

        self.myMatrix.halite.harvest_with_bonus = self.myMatrix.halite.harvest + self.myMatrix.halite.bonus


    def populate_cell_distances(self):
        """
        POPULATE DISTANCES OF EACH CELLS TO ONE ANOTHER

        self.myMatrix.distances.cell[curr_section][y][x] = distance
        """
        height = self.game.game_map.height
        width = self.game.game_map.width

        curr_cell = (0, 0)
        base_matrix = get_distance_matrix(curr_cell, self)

        for r in range(height + 1):
            for c in range(width + 1):
                curr_cell = (r, c)
                ## THIS METHOD WILL TIME OUT (ALSO UNNECESSARY CALCULATIONS
                ## SINCE DISTANCE MATRIX IS PRETTY SIMILAR
                # self.myMatrix.distances.cell[curr_cell] = get_distance_matrix(curr_cell, height, width)
                # print_matrix("Distances (1) on {}".format(curr_cell), self.myMatrix.distances.cell[curr_cell])

                self.myMatrix.distances.cell[curr_cell] = shift_matrix(r, c, base_matrix)                               ## SHIFTING/ROLLING SO NO RECALCULATION NEEDED
                # print_matrix("Distances (2) on {}".format(curr_cell), self.myMatrix.distances.cell[curr_cell])


    def populate_cell_averages(self):
        """
        POPULATE AVERAGES OF EACH CELL BASED ON DISTANCE
        USED FOR DETERMINING DOCK PLACEMENT
        """
        ## THE AVERAGE MANHATTAN OF EACH MAP CELL, BASED ON AVERAGE MANHATTAN DISTANCE
        for r in range(self.game.game_map.height):
            for c in range(self.game.game_map.width):
                loc = Position(c, r) ## Position(x, y)
                self.myMatrix.cell_average.manhattan[r][c] = get_average_manhattan(self.myMatrix.halite.amount,
                                                                                 loc,
                                                                                 MyConstants.AVERAGE_MANHATTAN_DISTANCE)


    def populate_top_halite(self):
        """
        POPULATE TOP HALITE CELLS
        """
        ## NO LONGER USED
        ## NOW JUST USING RATIO (HARVEST PER TURN)
        if self.game.turn_number > constants.MAX_TURNS * MyConstants.EXPLORE_ENABLE_WITH_BONUS_TURNS_ABOVE:
            ## BASED ON HARVEST (INCLUDING INFLUENCE)
            top_num_cells = int(MyConstants.TOP_N_HALITE * (self.game.game_map.height * self.game.game_map.width))
            top, ind = get_n_largest_values(self.myMatrix.halite.harvest_with_bonus, top_num_cells)
            self.myMatrix.halite.top_amount[ind] = top
        else:
            ## ORIGINAL
            top_num_cells = int(MyConstants.TOP_N_HALITE * (self.game.game_map.height * self.game.game_map.width))
            top, ind = get_n_largest_values(self.myMatrix.halite.amount, top_num_cells)
            self.myMatrix.halite.top_amount[ind] = top


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


    def get_mean_median_halite(self):
        self.myVars.average_halite = int(np.average(self.myMatrix.halite.amount))
        self.myVars.median_halite = int(np.median(self.myMatrix.halite.amount))

        ## HARVEST PERCENTILE USED FOR HARVEST LATER (WHETHER ITS A GOOD HARVEST OR NOT)
        if self.game.turn_number > constants.MAX_TURNS * MyConstants.HARVEST_ENABLE_WITH_BONUS_TURNS_ABOVE:
            self.myVars.harvest_percentile = int(np.percentile(self.myMatrix.halite.harvest_with_bonus, MyConstants.HARVEST_ABOVE_PERCENTILE))
        else:
            self.myVars.harvest_percentile = int(np.percentile(self.myMatrix.halite.harvest, MyConstants.HARVEST_ABOVE_PERCENTILE))


        logging.debug("Average Halite: {} Median Halite {} Harvest Percentile {}".
                        format(self.myVars.average_halite,
                        self.myVars.median_halite,
                        self.myVars.harvest_percentile))


    def update_dock_placement(self):
        """
        UPDATE DOCK PLACEMENT TO EXCLUDE ENEMY DOCKS/SHIPYARDS
        REMEMBER, DOCK PLACEMENT IS ONLY CALCULATED IN INIT_DATA
        """
        r, c = np.where(self.myMatrix.locations.enemyDocks == Matrix_val.ONE)
        self.init_data.myMatrix.locations.dock_placement[r, c] = Matrix_val.ZERO

        self.populate_dock_averages()

        ## ALSO UPDATE DOCK PLACEMENT WHERE AVERAGE IS TOO LOW NOW
        indexes = np.argwhere(self.init_data.myMatrix.locations.dock_placement == MyConstants.DOCK_MANHATTAN)
        for y, x in indexes:
            original_average = self.init_data.myMatrix.dock_averages[y][x]
            current_average = self.myMatrix.dock_averages[y][x]

            if current_average <= original_average * MyConstants.DOCK_HALITE_AVERAGE:                                   ## AVERAGE TOO LOW
                self.init_data.myMatrix.locations.dock_placement[r, c] = Matrix_val.ZERO



    def populate_dock_averages(self):
        """
        POPULATE AVERAGE OF EACH DOCKS (TO BE BUILT)
        """
        if getattr(self, 'init_data', None):
            indexes = np.argwhere(self.init_data.myMatrix.locations.dock_placement == MyConstants.DOCK_MANHATTAN)

        else:                                                                                                           ## init_data IS NONE, ITS AT GETINITDATA
            indexes = np.argwhere(self.myMatrix.locations.dock_placement == MyConstants.DOCK_MANHATTAN)

        for y, x in indexes:
            self.myMatrix.dock_averages[y][x] = get_average_manhattan(self.myMatrix.halite.amount,
                                                                     Position(x, y),
                                                                     MyConstants.AVERAGE_MANHATTAN_DISTANCE)


    ## NO LONGER USED
    # def populate_sectioned_halite(self):
    #     """
    #     POPULATE SECTIONED HALITE (MyConstants.SECTION_SIZE x MyConstants.SECTION_SIZE)
    #
    #     RECORD AVERAGE OF EACH SECTION
    #
    #     OBSOLETE???? NO LONGER USED
    #     """
    #     for y, row in enumerate(self.myMatrix.sectioned.halite):
    #         for x, col in enumerate(row):
    #             section = self.myMatrix.halite.amount[
    #                       y * MyConstants.SECTION_SIZE:y * MyConstants.SECTION_SIZE + MyConstants.SECTION_SIZE,
    #                       x * MyConstants.SECTION_SIZE:x * MyConstants.SECTION_SIZE + MyConstants.SECTION_SIZE]
    #             sum = section.sum()
    #             average_halite = sum // (MyConstants.SECTION_SIZE * 2)
    #
    #             self.myMatrix.sectioned.halite[y][x] = average_halite
    #
    #     print_matrix("sectioned halite", self.myMatrix.sectioned.halite)
    #
    #
    # def populate_sectioned_distances(self):
    #     """
    #     POPULATE DISTANCES OF EACH SECTIONS TO ONE ANOTHER
    #
    #     self.myMatrix.sectioned.distances[curr_section][y][x] = distance
    #
    #     OBSOLETE????? NO LONGER USED
    #     """
    #     height = (self.game.game_map.height // MyConstants.SECTION_SIZE) + 1  ## + 1 TO COUNT LAST ITEM FOR RANGE
    #     width = (self.game.game_map.width // MyConstants.SECTION_SIZE) + 1
    #
    #     for r in range(height):
    #         for c in range(width):
    #             curr_section = (r, c)
    #             self.myMatrix.sectioned.distances[curr_section] = get_distance_matrix(curr_section, height, width)
    #
    #             #print_matrix("Distances on {}".format(curr_section), self.myMatrix.sectioned.distances[curr_section])


    # def populate_depletion(self):
    #     """
    #     POPULATE
    #     """
    #     ## POPULATE NUMBER OF TURNS TO HAVE HALITE <= DONT_HARVEST_BELOW
    #     self.myMatrix.depletion.harvest_turns =  myHarvestCounter(self.myMatrix.halite.amount)
    #
    #     ## POPULATE SHIPYARD DISTANCES
    #     start_tuple = (self.game.me.shipyard.position.y, self.game.me.shipyard.position.x)
    #     self.myMatrix.depletion.shipyard_distances = get_distance_matrix(start_tuple, self.game.game_map.height, self.game.game_map.width)
    #
    #     ## POPULATE TOTAL NUMBER OF TURNS TO DEPLETE HALITE, INCLUDING TRAVELING THERE BACK AND FORTH
    #     self.myMatrix.depletion.total_turns = myTurnCounter(self.myMatrix.depletion.harvest_turns, self.myMatrix.depletion.shipyard_distances)
    #
    #     ## POPULATE IF A GOOD HARVEST AREA
    #     max_num = np.max(self.myMatrix.depletion.total_turns)
    #     max_matrix = self.myMatrix.depletion.max_matrix * max_num
    #     self.myMatrix.depletion.harvest_area = myHarvestArea(max_matrix, self.myMatrix.depletion.total_turns)



## NO LONGER USED
# class Sectioned():
#     """
#     MAP DIVIDED INTO SECTIONS
#
#     OBSOLETE????
#     """
#     def __init__(self, map_height, map_width):
#         self.halite = np.zeros((map_height // MyConstants.SECTION_SIZE , map_width // MyConstants.SECTION_SIZE), dtype=np.int16)
#         self.distances = {}  ## ONLY FILLED IN INIT


## NO LONGER USED
# class Depletion():
#     """
#     USED TO ANALYZE HOW MANY TURNS TO DEPLETE THE HALITE IN THE ENTIRE MAP
#
#     OBSOLETE????
#     """
#     def __init__(self, map_height, map_width):
#         self.harvest_turns = np.zeros((map_height, map_width), dtype=np.int16)
#         self.shipyard_distances = np.zeros((map_height, map_width), dtype=np.int16)
#         self.total_turns = np.zeros((map_height, map_width), dtype=np.int16)
#         self.max_matrix = np.zeros((map_height, map_width), dtype=np.int16)
#         self.max_matrix.fill(1)
#         self.harvest_area = np.zeros((map_height, map_width), dtype=np.int16)
