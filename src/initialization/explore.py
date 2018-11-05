import logging
import numpy as np
from src.common import Matrix_val

"""
Gather as much data as possible during initialization period (30 seconds)
"""
class Exploration():
    def __init__(self, game):
        self.game = game
        self.me = game.me                       ## My Player object
        self.my_id = game.me.id
        self.players = game.players             ## Dictionary of Players, base on player IDs
        self.game_map = game.game_map
        self.map_width = self.game_map.width
        self.map_height = self.game_map.height
        self.map_rows = self.game_map._cells    ## list of MapCell (in a row)

        self.matrix_map = np.zeros((self.map_height, self.map_width), dtype=np.int16)
        self.update_matrix()
        self.test_print()


    def update_matrix(self):
        """
        Populate matrix with halite amount
        Populate matrix with own shipyard
        Populate matrix with enemy shipyards

        :return: None
        """
        def populate_halite():
            for y, row in enumerate(self.map_rows):
                for x, cell in enumerate(row):
                    self.matrix_map[y][x] = cell.halite_amount

        def populate_myShipyard():
            myShipyard_position = self.me.shipyard.position
            self.matrix_map[myShipyard_position.y][myShipyard_position.x] = Matrix_val.ALLY_SHIPYARD.value

        def populate_enemyShipyard():
            for id, player in self.players.items():
                if id != self.my_id:
                    enemyShipyard_position = player.shipyard.position
                    self.matrix_map[enemyShipyard_position.y][enemyShipyard_position.x] = Matrix_val.ENEMY_SHIPYARD.value

        populate_halite()
        populate_myShipyard()
        populate_enemyShipyard()


    def test_print(self):
        np.set_printoptions(threshold=np.inf,linewidth=np.inf)              ## SET NUMPY PRINT THRESHOLD TO INFINITY
        logging.debug("Print out matrix_map: {}".format(self.matrix_map))
        np.set_printoptions(threshold=10)                                   ## SET NUMPY PRINT THRESHOLD TO 10




