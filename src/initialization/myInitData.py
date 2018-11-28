from src.common.matrix.data import Data
from src.common.print import print_matrix
from src.common.matrix.functions import populate_manhattan, get_index_highest_val, get_coord_closest
from src.common.values import Matrix_val, MyConstants
from hlt.positionals import Position
import logging
import copy

class MyInitData(Data):
    def __init__(self, game):
        super().__init__(game)
        self.update_matrix()

    def update_matrix(self):
        """
        POPULATE ALL MATRICES
        """
        self.populate_halite()
        self.populate_myShipyard()
        self.populate_enemyShipyard()
        self.populate_cost()
        self.populate_harvest()
        self.populate_docks()

        self.populate_cell_distances()
        self.populate_top_halite()
        self.get_average_halite()

        self.populate_sectioned_halite()
        self.populate_sectioned_distances()

        self.populate_cell_averages()

        self.populate_depletion()

        self.populate_dock_placement()


        # print_matrix("halite", self.matrix.halite)
        # print_matrix("top halite", self.matrix.top_halite)
        # logging.debug("Halite average: {}".format(self.average_halite))
        #
        # print_matrix("Average: manhattan", self.matrix.average.manhattan)
        # print_matrix("Average: top N", self.matrix.average.top_N)
        #
        # print_matrix("depletion: shipyard distances", self.matrix.depletion.shipyard_distances)
        # print_matrix("depletion: harvest_turns", self.matrix.depletion.harvest_turns)
        # print_matrix("depletion: total turns", self.matrix.depletion.total_turns)
        # print_matrix("depletion: harvest area", self.matrix.depletion.harvest_area)


    def populate_dock_placement(self):
        shipyard = self.me.shipyard
        matrix = copy.deepcopy(self.matrix.average.top_N)

        print_matrix("Average: top N", self.matrix.average.top_N)

        ## ELIMINATE TOP N CLOSE TO SHIPYARD
        populate_manhattan(matrix, Matrix_val.ZERO, shipyard.position, MyConstants.MIN_DIST_BTW_DOCKS)

        print_matrix("Eliminate close to shipyard: top N", self.matrix.average.top_N)

        ## GET COORD OF HIGHEST VALUE IN MATRIX
        curr_cell = (shipyard.position.y, shipyard.position.x)
        coord, distance, val = get_coord_closest(matrix.max(), matrix, self.matrix.distances[curr_cell])
        while val != 1:
            ## ELIMINATE TOP N CLOSE TO THIS AREA
            position = Position(coord[1], coord[0])
            populate_manhattan(matrix, Matrix_val.ONE, position, MyConstants.MIN_DIST_BTW_DOCKS)
            self.matrix.dock_placement[position.y][position.x] = Matrix_val.ONE

            ## GET COORD OF HIGHEST VALUE IN MATRIX
            coord, distance, val = get_coord_closest(matrix.max(), matrix, self.matrix.distances[curr_cell])

        print_matrix("Final dock placement", self.matrix.dock_placement)











