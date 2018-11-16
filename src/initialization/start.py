from src.common.matrix import Matrices

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
        self.populate_distances()
        self.populate_cost()
        self.populate_harvest()