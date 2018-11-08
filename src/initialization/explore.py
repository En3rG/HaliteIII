import logging
import numpy as np
from src.common import Matrix_val
from hlt.positionals import Position


def rounder(x):
    """
    SINCE np.round() DOESNT ALWAYS ROUND UP XX.5
    MAKING MY OWN FUNCTION THEN np.vectorize IT
    :param x:
    :return:
    """
    if (x - int(x) >= 0.5):
        return np.ceil(x)
    else:
        return np.floor(x)

myRound = np.vectorize(rounder)

class Exploration():
    """
    TAKE ADVANTAGE OF 30 SECONDS INITIALIZATION TIME
    """
    def __init__(self, game):
        logging.debug("Starting Exploration...")

        self.game = game
        self.me = game.me                       ## MY PLAYER OBJECT
        self.my_id = game.me.id
        self.players = game.players             ## DICTIONARY OF Players, BASE ON PLAYER IDs
        self.game_map = game.game_map
        self.map_width = self.game_map.width
        self.map_height = self.game_map.height

        self.matrix = Matrices(self.map_height, self.map_width)
        self.update_matrix()
        self.test_print()


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


    def populate_halite(self):
        """
        POPULATE MATRIX MAP WITH HALITE VALUES
        """
        halites = [ [ cell.halite_amount for cell in row ] for row in self.game_map._cells]
        self.matrix.halite = np.array(halites, dtype=np.int16)


    def populate_myShipyard(self):
        """
        POPULATE MATRIX MAP WITH ALLY_SHIPYARD.value WHERE MY SHIPYARD IS LOCATED
        """
        myShipyard_position = self.me.shipyard.position
        self.matrix.myShipyard[myShipyard_position.y][myShipyard_position.x] = Matrix_val.ALLY_SHIPYARD.value


    def populate_enemyShipyard(self):
        """
        POPULATE MATRIX MAP WITH ENEMY_SHIPYARD.value WHERE ENEMY SHIPYARDS ARE LOCATED
        """
        for id, player in self.players.items():
            if id != self.my_id:
                enemyShipyard_position = player.shipyard.position
                self.matrix.enemyShipyard[enemyShipyard_position.y][enemyShipyard_position.x] = Matrix_val.ENEMY_SHIPYARD.value


    def populate_distances(self):
        """
        POPULATE MATRIX DISTANCES FROM THE CENTER
        IF THE MAP IS AN EVEN LENGTH, SUBTRACT 1 SO THAT THE CENTER IS EXACT
        """
        if self.map_width % 2 == 0: ## EVEN
            width = self.map_width - 1
        else: ## ODD
            width = self.map_width

        center = width // 2
        self.matrix.distances.center = center
        start = Position(center, center)

        for y in range(width):
            for x in range(width):
                destination = Position(x, y)
                self.matrix.distances.matrix[y][x] = self.game_map.calculate_distance(start, destination)


    def populate_cost(self):
        """
        POPULATE MATRIX COST
        """
        cost = self.matrix.halite * 0.1
        #self.matrix.cost = np.round(cost)           ## FYI, numpy.round IS UNBIASED FOR XX.5 (BY DESIGN)
        self.matrix.cost = myRound(cost)

    def populate_harvest(self):
        """
        POPULATE MATRIX HARVEST
        """
        harvest = self.matrix.halite * 0.25
        #self.matrix.harvest = np.round(harvest)     ## FYI, numpy.round IS UNBIASED FOR XX.5 (BY DESIGN)
        self.matrix.harvest = myRound(harvest)

    def test_print(self):
        """
        FOR TESTING PURPOSES ONLY
        """
        np.set_printoptions(threshold=np.inf,linewidth=np.inf)              ## SET NUMPY PRINT THRESHOLD TO INFINITY
        logging.debug("Print out matrix halite: {}".format(self.matrix.halite))
        logging.debug("Print out matrix myShipyard: {}".format(self.matrix.myShipyard))
        logging.debug("Print out matrix enemyShipyard: {}".format(self.matrix.enemyShipyard))
        logging.debug("Print out matrix cost: {}".format(self.matrix.cost))
        logging.debug("Print out matrix harvest: {}".format(self.matrix.harvest))
        logging.debug("Print out matrix distances: {}".format(self.matrix.distances.matrix))
        np.set_printoptions(threshold=10)                                   ## SET NUMPY PRINT THRESHOLD TO 10


class Matrices():
    def __init__(self, map_height, map_width):
        self.halite = np.zeros((map_height, map_width), dtype=np.int16)
        self.myShipyard = np.zeros((map_height, map_width), dtype=np.int16)
        self.enemyShipyard = np.zeros((map_height, map_width), dtype=np.int16)
        self.cost = None
        self.harvest = None
        self.distances = Matrix_distances(map_height, map_width)


class Matrix_distances():
    def __init__(self, map_height, map_width):
        self.matrix = np.zeros((map_height, map_width), dtype=np.int16)
        self.center = None      ## set at update_matrix





