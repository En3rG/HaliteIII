from src.common.matrix import Data
from src.common.print import print_matrix

class Init(Data):
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

        self.populate_sectioned_halite()
        self.populate_sectioned_distances()
        self.populate_average_manhattan()

        self.populate_depleted()

        print_matrix("myShipyard", self.matrix.myShipyard)
        print_matrix("halite", self.matrix.halite)
        print_matrix("depleted shipyard distances", self.matrix.depleted.shipyard_distances)
        print_matrix("depleted harvest_turns", self.matrix.depleted.harvest_turns)
        print_matrix("depleted total turns", self.matrix.depleted.total_turns)
        print_matrix("depleted harvest area", self.matrix.depleted.harvest_area)






