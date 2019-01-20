from src.common.move.moves import Moves
from src.common.move.harvests import Harvests
from src.common.print import print_heading
from src.common.orderedSet import OrderedSet
from src.common.move.explores import Explores
from hlt.positionals import Position
from src.common.move.deposits import Deposits
from src.common.values import MoveMode, Matrix_val, Inequality, MyConstants
from src.common.points import FarthestShip, DepositPoints, ExploreShip
from src.common.matrix.functions import get_coord_closest, count_manhattan
from hlt import constants
import heapq
import logging
import copy
import numpy as np


class Target():
    def __init__(self, ratio, ship_id, destination, matrix_ratio):
        self.ratio = ratio
        self.ship_id = ship_id
        self.destination = destination
        self.matrix_ratio = matrix_ratio

class ExploreTarget(Moves, Harvests, Deposits, Explores):
    def __init__(self, data, prev_data):
        Moves.__init__(self, data, prev_data)

        self.heap_dist = []
        self.heap_set = set()
        self.heap_set_dist = set()
        self.heap_explore = []
        self.ships_kicked_temp = OrderedSet()

        self.halite_matrix = self.data.myMatrix.halite.updated_amount
        self.average_matrix = self.data.myMatrix.cell_average.halite

        if data.myVars.explore_disable_bonus:
            #self.harvest_matrix = copy.deepcopy(self.data.myMatrix.halite.harvest)
            #self.harvest_matrix = self.data.myMatrix.halite.updated_harvest
            self.harvest_matrix = self.data.myMatrix.halite.updated_harvest * MyConstants.explore.score_harvest_ratio \
                                  + self.average_matrix * MyConstants.explore.score_average_ratio
        else:
            #self.harvest_matrix = copy.deepcopy(self.data.myMatrix.halite.harvest_with_bonus)
            #self.harvest_matrix = self.data.myMatrix.halite.updated_harvest_with_bonus
            self.harvest_matrix = self.data.myMatrix.halite.updated_harvest_with_bonus * MyConstants.explore.score_harvest_ratio \
                                  + self.average_matrix * MyConstants.explore.score_average_ratio

        self.taken_matrix = np.zeros((self.data.game.game_map.height, self.data.game.game_map.width), dtype=np.int16)
        self.taken_matrix.fill(1)                                                                                       ## ZERO WILL BE FOR TAKEN CELL
        # r, c = np.where(self.data.myMatrix.locations.safe == Matrix_val.UNSAFE)
        # self.taken_matrix[r, c] = Matrix_val.ZERO
        #
        # self.taken_destinations = set()

        self.move_ships()

    def populate_heap_return(self, ship):
        """
        GET DISTANCE FROM SHIPYARD/DOCKS
        """
        ## TAKING DOCKS INTO ACCOUNT
        if ship.id not in self.heap_set_dist:
            self.heap_set_dist.add(ship.id)

            curr_cell = (ship.position.y, ship.position.x)
            coord, distance, value = get_coord_closest(Matrix_val.ONE,
                                                       self.data.myMatrix.locations.myDocks,
                                                       self.data.init_data.myMatrix.distances.cell[curr_cell],
                                                       Inequality.EQUAL)
            dock_position = Position(coord[1], coord[0])
            directions = self.get_directions_target(ship, dock_position)
            num_directions = len(directions)
            s = FarthestShip(distance, num_directions, ship.id, directions, dock_position)
            heapq.heappush(self.heap_dist, s)


    def move_ships(self):
        print_heading("Populate Explore targets and depositing ships......")

        for ship_id in (self.data.mySets.ships_all & self.data.mySets.ships_to_move):
            ship = self.data.game.me._ships.get(ship_id)

            ## GATHER SHIPS THAT ARE FULL
            if ship.is_full:
                self.populate_heap_return(ship)

            ## GATHER SHIPS THAT WERE RETURNING BEFORE
            elif ship_id in self.prev_data.ships_returning and (ship.position.y, ship.position.x) not in self.data.mySets.dock_coords:
                self.populate_heap_return(ship)

            ## GATHER THE REST FOR FURTHER ANALYSIS
            else:
                self.populate_heap(ship_id)

        ## GATHER TARGET / DEPOSITING
        while self.heap_explore:
            s = heapq.heappop(self.heap_explore)

            ## OLD WAY (MARK TAKEN)
            #explore_destination = self.isDestination_untaken(s)
            ## NEW WAY
            explore_destination = self.isDestination_updated(s)

            if s.ship_id in self.data.mySets.ships_to_move and explore_destination:
                logging.debug(s)

                ship = self.data.game.me._ships.get(s.ship_id)
                current_harvest = self.data.myMatrix.halite.harvest_with_bonus[ship.position.y][ship.position.x]
                target_harvest = self.harvest_matrix[explore_destination.y][explore_destination.x]

                if ship.halite_amount >= MyConstants.deposit.potentially_enough_cargo \
                        and (ship.halite_amount + (current_harvest * MyConstants.deposit.over_harvest_percent) >= 1000 \
                              or ship.halite_amount + (target_harvest * MyConstants.deposit.over_harvest_percent) >= 1000):
                    self.populate_heap_return(ship)

                # elif ship.halite_amount >= MyConstants.deposit.potentially_enough_cargo and self.hasTooManyEnemy(ship):
                #     self.populate_heap_return(ship)

                elif ship.halite_amount > MyConstants.attack.kamikaze_halite_max \
                        and self.data.myMatrix.locations.engage_enemy[MyConstants.attack.kamikaze_retreat_distance][ship.position.y][ship.position.x] == Matrix_val.ONE:
                    self.populate_heap_return(ship)


                else:
                    self.data.myDicts.explore_ship.setdefault(s.ship_id, None)
                    self.data.myDicts.explore_ship[s.ship_id] = s
                    self.data.myLists.explore_target.append(Target(s.ratio, s.ship_id, s.destination, s.matrix_ratio))

                    ## OLD WAY (MARK TAKEN)
                    #self.mark_taken_udpate_top_halite(explore_destination)
                    ## NEW WAY (DEDUCT HALITE TO BE HARVESTED)
                    self.update_harvest_matrix(s.ship_id, explore_destination)


        ## GATHER ALL SHIPS DEPOSITING, TO BE ALL MOVED LATER
        while self.heap_dist:
            s = heapq.heappop(self.heap_dist)
            logging.debug(s)
            if s.ship_id in self.data.mySets.ships_to_move:
                ship = self.data.game.me._ships.get(s.ship_id)
                # self.depositNow(ship, s.dock_position, s.directions)

                ## INSTEAD OF MOVING IT NOW, SAVE THAT DATA AND MOVE THE SHIPS LATER
                #if s.ship_id in self.data.mySets.ships_to_move: self.data.mySets.ships_to_move.remove(ship.id)
                self.data.mySets.deposit_ships.add(s.ship_id)

                self.data.myDicts.deposit_ship[s.ship_id] = s


    def populate_heap(self, ship_id):
        if ship_id not in self.heap_set:
            self.heap_set.add(ship_id)

            ship = self.data.game.me._ships.get(ship_id)
            matrix_highest_ratio, max_ratio, destination, harvest_value = self.get_matrix_ratio(ship)

            s = ExploreShip(max_ratio, ship.halite_amount, ship_id, destination, harvest_value, matrix_highest_ratio)
            heapq.heappush(self.heap_explore, s)


    def hasTooManyEnemy(self, ship):
        """
        IF HAS TOO MANY ENEMY
        """
        count = count_manhattan(self.data.myMatrix.locations.enemyShips, Matrix_val.ONE, ship.position,
                                MyConstants.deposit.enemy_check_manhattan)

        if count > MyConstants.deposit.enemy_check_num:
            return True
        else:
            return False







