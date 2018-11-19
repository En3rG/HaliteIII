from src.common.matrix import Matrices
from src.common.print import print_heading, print_matrix

class Data(Matrices):
    def __init__(self, game, prev_data, halite_stats):
        super().__init__(game)

        self.all_ships = set(self.me._ships.keys())         ## ALL SHIPS
        self.ships_to_move = set(self.me._ships.keys())     ## SHIPS TO MOVE
        self.ships_returning = set()                        ## SHIPS RETURNING HALITE
        self.ships_harvesting = set()                       ## SHIPS HARVESTING/STILL
        self.ships_retreating = set()                       ## SHIPS RETREATING BEFORE GAME ENDS

        self.count_ships_died(prev_data, halite_stats)      ## RECORD DROPPED HALITE, BASED ON SHIPS THAT DIED

        print_heading("All ships [{} total]: {}".format(len(self.all_ships), self.all_ships))

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

        self.populate_sectioned_halite()


        # print_matrix("", self.matrix.halite)
        # print_matrix("", self.matrix.myShipyard)
        # print_matrix("", self.matrix.enemyShipyard)
        # print_matrix("", self.matrix.myShips)
        # print_matrix("", self.matrix.myShipsID)
        # print_matrix("", self.matrix.enemyShips)
        # print_matrix("", self.matrix.cost)
        # print_matrix("", self.matrix.harvest)
        # print_matrix("", self.matrix.distances)
        # print_matrix("Influenced", self.matrix.influenced)
        # print_matrix("safe", self.matrix.safe)
        # print_matrix("Potential Enemy Collisions", self.matrix.potential_enemy_collisions)
        # print_matrix("Potential Ally Collisions", self.matrix.potential_ally_collisions)


    def count_ships_died(self, prev_data, halite_stats):
        if prev_data:
            self.ships_died = prev_data.all_ships - self.all_ships
            halite_stats.record_drop(self.ships_died, prev_data)









