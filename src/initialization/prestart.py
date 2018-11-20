from src.common.matrix import Matrices
from src.common.print import print_matrix

class Init(Matrices):
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

        print_matrix("halite", self.matrix.halite)

        




