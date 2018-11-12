from src.common.matrix import fill_circle, print_matrix, Matrices, Matrix


class Data(Matrices):
    def __init__(self, game):
        super().__init__(game)

        self.all_ships = set(self.me._ships.keys())  ## ALL SHIPS
        self.ships_to_move = set(self.me._ships.keys())  ## SHIPS TO MOVE
        self.ships_returning = set()  ## SHIPS RETURNING HALITE
        self.ships_harvesting = set()  ## SHIPS HARVESTING/STILL
        self.ships_retreating = set()  ## SHIPS RETREATING BEFORE GAME ENDS

        self.update_matrix()


    def update_matrix(self):
        """
        POPULATE ALL MATRICES
        """
        self.populate_halite()
        self.populate_myShipyard()
        self.populate_enemyShipyard()
        self.populate_myShips()
        self.populate_enemyShips_influenced()
        self.populate_cost()
        self.populate_harvest()


        # print_matrix("", self.matrix.halite)
        # print_matrix("", self.matrix.myShipyard)
        # print_matrix("", self.matrix.enemyShipyard)
        # print_matrix("", self.matrix.myShips)
        # print_matrix("", self.matrix.myShipsID)
        # print_matrix("", self.matrix.enemyShips)
        # print_matrix("", self.matrix.cost)
        # print_matrix("", self.matrix.harvest)
        # print_matrix("", self.matrix.distances)
        # print_matrix("", self.matrix.influenced)
        # print_matrix("unsafe", self.matrix.unsafe)








