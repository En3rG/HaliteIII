from src.common.matrix.data import Data
from src.common.print import print_heading, print_matrix
from src.common.values import MyConstants
import logging

class GetData(Data):
    def __init__(self, game, init_data, prev_data, halite_stats):
        super().__init__(game)

        print_heading("Gathering data......")

        self.prev_data = prev_data
        self.halite_stats = halite_stats
        self.init_data = init_data
        self.command_queue = []
        self.starting_halite = init_data.myVars.total_halite
        self.count_ships_died()                                                                                 ## RECORD DROPPED HALITE, BASED ON SHIPS THAT DIED

        logging.debug("All ships [{} total]: {}".format(len(self.mySets.ships_all), self.mySets.ships_all))

        self.update_matrix()

        self.get_rate_of_decay()


    def update_matrix(self):
        """
        POPULATE ALL MATRICES
        """
        self.populate_halite()
        self.populate_myShipyard_docks()
        self.populate_enemyShipyard_docks()
        self.populate_cost()
        self.populate_myShips()
        self.populate_enemyShips_influenced()
        self.populate_harvest()

        #self.populate_sectioned_halite()

        # self.populate_top_halite()

        self.get_mean_median_halite()

        self.populate_cell_averages(MyConstants.explore.average_manhattan_distance)

        self.update_dock_placement()


    def get_rate_of_decay(self):
        """
        GET RATE OF DECAYS FROM PREVIOUSLY
        """
        if self.prev_data:
            self.myLists.ratio_left_halite = self.prev_data.ratio_left_halite


    def count_ships_died(self):
        """
        COUNT SHIPS DIED
        WHICH SHIPS COLLIDED WITH ALLY SHIPS
        WHICH SHIPS COLLIDED WITH ENEMY SHIPS
        """
        if self.prev_data:
            self.mySets.ships_died = self.prev_data.ships_all - self.mySets.ships_all
            logging.debug("Ships died: {}".format(self.mySets.ships_died))

            for v in self.prev_data.positions_taken.values():
                if len(v) > 1: self.mySets.ships_ally_collision.update(v)
            logging.debug("Ships collided (ally): {}".format(self.mySets.ships_ally_collision))

            self.mySets.ships_enemy_collision = self.mySets.ships_died - self.mySets.ships_ally_collision
            logging.debug("Ships collided (enemy): {}".format(self.mySets.ships_enemy_collision))
            self.halite_stats.record_drop(self.mySets.ships_died, self.prev_data)









