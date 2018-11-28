from src.common.matrix.data import Data
from src.common.print import print_matrix
import logging

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



        print_matrix("halite", self.matrix.halite)
        print_matrix("top halite", self.matrix.top_halite)
        logging.debug("Halite average: {}".format(self.average_halite))

        print_matrix("Average: manhattan", self.matrix.average.manhattan)
        print_matrix("Average: top N", self.matrix.average.top_N)

        print_matrix("depletion: shipyard distances", self.matrix.depletion.shipyard_distances)
        print_matrix("depletion: harvest_turns", self.matrix.depletion.harvest_turns)
        print_matrix("depletion: total turns", self.matrix.depletion.total_turns)
        print_matrix("depletion: harvest area", self.matrix.depletion.harvest_area)






