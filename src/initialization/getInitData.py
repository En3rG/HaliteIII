from src.common.matrix.data import Data
from src.common.print import print_matrix
from src.common.matrix.data import Section
from src.common.matrix.functions import populate_manhattan, get_index_highest_val, get_coord_closest, \
    get_n_largest_values, get_cell_averages
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


        # print_matrix("halite", self.matrix.halite.amount)
        # print_matrix("top halite", self.matrix.halite.top_amount)
        # logging.debug("Halite average: {}".format(self.average_halite))
        #
        # print_matrix("Average: manhattan", self.matrix.cell_average.manhattan)
        # print_matrix("Average: top N", self.matrix.cell_average.top_N)
        #
        # print_matrix("depletion: shipyard distances", self.matrix.depletion.shipyard_distances)
        # print_matrix("depletion: harvest_turns", self.matrix.depletion.harvest_turns)
        # print_matrix("depletion: total turns", self.matrix.depletion.total_turns)
        # print_matrix("depletion: harvest area", self.matrix.depletion.harvest_area)


    def get_top_N_averages(self):
        ## POPULATE WHERE TOP N PLACES ARE
        ## NEED TO GET HIGHEST HALITE AMOUNT IN THAT AREA
        ## THE HIGHEST CELL AVERAGE IS NOT ALWAYS THE HIGHEST HALITE CELL IN THAT AREA
        top_indexes = set()
        average_manhattan = copy.deepcopy(self.matrix.cell_average.manhattan)

        ## GET INDEXES OF TOP N
        ## REMOVE ITS SURROUNDING AVERAGES, SO NEXT TOP CELL WONT BE AROUND IT
        for _ in range(MyConstants.TOP_N):
            print_matrix("average manhattan", average_manhattan)

            ## GET TOP AVERAGE LOCATION
            value_top_ave, indx_top_ave = get_n_largest_values(average_manhattan, 1)

            logging.debug("value_top_ave {}, indx_top_ave {}".format(value_top_ave, indx_top_ave))

            loc_top_ave = (indx_top_ave[0][0], indx_top_ave[1][0])
            pos_top_ave = Position(loc_top_ave[1], loc_top_ave[0])  ## Position(x, y)

            ## GET TOP HALITE CLOSE TO TOP AVERAGE LOCATION
            section_halite = Section(self.matrix.halite.amount, pos_top_ave, MyConstants.AVERAGE_MANHATTAN_DISTANCE)
            value_top_halite, indx_top_halite_section = get_n_largest_values(section_halite.matrix, 1)
            loc_top_halite = (loc_top_ave[0] + (indx_top_halite_section[0][0] - section_halite.center.y),
                              loc_top_ave[1] + (indx_top_halite_section[1][0] - section_halite.center.x))
            loc_top_halite_normalized = (loc_top_halite[0] % self.game.game_map.height,
                                         loc_top_halite[1] % self.game.game_map.width)  ## CONSIDER WHEN OUT OF BOUNDS
            pos_top_halite_normalized = Position(loc_top_halite_normalized[1], loc_top_halite_normalized[0])

            ## COLLECT LOCATIONS
            ## REMOVE SURROUNDING TOP HALITE
            top_indexes.add(loc_top_halite_normalized)
            populate_manhattan(average_manhattan, 0, pos_top_halite_normalized, MyConstants.AVERAGE_MANHATTAN_DISTANCE,
                               cummulative=False)

            ## RECALCULATE CELL AVERAGES
            average_manhattan = get_cell_averages(self.game.game_map.height, self.game.game_map.width, average_manhattan)

        ## POPULATE TOP N POSITIONS IN cell_average.top_N
        for ind in top_indexes:
            self.matrix.cell_average.top_N[ind[0]][ind[1]] = self.matrix.cell_average.manhattan[ind[0]][ind[1]]


    def final_dock_placement(self):
        shipyard = self.game.me.shipyard
        matrix = copy.deepcopy(self.matrix.cell_average.top_N)

        print_matrix("Average: top N", self.matrix.cell_average.top_N)

        ## ELIMINATE TOP N CLOSE TO SHIPYARD
        populate_manhattan(matrix, Matrix_val.ZERO, shipyard.position, MyConstants.MIN_DIST_BTW_DOCKS)

        print_matrix("Eliminate close to shipyard: top N", self.matrix.cell_average.top_N)

        ## GET COORD OF HIGHEST VALUE IN MATRIX
        curr_cell = (shipyard.position.y, shipyard.position.x)
        coord, distance, val = get_coord_closest(matrix.max(), matrix, self.matrix.distances[curr_cell])
        while val != 1:
            ## ELIMINATE TOP N CLOSE TO THIS AREA
            position = Position(coord[1], coord[0])
            populate_manhattan(matrix, Matrix_val.ONE, position, MyConstants.MIN_DIST_BTW_DOCKS)
            self.matrix.locations.dock_placement[position.y][position.x] = Matrix_val.ONE

            ## GET COORD OF HIGHEST VALUE IN MATRIX
            coord, distance, val = get_coord_closest(matrix.max(), matrix, self.matrix.distances[curr_cell])

        print_matrix("Final dock placement", self.matrix.locations.dock_placement)


    def populate_dock_placement(self):
        self.get_top_N_averages()
        self.final_dock_placement()












