from src.common.matrix import Matrices
from src.common.print import print_matrix

class Start(Matrices):
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

        print_matrix("distances (0,0)", self.matrix.sectioned.distances[(0,0)])



