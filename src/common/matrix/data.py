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


    @abc.abstractmethod
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

            self.myVars.explore_disable_bonus = self.myVars.ratio_left_halite > MyConstants.explore.enable_bonus_halite_left \
                                                and self.game.turn_number <= constants.MAX_TURNS * MyConstants.explore.enable_bonus_turns_above


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
        if getattr(self, 'init_data', None):
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
        # indexes = np.argwhere(self.init_data.myMatrix.locations.dock_placement == MyConstants.build.dock_manhattan)
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
                                       MyConstants.influence.engage_distance,
                                       Option.REPLACE)

                    for dist in range(1, MyConstants.attack.engage_enemy_distance + 1):
                        populate_manhattan(self.myMatrix.locations.engage_enemy[dist],
                                           Matrix_val.ONE,
                                           ship.position,
                                           dist,
                                           Option.REPLACE)

        ## CHECK IF KILLING SPREE SHOULD BE ENABLED
        if self.myDicts.players_info[enemy_id].num_ships * MyConstants.snipe.killing_spree_halite_ratio <= self.myDicts.players_info[self.game.me.id].num_ships \
            and self.myVars.ratio_left_halite <= MyConstants.snipe.killing_spree_halite_left \
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

        THE AVERAGE MANHATTAN OF EACH MAP CELL, BASED ON AVERAGE MANHATTAN DISTANCE
        """
        ## OLD WAY (10x SLOWER THAN BELOW)
        # for r in range(self.game.game_map.height):
        #     for c in range(self.game.game_map.width):
        #         loc = Position(c, r) ## Position(x, y)
        #         self.myMatrix.cell_average.halite[r][c] = get_average_manhattan(self.myMatrix.halite.amount,
        #                                                                            loc,
        #                                                                            distance)

        ## MUCH FASTER WAY OF GENERATING THE ENTIRE MAP AVERAGES
        self.myMatrix.cell_average.halite = get_average_manhattan_matrix(self.myMatrix.halite.amount, distance)

        self.myMatrix.cell_average.enemyCargo = get_average_manhattan_matrix(self.myMatrix.halite.enemyCargo, distance)


    def populate_top_halite(self):
        """
        POPULATE TOP HALITE CELLS
        """
        ## NO LONGER USED
        ## NOW JUST USING RATIO (HARVEST PER TURN)
        if self.game.turn_number > constants.MAX_TURNS * MyConstants.explore.enable_bonus_turns_above:
            ## BASED ON HARVEST (INCLUDING INFLUENCE)
            top_num_cells = int(MyConstants.build.top_n_halite * (self.game.game_map.height * self.game.game_map.width))
            top, ind = get_n_largest_values(self.myMatrix.halite.harvest_with_bonus, top_num_cells)
            self.myMatrix.halite.top_amount[ind] = top
        else:
            ## ORIGINAL
            top_num_cells = int(MyConstants.build.top_n_halite * (self.game.game_map.height * self.game.game_map.width))
            top, ind = get_n_largest_values(self.myMatrix.halite.amount, top_num_cells)
            self.myMatrix.halite.top_amount[ind] = top


    def get_mean_median_halite(self):
        self.myVars.average_halite = int(np.average(self.myMatrix.halite.amount))
        self.myVars.median_halite = int(np.median(self.myMatrix.halite.amount))

        ## HARVEST PERCENTILE USED FOR HARVEST LATER (WHETHER ITS A GOOD HARVEST OR NOT)
        if self.game.turn_number > constants.MAX_TURNS * MyConstants.harvest.enable_bonus_turns_above:
            self.myVars.harvest_percentile = int(np.percentile(self.myMatrix.halite.harvest_with_bonus, MyConstants.harvest.harvest_above_percentile))
            self.myVars.deposit_harvest_percentile = int(np.percentile(self.myMatrix.halite.harvest_with_bonus, MyConstants.deposit.harvest_above_percentile))
        else:
            self.myVars.harvest_percentile = int(np.percentile(self.myMatrix.halite.harvest, MyConstants.harvest.harvest_above_percentile))
            self.myVars.deposit_harvest_percentile = int(np.percentile(self.myMatrix.halite.harvest, MyConstants.deposit.harvest_above_percentile))


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

            if current_average <= original_average * MyConstants.build.min_dock_halite_average:                                   ## AVERAGE TOO LOW
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
        #     if current_average <= original_average * MyConstants.build.min_dock_halite_average:  ## AVERAGE TOO LOW
        #         self.init_data.myMatrix.docks.order[y, x] = Matrix_val.NINETY
        #
        # ## GET LOWEST ORDER DOCK
        # matrix = self.init_data.myMatrix.docks.order
        # y, x = np.where(matrix == matrix.min())
        # position = Position(x, y)
        #
        # ## POPULATE DOCK PLACEMENT
        # for i in range(0, MyConstants.build.dock_manhattan):
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
                                                                     MyConstants.build.average_manhattan_distance)


    def populate_dock_manhattan(self):
        if getattr(self, 'init_data', None):
            indexes = np.argwhere(self.init_data.myMatrix.docks.placement == Matrix_val.ONE)
        else:
            indexes = np.argwhere(self.myMatrix.docks.placement == Matrix_val.ONE)

        for y, x in indexes:
            for i in range(0, MyConstants.build.dock_manhattan):
                position = Position(x,y)
                populate_manhattan(self.myMatrix.docks.manhattan, Matrix_val.ONE, position, i, Option.CUMMULATIVE)

