from src.common.matrix.data import Data
from src.common.print import print_matrix
from src.common.matrix.functions import Section, populate_manhattan, get_index_highest_val, get_coord_closest, \
    get_n_largest_values, get_cell_averages, get_n_max_values, calculate_distance, get_average_manhattan
from src.common.values import Matrix_val, MyConstants, Inequality
from hlt.positionals import Position
from src.common.matrix.classes import Option
from src.common.print import print_heading
import numpy as np
import logging
import copy


"""
TO DO !!!

"""


class GetInitData(Data):
    def __init__(self, game):
        super().__init__(game)

        print_heading("Gathering Initialized data......")

        self.unavailable_area = np.zeros((game.game_map.height, game.game_map.width), dtype=np.float16)
        self.update_matrix()

    def update_matrix(self):
        """
        POPULATE ALL MATRICES
        """
        self.populate_halite()
        self.populate_myShipyard_docks()
        self.populate_enemyShipyard_docks()
        self.populate_cost()
        self.populate_harvest()

        self.populate_cell_distances()
        # self.populate_top_halite()
        self.get_mean_median_halite()

        self.populate_cell_averages(MyConstants.build.average_manhattan_distance)

        self.populate_dock_placement()

        ## NO LONGER USED
        # self.populate_sectioned_halite()
        # self.populate_sectioned_distances()
        # self.populate_depletion()


    def populate_dock_placement(self):
        self.get_top_N_averages()
        self.final_dock_placement()
        self.populate_dock_averages()


    def get_top_N_averages(self):
        """
        POPULATE WHERE TOP N PLACES ARE, BASED ON HIGHEST AVERAGE CELL MANHATTAN
        THEN GET HIGHEST HALITE AMOUNT WITHIN THAT AREA
        BECAUSE THE HIGHEST CELL AVERAGE IS NOT ALWAYS THE HIGHEST HALITE CELL IN THAT AREA
        """
        ## NEW WAY (SHOULD BE MORE EFFICIENT AND BETTER POSITIONING)
        average_manhattan = copy.deepcopy(self.myMatrix.cell_average.halite)

        ## POPULATE UNAVAILABLE AREA CLOSE TO SHIPYARD
        self.populate_shipyards_unavailable()

        ## GET INDEXES OF TOP N AVERAGES
        for _ in range(MyConstants.build.top_n):
            keep_looking = True
            quit = False

            while keep_looking:
                ## GET TOP AVERAGE LOCATION
                value_top_ave, indexes = get_n_max_values(average_manhattan)
                index_top_ave = self.get_closest_to_shipyard(indexes)

                loc_top_ave = (index_top_ave[0], index_top_ave[1])
                pos_top_ave = Position(loc_top_ave[1], loc_top_ave[0])                                                  ## Position(x, y)

                if self.unavailable_area[pos_top_ave.y][pos_top_ave.x] != Matrix_val.UNAVAILABLE:
                    ## SET THE SURROUNDING TO UNAVAILABLE
                    populate_manhattan(self.unavailable_area,
                                       Matrix_val.UNAVAILABLE,
                                       pos_top_ave,
                                       MyConstants.build.min_dist_btw_docks,
                                       Option.REPLACE)

                    ## TOP N IS THE HIGHEST HALITE WITHIN THE HIGHEST AVERAGE
                    ## GET TOP HALITE WITHIN THIS AREA
                    loc_top_halite_normalized, pos_top_halite_normalized = self.get_closest_top_halite(loc_top_ave, pos_top_ave)

                    ## POPULATE TOP N POSITIONS IN cell_average.top_N
                    self.myMatrix.cell_average.top_N[loc_top_halite_normalized[0]][loc_top_halite_normalized[1]] = value_top_ave

                    ## TOP N IS THE HIGHEST AVERAGE
                    # self.myMatrix.cell_average.top_N[pos_top_ave.y][pos_top_ave.x] = value_top_ave

                    keep_looking = False

                ## CHANGE THIS TO ZERO SO IT WONT BE TAKEN AS HIGHEST AVERAGE LATER
                average_manhattan[pos_top_ave.y][pos_top_ave.x] = Matrix_val.ZERO

                ## WHEN TOP AVERAGE IS BELOW THE TOTAL AVERAGE, WILL EXIT FOR LOOP
                if value_top_ave < self.myVars.average_halite:
                    quit = True
                    break

            if quit: break


    def populate_shipyards_unavailable(self):
        """
        POPULATE UNAVAILABLE AREA CLOSE TO SHIPYARD
        SO NO DOCK WILL BE TOO CLOSE TO SHIPYARD
        """
        ## POPULATE AROUND MY SHIPYARD
        populate_manhattan(self.unavailable_area,
                           Matrix_val.UNAVAILABLE,
                           self.game.me.shipyard.position,
                           MyConstants.build.min_dist_btw_docks,
                           Option.REPLACE)

        ## POPULATE AROUND ENEMY SHIPYARD
        for id, player in self.game.players.items():
            if id != self.game.me.id:
                populate_manhattan(self.unavailable_area,
                                   Matrix_val.UNAVAILABLE,
                                   player.shipyard.position,
                                   MyConstants.build.min_dist_btw_enemy_docks,
                                   Option.REPLACE)




    def get_closest_top_halite(self, loc_top_ave, pos_top_ave):
        """
        GET LOCATION/POSITION OF HIGHEST HALITE IN THE AREA (ITS MIDDLE IS THE POSITION GIVEN
        IF THERE ARE MULTIPLE RESULTS, NEED TO GET HIGHEST ONE CLOSE TO SHIPYARD

        :param loc_top_ave: LOCATION (CENTER) OF THE HIGHEST AVERAGE
        :param pos_top_ave: POSITION (CENTER) OF THE HIGHEST AVERAGE
        :return: LOCATION AND POSITION OF HIGHEST HALITE IN THIS SECTION
        """
        section_halite = Section(self.myMatrix.halite.amount, pos_top_ave, MyConstants.build.average_manhattan_distance)
        value_top_halite, indexes = get_n_max_values(section_halite.matrix)

        return self.get_loc_pos_top_halite(indexes, loc_top_ave, section_halite)


    def get_loc_pos_top_halite(self, indexes, loc_top_ave, section_halite):
        """
        GET LOCATION AND POSITION OF TOP HALITE IN THE GIVEN SECTION

        :param indexes:
        :param loc_top_ave:
        :param section_halite:
        :return: BEST LOC NORMALIZED AND POS NORMALIZED
        """
        closest = (10000, None, None)

        for ind in indexes:
            loc = (loc_top_ave[0] + (ind[0] - section_halite.center.y), loc_top_ave[1] + (ind[1] - section_halite.center.x))

            loc_normalized = (loc[0] % self.game.game_map.height, loc[1] % self.game.game_map.width)                    ## CONSIDER WHEN OUT OF BOUNDS
            pos_normalized = Position(loc_normalized[1], loc_normalized[0])

            dist_shipyard = calculate_distance(self.game.me.shipyard.position,
                                               pos_normalized,
                                               self)

            if dist_shipyard < closest[0]:
                closest = (dist_shipyard, loc_normalized, pos_normalized)

        return closest[1], closest[2]


    def get_closest_to_shipyard(self, indexes):
        """
        GET CLOSEST INDEX TO SHIPYARD

        :param indexes: INDEXES TO CHOOSE FROM
        :return: CLOSEST INDEX TO SHIPYARD
        """
        closest = (10000, None)
        for ind in indexes:
            dist_shipyard = calculate_distance(self.game.me.shipyard.position,
                                               Position(ind[1], ind[0]),
                                               self)

            if dist_shipyard < closest[0]:
                closest = (dist_shipyard, ind)

        return closest[1]


    def final_dock_placement(self):
        """
        POPULATE DOCK PLACEMENT
        """
        shipyard = self.game.me.shipyard
        matrix = copy.deepcopy(self.myMatrix.cell_average.top_N)

        ## OLD WAY
        print_matrix("Average: top N", self.myMatrix.cell_average.top_N)

        ## ELIMINATE TOP N CLOSE TO SHIPYARD
        populate_manhattan(matrix, Matrix_val.ZERO, shipyard.position, MyConstants.build.min_dist_btw_docks, Option.REPLACE)

        print_matrix("Eliminate close to shipyard: top N", matrix)

        ## ELIMINATE TOP N CLOSE TO ENEMY SHIPYARD
        for id, player in self.game.players.items():
            if id != self.game.me.id:
                enemyShipyard_position = player.shipyard.position
                populate_manhattan(matrix, Matrix_val.ZERO, enemyShipyard_position, MyConstants.build.min_dist_btw_docks, Option.REPLACE)

        print_matrix("Eliminate close to enemy shipyard: top N", matrix)


        ## GET COORD OF HIGHEST VALUE IN MATRIX
        ## LOCATED ON HIGHEST HALITE (WITH HIGHEST AVERAGE VALUE FROM THAT SECTION)
        curr_cell = (shipyard.position.y, shipyard.position.x)
        coord, distance, val = get_coord_closest(matrix.max(), matrix, self.myMatrix.distances.cell[curr_cell], Inequality.EQUAL)
        while val > 1:
            ## ELIMINATE TOP N CLOSE TO THIS AREA
            position = Position(coord[1], coord[0])
            populate_manhattan(matrix, Matrix_val.ONE, position, MyConstants.build.min_dist_btw_docks, Option.REPLACE)

            ## POPULATE DOCK PLACEMENT
            # # self.myMatrix.locations.dock_placement[position.y][position.x] = Matrix_val.ONE
            # for i in range(0, MyConstants.build.dock_manhattan):
            #     populate_manhattan(self.myMatrix.docks.placement, Matrix_val.ONE, position, i, Option.CUMMULATIVE)
            self.myMatrix.docks.placement[position.y][position.x] = Matrix_val.ONE

            ## GET COORD OF NEXT HIGHEST VALUE IN MATRIX
            coord, distance, val = get_coord_closest(matrix.max(), matrix, self.myMatrix.distances.cell[curr_cell], Inequality.EQUAL)

        print_matrix("Final dock placement", self.myMatrix.docks.placement)


        ## ORDERED DOCK
        # print_matrix("Average: top N", matrix)
        #
        # self.get_dock_order()
        #
        # indexes = np.argwhere(self.myMatrix.docks.order != Matrix_val.NINETY)
        # self.myMatrix.docks.placement[indexes] = Matrix_val.ONE


    def get_dock_order(self):
        """
        GET ORDER OF WHAT DOCKS TO BUILD
        """
        order_num = 1
        shipyard = self.game.me.shipyard
        shipyard_coord = (shipyard.position.y, shipyard.position.x)
        value_matrix = copy.deepcopy(self.myMatrix.cell_average.top_N)
        distance_coords = {shipyard_coord}

        ## ELIMINATE TOP N CLOSE TO SHIPYARD
        populate_manhattan(value_matrix, Matrix_val.ZERO, shipyard.position, MyConstants.build.min_dist_btw_docks, Option.REPLACE)

        print_matrix("Eliminate close to shipyard: top N", value_matrix)

        ## ELIMINATE TOP N CLOSE TO ENEMY SHIPYARD
        for id, player in self.game.players.items():
            if id != self.game.me.id:
                enemyShipyard_position = player.shipyard.position
                populate_manhattan(value_matrix, Matrix_val.ZERO, enemyShipyard_position, MyConstants.MIN_DIST_BTW_DOCKS,
                                   Option.REPLACE)

        print_matrix("Eliminate close to enemy shipyard: top N", value_matrix)

        ratio, distances = self.get_ratio(value_matrix, distance_coords)

        print_matrix("ratio order_num {}".format(order_num), ratio)

        ## GET HIGHEST RATIO
        coord, distance, val = get_coord_closest(ratio.max(), ratio, distances, Inequality.EQUAL)

        while val > 0:
            ## POPULATE ORDER MATRIX
            position = Position(coord[1], coord[0])
            self.myMatrix.docks.order[position.y][position.x] = order_num
            order_num += 1

            ## ELIMINATE TOP N CLOSE TO THIS AREA
            populate_manhattan(value_matrix, Matrix_val.ZERO, position, MyConstants.build.min_dist_btw_docks, Option.REPLACE)

            print_matrix("order matrix", self.myMatrix.docks.order)

            ## CLEAR THAT LOCATION
            value_matrix[position.y][position.x] = Matrix_val.ZERO

            ## ADD THIS COORD TO DISTANCES TO TAKE INTO ACCOUNT
            distance_coords.add(coord)

            ratio, distances = self.get_ratio(value_matrix, distance_coords)

            print_matrix("ratio order_num {}".format(order_num), ratio)

            ## GET HIGHEST RATIO
            coord, distance, val = get_coord_closest(ratio.max(), ratio, distances, Inequality.EQUAL)


    def get_ratio(self, value_matrix, distance_coords):
        """
        GET RATIO GIVEN THE DISTANCE MATRICES TO BE CONSIDERED
        """
        distances = []
        for coord in distance_coords:
            distances.append(copy.deepcopy(self.myMatrix.distances.cell[coord]))

        distance_matrix = myMinValueMatrix(*distances)

        ratio = np.divide(value_matrix, distance_matrix, out=np.zeros_like(value_matrix), where=distance_matrix != 0)

        return ratio, distance_matrix












