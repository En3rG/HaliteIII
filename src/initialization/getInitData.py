from src.common.matrix.data import Data
from src.common.print import print_matrix
from src.common.matrix.data import Section
from src.common.matrix.functions import populate_manhattan, get_index_highest_val, get_coord_closest, \
    get_n_largest_values, get_cell_averages, get_n_max_values, calculate_distance
from src.common.values import Matrix_val, MyConstants
from hlt.positionals import Position

import logging
import copy

class GetInitData(Data):
    def __init__(self, game):
        super().__init__(game)
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
        self.populate_top_halite()
        self.get_average_halite()

        self.populate_sectioned_halite()
        self.populate_sectioned_distances()

        self.populate_cell_averages()

        self.populate_depletion()

        self.populate_dock_placement()


        # print_matrix("halite", self.myMatrix.halite.amount)
        # print_matrix("top halite", self.myMatrix.halite.top_amount)
        # logging.debug("Halite average: {}".format(self.myVars.average_halite))
        #
        # print_matrix("Average: manhattan", self.myMatrix.cell_average.manhattan)
        # print_matrix("Average: top N", self.myMatrix.cell_average.top_N)
        #
        # print_matrix("depletion: shipyard distances", self.myMatrix.depletion.shipyard_distances)
        # print_matrix("depletion: harvest_turns", self.myMatrix.depletion.harvest_turns)
        # print_matrix("depletion: total turns", self.myMatrix.depletion.total_turns)
        # print_matrix("depletion: harvest area", self.myMatrix.depletion.harvest_area)


    def populate_dock_placement(self):
        self.get_top_N_averages()
        self.final_dock_placement()


    def get_top_N_averages(self):
        """
        POPULATE WHERE TOP N PLACES ARE, BASED ON HIGHEST AVERAGE CELL MANHATTAN
        THEN GET HIGHEST HALITE AMOUNT IN THAT SECTION
        BECAUSE THE HIGHEST CELL AVERAGE IS NOT ALWAYS THE HIGHEST HALITE CELL IN THAT AREA
        """
        average_manhattan = copy.deepcopy(self.myMatrix.cell_average.manhattan)

        ## GET INDEXES OF TOP N
        ## REMOVE ITS SURROUNDING AVERAGES, SO NEXT TOP CELL WONT BE AROUND IT
        for _ in range(MyConstants.TOP_N):
            print_matrix("average manhattan", average_manhattan)

            ## GET TOP AVERAGE LOCATION
            value_top_ave, indexes = get_n_max_values(average_manhattan)
            indx_top_ave = self.get_closest_to_shipyard(indexes)

            logging.debug("value_top_ave {}, indx_top_ave {}".format(value_top_ave, indx_top_ave))

            loc_top_ave = (indx_top_ave[0], indx_top_ave[1])
            pos_top_ave = Position(loc_top_ave[1], loc_top_ave[0])  ## Position(x, y)

            ## GET TOP HALITE CLOSE TO TOP AVERAGE LOCATION
            loc_top_halite_normalized, pos_top_halite_normalized = self.get_closest_top_halite(loc_top_ave, pos_top_ave)

            ## POPULATE TOP N POSITIONS IN cell_average.top_N
            self.myMatrix.cell_average.top_N[loc_top_halite_normalized[0]][loc_top_halite_normalized[1]] = value_top_ave

            ## COLLECT LOCATIONS
            ## REMOVE SURROUNDING TOP HALITE
            populate_manhattan(average_manhattan,
                               Matrix_val.ZERO,
                               pos_top_halite_normalized,
                               MyConstants.AVERAGE_MANHATTAN_DISTANCE,
                               cummulative=False)

            ## RECALCULATE CELL AVERAGES
            average_manhattan = get_cell_averages(self.game.game_map.height, self.game.game_map.width,
                                                  average_manhattan)


    def get_closest_top_halite(self, loc_top_ave, pos_top_ave):
        """
        GET LOCATION/POSITION OF HIGHEST HALITE IN THE SECTION
        IF THERE ARE MULTIPLE RESULTS, NEED TO GET HIGHEST ONE CLOSE TO SHIPYARD

        :param loc_top_ave: LOCATION (CENTER) OF THE HIGHEST AVERAGE
        :param pos_top_ave: POSITION (CENTER) OF THE HIGHEST AVERAGE
        :return: LOCATION AND POSITION OF HIGHEST HALITE IN THIS SECTION
        """
        logging.debug("pos_top_ave {}".format(pos_top_ave))

        section_halite = Section(self.myMatrix.halite.amount, pos_top_ave, MyConstants.AVERAGE_MANHATTAN_DISTANCE)

        print_matrix("section_halite:", section_halite.matrix)

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

            loc_normalized = (loc[0] % self.game.game_map.height, loc[1] % self.game.game_map.width)  ## CONSIDER WHEN OUT OF BOUNDS
            pos_normalized = Position(loc_normalized[1], loc_normalized[0])

            dist_shipyard = calculate_distance(self.game.me.shipyard.position,
                                               pos_normalized,
                                               self.game.game_map.height,
                                               self.game.game_map.width)

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
                                               self.game.game_map.height,
                                               self.game.game_map.width)

            if dist_shipyard < closest[0]:
                closest = (dist_shipyard, ind)

        return closest[1]


    def final_dock_placement(self):
        """
        POPULATE DOCK PLACEMENT
        """
        shipyard = self.game.me.shipyard
        matrix = copy.deepcopy(self.myMatrix.cell_average.top_N)

        print_matrix("Average: top N", self.myMatrix.cell_average.top_N)

        ## ELIMINATE TOP N CLOSE TO SHIPYARD
        populate_manhattan(matrix, Matrix_val.ZERO, shipyard.position, MyConstants.MIN_DIST_BTW_DOCKS)

        print_matrix("Eliminate close to shipyard: top N", self.myMatrix.cell_average.top_N)

        ## GET COORD OF HIGHEST VALUE IN MATRIX
        ## LOCATED ON HIGHEST HALITE (WITH HIGHEST AVERAGE VALUE FROM THAT SECTION)
        curr_cell = (shipyard.position.y, shipyard.position.x)
        coord, distance, val = get_coord_closest(matrix.max(), matrix, self.myMatrix.distances[curr_cell])
        while val != 1:
            ## ELIMINATE TOP N CLOSE TO THIS AREA
            position = Position(coord[1], coord[0])
            populate_manhattan(matrix, Matrix_val.ONE, position, MyConstants.MIN_DIST_BTW_DOCKS)
            self.myMatrix.locations.dock_placement[position.y][position.x] = Matrix_val.ONE

            ## GET COORD OF HIGHEST VALUE IN MATRIX
            coord, distance, val = get_coord_closest(matrix.max(), matrix, self.myMatrix.distances[curr_cell])

        print_matrix("Final dock placement", self.myMatrix.locations.dock_placement)















