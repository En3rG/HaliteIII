from src.common.matrix.data import Data
from src.common.print import print_heading, print_matrix

class MyData(Data):
    def __init__(self, game, init_data, prev_data, halite_stats):
        super().__init__(game)
        self.halite_stats = halite_stats
        self.init_data = init_data
        self.command_queue = []

        self.all_ships = set(self.me._ships.keys())         ## ALL SHIPS
        self.ships_to_move = set(self.me._ships.keys())     ## SHIPS TO MOVE
        self.ships_returning = set()                        ## SHIPS RETURNING HALITE
        self.ships_kicked = set()

        self.count_ships_died(prev_data)                    ## RECORD DROPPED HALITE, BASED ON SHIPS THAT DIED

        print_heading("All ships [{} total]: {}".format(len(self.all_ships), self.all_ships))

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
        self.populate_myShips()
        self.populate_docks()
        self.populate_enemyShips_influenced()

        #self.populate_sectioned_halite()

        self.populate_top_halite()
        self.get_average_halite()


    def count_ships_died(self, prev_data):
        if prev_data:
            self.ships_died = prev_data.all_ships - self.all_ships
            self.halite_stats.record_drop(self.ships_died, prev_data)









