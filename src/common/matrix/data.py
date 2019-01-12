import numpy as np
import logging
from hlt.positionals import Position
from src.common.values import MyConstants, Matrix_val, Inequality
from hlt import constants
from src.common.matrix.functions import populate_manhattan, get_n_largest_values, get_distance_matrix, \
    get_average_manhattan, shift_matrix, get_average_manhattan_matrix
from src.common.matrix.vectorized import myRound, myBonusArea, myMinValueMatrix, mySunkenShips
from src.common.orderedSet import OrderedSet
from src.common.print import print_matrix
from src.common.matrix.classes import Option, PlayerInfo, MySets, MyVars, MyDicts, MyLists, Matrix
import copy
import abc

class Data(abc.ABC):
    def __init__(self, game):
        self.game = game
        self.mySets = MySets(game)
        self.myVars = MyVars(self, game)
        self.myDicts = MyDicts()
        self.myLists = MyLists(self)
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

        halites = [[cell.halite_amount for cell in row] for row in self.game.game_map._cells]
        self.myMatrix.halite.updated_amount = np.array(halites, dtype=np.int16)

        self.myVars.total_halite = self.myMatrix.halite.amount.sum()

        if getattr(self, 'init_data', None):                                                                            ## IF THIS IS NONE, ITS AT GETINITDATA
            self.myVars.ratio_left_halite = self.myVars.total_halite / self.starting_halite

            self.myVars.explore_disable_bonus = self.myVars.ratio_left_halite > MyConstants.EXPLORE_ENABLE_BONUS_HALITE_LEFT \
                                                or self.data.game.turn_number <= constants.MAX_TURNS * MyConstants.EXPLORE_ENABLE_BONUS_TURNS_ABOVE


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

            self.myMatrix.distances.closest_dock = myMinValueMatrix(*distance_matrixes)                                 ## COMBINE AND GET LEAST DISTANCE


    def forecast_distance_docks(self):
        """
        UPDATE DISTANCE DOCKS (USED TO FORECAST THAT A DOCK IS GETTING BUILT THERE)
        """
        ## FORECASTS
        distance_matrixes = [self.myMatrix.distances.closest_dock]

        for dock_coord in self.myDicts.ships_building_dock.keys():
            if dock_coord:
                distance_matrixes.append(copy.deepcopy(self.init_data.myMatrix.distances.cell[dock_coord]))

        self.myMatrix.distances.closest_dock = myMinValueMatrix(*distance_matrixes)

        ## PRETENDS DOCKS ARE ALL THERE
        # distance_matrixes = [self.myMatrix.distances.closest_dock]
        #
        # indexes = np.argwhere(self.init_data.myMatrix.locations.dock_placement == MyConstants.DOCK_MANHATTAN)
        # for y, x in indexes:
        #     dock_coord = (y, x)
        #     distance_matrixes.append(copy.deepcopy(self.init_data.myMatrix.distances.cell[dock_coord]))
        #
        # self.myMatrix.distances.closest_dock = myMinValueMatrix(*distance_matrixes)


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
        self.myDicts.players_info[self.game.my_id] = PlayerInfo()
        self.myDicts.players_info[self.game.my_id].halite_amount = self.game.me.halite_amount
        self.myDicts.players_info[self.game.my_id].num_ships = len(self.game.me.get_ships())

        for ship in self.game.me.get_ships():
            self.myDicts.players_info[self.game.my_id].halite_carried += ship.halite_amount
            self.myMatrix.locations.myShips[ship.position.y][ship.position.x] = Matrix_val.ONE
            self.myMatrix.locations.myShipsID[ship.position.y][ship.position.x] = ship.id
            self.myMatrix.locations.occupied[ship.position.y][ship.position.x] = Matrix_val.OCCUPIED
            self.myMatrix.locations.shipsCargo[ship.position.y][ship.position.x] = ship.halite_amount
            populate_manhattan(self.myMatrix.locations.potential_ally_collisions,
                               Matrix_val.POTENTIAL_COLLISION,
                               ship.position,
                               MyConstants.DIRECT_NEIGHBOR_DISTANCE,
                               Option.CUMMULATIVE)

            ## POPULATE STUCK SHIPS
            if self.myMatrix.halite.cost[ship.position.y][ship.position.x] > ship.halite_amount:
                self.myMatrix.locations.stuck[ship.position.y][ship.position.x] = Matrix_val.ONE


        if self.prev_data:
            self.myMatrix.sunken_ships = mySunkenShips(self.prev_data.matrix.locations.updated_myShipsID,
                                                       self.myMatrix.locations.myShipsID)


    def populate_enemyShips_influenced(self):
        """
        POPULATE MATRIX LOCATION OF ENEMY SHIPS AND ITS IDs
        GATHER HALITE INFO AS WELL
        POPULATE MATRIX WITH ENEMY CARGO
        POPULATE MATRIX WITH ENEMY INFLUENCE
        POPULATE MATRIX WITH POTENTIAL ENEMY COLLISIONS
        POPULATE MATRIX WITH ENGAGE ENEMY (CLOSE TO ENEMY)
        """
        enemy_id = None

        for id, player in self.game.players.items():
            if id != self.game.me.id:
                enemy_id = id
                self.myDicts.players_info[id] = PlayerInfo()
                self.myDicts.players_info[id].halite_amount = player.halite_amount
                self.myDicts.players_info[id].num_ships = len(player.get_ships())

                for ship in player.get_ships():
                    self.myDicts.players_info[id].halite_carried += ship.halite_amount
                    self.myMatrix.locations.enemyShips[ship.position.y][ship.position.x] = Matrix_val.ONE
                    self.myMatrix.locations.enemyShipsID[ship.position.y][ship.position.x] = ship.id
                    self.myMatrix.locations.enemyShipsOwner[ship.position.y][ship.position.x] = id
                    self.myMatrix.locations.shipsCargo[ship.position.y][ship.position.x] = ship.halite_amount
                    self.myMatrix.halite.enemyCargo[ship.position.y][ship.position.x] = ship.halite_amount
                    self.myMatrix.halite.updated_enemyCargo[ship.position.y][ship.position.x] = ship.halite_amount

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
                                       Option.CUMMULATIVE)

                    populate_manhattan(self.myMatrix.locations.potential_enemy_collisions,
                                       Matrix_val.POTENTIAL_COLLISION,
                                       ship.position,
                                       MyConstants.DIRECT_NEIGHBOR_DISTANCE,
                                       Option.CUMMULATIVE)

                    populate_manhattan(self.myMatrix.locations.potential_enemy_cargo,
                                       ship.halite_amount,
                                       ship.position,
                                       MyConstants.DIRECT_NEIGHBOR_DISTANCE,
                                       Option.MINIMUM)

                    populate_manhattan(self.myMatrix.locations.engage_influence,
                                       Matrix_val.ONE,
                                       ship.position,
                                       MyConstants.ENGAGE_INFLUENCE_DISTANCE,
                                       Option.REPLACE)

                    for dist in range(1, MyConstants.ENGAGE_ENEMY_DISTANCE + 1):
                        populate_manhattan(self.myMatrix.locations.engage_enemy[dist],
                                           Matrix_val.ONE,
                                           ship.position,
                                           dist,
                                           Option.REPLACE)

        ## CHECK IF KILLING SPREE SHOULD BE ENABLED
        if self.myDicts.players_info[enemy_id].num_ships * MyConstants.KILLING_SPREE_RATIO <= self.myDicts.players_info[self.game.me.id].num_ships \
            and self.myVars.ratio_left_halite <= MyConstants.KILLING_SPREE_HALITE \
            and len(self.game.players) == 2:
            self.myVars.on_killing_spree = True

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
        self.myMatrix.halite.updated_harvest = myRound(harvest)

        self.myMatrix.halite.bonus = myBonusArea(self.myMatrix.halite.harvest, self.myMatrix.locations.influenced)

        self.myMatrix.halite.harvest_with_bonus = self.myMatrix.halite.harvest + self.myMatrix.halite.bonus
        self.myMatrix.halite.updated_harvest_with_bonus = self.myMatrix.halite.harvest + self.myMatrix.halite.bonus


        ## POPULATE ENEMY CARGO, HARVEST, WITH BONUS
        enemy_harvest = self.myMatrix.halite.enemyCargo * 0.25
        #self.myMatrix.halite.enemyCargo_harvest = myRound(enemy_harvest) + self.myMatrix.halite.harvest
        self.myMatrix.halite.enemyCargo_harvest = myRound(enemy_harvest)
        #self.myMatrix.halite.updated_enemyCargo_harvest = myRound(enemy_harvest) + self.myMatrix.halite.harvest
        self.myMatrix.halite.updated_enemyCargo_harvest = myRound(enemy_harvest)

        bonus = myBonusArea(self.myMatrix.halite.enemyCargo_harvest, self.myMatrix.locations.influenced)
        self.myMatrix.halite.enemyCargo_harvest_with_bonus = self.myMatrix.halite.enemyCargo_harvest + bonus
        self.myMatrix.halite.updated_enemyCargo_harvest_with_bonus = self.myMatrix.halite.enemyCargo_harvest + bonus


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


    def populate_cell_averages(self, distance):
        """
        POPULATE AVERAGES OF EACH CELL BASED ON DISTANCE
        USED FOR DETERMINING DOCK PLACEMENT
        """
        ## THE AVERAGE MANHATTAN OF EACH MAP CELL, BASED ON AVERAGE MANHATTAN DISTANCE
        for r in range(self.game.game_map.height):
            for c in range(self.game.game_map.width):
                loc = Position(c, r) ## Position(x, y)
                self.myMatrix.cell_average.halite[r][c] = get_average_manhattan(self.myMatrix.halite.amount,
                                                                                   loc,
                                                                                   distance)

    def populate_cell_averages2(self, distance):
        """
        MUCH FASTER WAY OF GENERATING THE ENTIRE MAP AVERAGES
        BUT IS ONLY LIMITED TO 32 ARRAYS (THUS MAX DISTANCE OF 3)
        6 DISTANCES REQUIRES 85 MATRICES, WILL ERROR OUT
        """
        self.myMatrix.cell_average.halite = get_average_manhattan_matrix(self.myMatrix.halite.amount, distance)

        self.myMatrix.cell_average.enemyCargo = get_average_manhattan_matrix(self.myMatrix.halite.enemyCargo, distance)



    def populate_top_halite(self):
        """
        POPULATE TOP HALITE CELLS
        """
        ## NO LONGER USED
        ## NOW JUST USING RATIO (HARVEST PER TURN)
        if self.game.turn_number > constants.MAX_TURNS * MyConstants.EXPLORE_ENABLE_BONUS_TURNS_ABOVE:
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
        if self.game.turn_number > constants.MAX_TURNS * MyConstants.HARVEST_ENABLE_BONUS_TURNS_ABOVE:
            self.myVars.harvest_percentile = int(np.percentile(self.myMatrix.halite.harvest_with_bonus, MyConstants.HARVEST_ABOVE_PERCENTILE))
            self.myVars.deposit_harvest_percentile = int(np.percentile(self.myMatrix.halite.harvest_with_bonus, MyConstants.DEPOSIT_HARVEST_ABOVE_PERCENTILE))
        else:
            self.myVars.harvest_percentile = int(np.percentile(self.myMatrix.halite.harvest, MyConstants.HARVEST_ABOVE_PERCENTILE))
            self.myVars.deposit_harvest_percentile = int(np.percentile(self.myMatrix.halite.harvest, MyConstants.DEPOSIT_HARVEST_ABOVE_PERCENTILE))


        logging.debug("Average Halite: {} Median Halite {} Harvest Percentile {}".
                        format(self.myVars.average_halite,
                        self.myVars.median_halite,
                        self.myVars.harvest_percentile))


    def update_dock_placement(self):
        """
        UPDATE DOCK PLACEMENT TO EXCLUDE ENEMY DOCKS/SHIPYARDS
        REMEMBER, DOCK PLACEMENT IS ONLY CALCULATED IN INIT_DATA
        """
        ## OLD WAY
        r, c = np.where(self.myMatrix.locations.enemyDocks == Matrix_val.ONE)
        self.init_data.myMatrix.docks.placement[r, c] = Matrix_val.ZERO

        self.populate_dock_averages()

        ## ALSO UPDATE DOCK PLACEMENT WHERE AVERAGE IS TOO LOW NOW
        indexes = np.argwhere(self.init_data.myMatrix.docks.placement == Matrix_val.ONE)
        for y, x in indexes:
            original_average = self.init_data.myMatrix.docks.averages[y][x]
            current_average = self.myMatrix.docks.averages[y][x]

            #logging.debug("Dock average: original_average {} current_average {}".format(original_average, current_average))

            if current_average <= original_average * MyConstants.MIN_DOCK_HALITE_AVERAGE:                                   ## AVERAGE TOO LOW
                self.init_data.myMatrix.docks.placement[y][x] = Matrix_val.ZERO

        self.populate_dock_manhattan()


        ## ORDERED DOCK
        # r, c = np.where(self.myMatrix.locations.enemyDocks == Matrix_val.ONE)
        # self.init_data.myMatrix.docks.order[r, c] = Matrix_val.NINETY
        #
        # self.populate_dock_averages()
        #
        # ## ALSO UPDATE DOCK PLACEMENT WHERE AVERAGE IS TOO LOW NOW
        # indexes = np.argwhere(self.init_data.myMatrix.docks.order != Matrix_val.NINETY)
        # for y, x in indexes:
        #     original_average = self.init_data.myMatrix.docks.averages[y][x]
        #     current_average = self.myMatrix.docks.averages[y][x]
        #
        #     if current_average <= original_average * MyConstants.MIN_DOCK_HALITE_AVERAGE:  ## AVERAGE TOO LOW
        #         self.init_data.myMatrix.docks.order[y, x] = Matrix_val.NINETY
        #
        # ## GET LOWEST ORDER DOCK
        # matrix = self.init_data.myMatrix.docks.order
        # y, x = np.where(matrix == matrix.min())
        # position = Position(x, y)
        #
        # ## POPULATE DOCK PLACEMENT
        # for i in range(0, MyConstants.DOCK_MANHATTAN):
        #     populate_manhattan(self.myMatrix.docks.manhattan, Matrix_val.ONE, position, i, Option.CUMMULATIVE)


    def populate_dock_averages(self):
        """
        POPULATE AVERAGE OF EACH DOCKS (TO BE BUILT)
        """
        ## OLD WAY
        if getattr(self, 'init_data', None):
            indexes = np.argwhere(self.init_data.myMatrix.docks.placement == Matrix_val.ONE)
        else:                                                                                                           ## init_data IS NONE, ITS AT GETINITDATA
            indexes = np.argwhere(self.myMatrix.docks.placement == Matrix_val.ONE)

        ## ORDERED DOCK
        # if getattr(self, 'init_data', None):
        #     indexes = np.argwhere(self.init_data.myMatrix.docks.order != Matrix_val.NINETY)
        # else:
        #     indexes = np.argwhere(self.myMatrix.docks.order != Matrix_val.NINETY)



        for y, x in indexes:
            self.myMatrix.docks.averages[y][x] = get_average_manhattan(self.myMatrix.halite.amount,
                                                                     Position(x, y),
                                                                     MyConstants.AVERAGE_MANHATTAN_DISTANCE)

        #print_matrix("dock averages ", self.myMatrix.docks.averages)

    def populate_dock_manhattan(self):
        if getattr(self, 'init_data', None):
            indexes = np.argwhere(self.init_data.myMatrix.docks.placement == Matrix_val.ONE)
        else:
            indexes = np.argwhere(self.myMatrix.docks.placement == Matrix_val.ONE)

        for y, x in indexes:
            for i in range(0, MyConstants.DOCK_MANHATTAN):
                position = Position(x,y)
                populate_manhattan(self.myMatrix.docks.manhattan, Matrix_val.ONE, position, i, Option.CUMMULATIVE)

        #print_matrix("dock manhattan", self.myMatrix.docks.manhattan)

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
