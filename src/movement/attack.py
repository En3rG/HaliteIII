from src.common.print import print_heading
from src.common.move.moves import Moves
from src.common.move.attacks import Attacks
from src.common.values import MyConstants, Matrix_val, MoveMode, Inequality
from hlt.positionals import Direction
from src.common.classes import OrderedSet
from src.common.move.harvests import Harvests
from src.common.move.explores import Explores
from src.common.points import SupportShip, SupportPoints, AttackPoints
from hlt import constants
import numpy as np
import logging
import copy
import heapq

"""
TO DO!!!!!!!!!!!!

BLOCK ENEMY DOCKS

ONLY ATTACK WHEN THERES SUPPORT
DONT ATTACK WHEN HAVE HIGH CARGO


TRY TO NOT INFLUENCE ENEMY IF POSSIBLE


"""


class Attack(Moves, Attacks, Harvests, Explores):
    def __init__(self, data, prev_data):
        Moves.__init__(self, data, prev_data)

        if self.data.game.turn_number <= constants.MAX_TURNS * MyConstants.EXPLORE_ENABLE_WITH_BONUS_TURNS_ABOVE:
            self.harvest_matrix = copy.deepcopy(self.data.myMatrix.halite.harvest)
        else:
            self.harvest_matrix = copy.deepcopy(self.data.myMatrix.halite.harvest_with_bonus)

        self.taken_matrix = np.zeros((self.data.game.game_map.height, self.data.game.game_map.width), dtype=np.int16)
        self.taken_matrix.fill(1)  ## ZERO WILL BE FOR TAKEN CELL
        r, c = np.where(self.data.myMatrix.locations.safe == Matrix_val.UNSAFE)
        self.taken_matrix[r, c] = Matrix_val.ZERO
        self.taken_destinations = set()

        self.heap_support = []
        self.considered_already = OrderedSet()
        self.move_ships()


    def move_ships(self):
        print_heading("Moving attack ships......")

        ## MOVE SHIPS CLOSEST TO ENEMY FIRST (WITH ITS SUPPORT SHIP)
        if self.data.myVars.allowAttack:
            for i in range(1, MyConstants.ENGAGE_ENEMY_DISTANCE):  ## DONT NEED TO MOVE FURTHEST ONES (WILL BE MOVED AS SUPPORT)
                matrixIDs = self.data.myMatrix.locations.engage_enemy[i] * self.data.myMatrix.locations.myShipsID
                r, c = np.where(matrixIDs > Matrix_val.ZERO)
                ships_engaging = OrderedSet(self.data.myMatrix.locations.myShipsID[r, c])
                ships_attacking = ships_engaging & self.data.mySets.ships_to_move
                self.considered_already.update(ships_attacking)

                self.heap_support = [] ## RESET PER ITERATION
                for ship_id in ships_attacking:
                    self.populate_heap(ship_id)

                while self.heap_support:
                    s = heapq.heappop(self.heap_support)
                    logging.debug(s)

                    first_ship = self.data.game.me._ships.get(s.ship_id)
                    direction, points = self.best_direction(first_ship, s.directions, mode=MoveMode.ATTACKING)

                    if direction != Direction.Still:
                    ## IF STAYING STILL, NO NEED TO MOVE
                    ## FIRST SHIP WILL JUST HARVEST/EXPLORE
                    ## SUPPORT SHIP MOVE WILL BE DETERMINED LATER
                        destination = self.get_destination(first_ship, direction)
                        self.mark_taken_udpate_top_halite(destination)
                        self.move_mark_unsafe(first_ship, direction, points)

                        logging.debug("Attacking ship id: {} support ships: {}".format(first_ship.id, s.support_ships))

                        for support_id in sorted(s.support_ships):                      ## ADD SORTED TO HAVE SAME ORDER ONLINE
                            if support_id in self.data.mySets.ships_to_move:            ## DONT MOVE SHIPS THAT ALREADY MOVED
                                support_ship = self.data.game.me._ships.get(support_id)
                                support_directions = self.get_directions_target(support_ship, first_ship.position)
                                direction, points = self.best_direction(support_ship, support_directions, mode=MoveMode.SUPPORTING)
                                destination = self.get_destination(support_ship, direction)
                                self.mark_taken_udpate_top_halite(destination)
                                self.move_mark_unsafe(support_ship, direction, points)


    def populate_heap(self, ship_id):
        """
        POPULATE HEAP, SHIP WITH LEAST SUPPORT WILL MOVE FIRST
        SO SHIPS WITH 2 SUPPORT WILL NOT TAKE A SUPPORT FOR ANOTHER

        WILL NOT BE ADDED TO HEAP IF IT HAS TOO MUCH HALITE CARGO
        """
        ship = self.data.game.me._ships.get(ship_id)
        neighbors = self.get_neighbor_IDs(ship)
        potential_support = neighbors - self.considered_already
        directions_to_enemy, enemy_position = self.get_enemy(ship)
        enemy_halite = self.data.myMatrix.locations.shipCargo[enemy_position.y][enemy_position.x]
        my_halite = ship.halite_amount

        canHarvest, harvest_direction = self.check_harvestNow(ship_id, moveNow=False)
        if not (canHarvest): canHarvest, harvest_direction = self.check_harvestLater(ship_id,
                                                                                     MyConstants.DIRECTIONS,
                                                                                     kicked=False,
                                                                                     moveNow=False)

        matrix_highest_ratio, max_ratio, explore_destination = self.get_matrix_ratio(ship)

        directions = self.get_directions_target(ship, explore_destination)
        explore_direction, points = self.best_direction(ship, directions, mode=MoveMode.EXPLORE)

        harvest_destination = self.get_destination(ship, harvest_direction)
        harvest_ratio = matrix_highest_ratio[harvest_destination.y][harvest_destination.x]

        if not(canHarvest) and max_ratio > harvest_ratio * MyConstants.HARVEST_RATIO_TO_EXPLORE:
            ## ATTACKING (NOT HARVESTING)
            support_ships = OrderedSet()
            for support_id in potential_support:
                support_ship = self.data.game.me._ships.get(support_id)

                canHarvest, harvest_direction = self.check_harvestNow(support_id, moveNow=False)
                if not (canHarvest): canHarvest, harvest_direction = self.check_harvestLater(support_id,
                                                                                             MyConstants.DIRECTIONS,
                                                                                             kicked=False,
                                                                                             moveNow=False)

                matrix_highest_ratio, max_ratio, explore_destination = self.get_matrix_ratio(support_ship)

                directions = self.get_directions_target(ship, explore_destination)
                explore_direction, points = self.best_direction(support_ship, directions, mode=MoveMode.EXPLORE)

                harvest_destination = self.get_destination(support_ship, harvest_direction)
                harvest_ratio = matrix_highest_ratio[harvest_destination.y][harvest_destination.x]

                if support_id in self.data.mySets.ships_to_move and not(canHarvest) and max_ratio > harvest_ratio * MyConstants.HARVEST_RATIO_TO_EXPLORE:
                    potental_harvest = (my_halite + enemy_halite) * 0.25  ## POTENTIAL HARVEST
                    real_gain = (support_ship.halite_amount + potental_harvest) % 1000  ## CAN ONLY GET MAX 1000
                    if real_gain > my_halite * self.data.myVars.support_gain_ratio:  ## MORE THAN 20% GAIN THAN WHAT WE LOST
                        support_ships.add(support_id)

            num_support = len(support_ships)

            # if my_halite < enemy_halite * MyConstants.ATTACK_ENEMY_HALITE_RATIO and num_support >= 1:
            if num_support >= 1:  ## ATTACK EVEN WHEN HAS HIGH CARGO
                s = SupportShip(num_support, ship.id, support_ships, directions_to_enemy)
                logging.debug(s)
                heapq.heappush(self.heap_support, s)

        ## ABOVE IS CONSIDERING HARVEST AND EXPLORE, BUT NOT REALLY DOING ANYTHING ABOUT EXPLORE
        # ship = self.data.game.me._ships.get(ship_id)
        # neighbors = self.get_neighbor_IDs(ship)
        # potential_support = neighbors - self.considered_already
        # directions_to_enemy, enemy_position = self.get_enemy(ship)
        # enemy_halite = self.data.myMatrix.locations.shipCargo[enemy_position.y][enemy_position.x]
        # my_halite = ship.halite_amount
        #
        # support_ships = OrderedSet()
        # for support_id in potential_support:
        #     if support_id in self.data.mySets.ships_to_move:
        #         support_ship = self.data.game.me._ships.get(support_id)
        #         potental_harvest = (my_halite + enemy_halite) * 0.25  ## POTENTIAL HARVEST
        #         real_gain = (support_ship.halite_amount + potental_harvest) % 1000  ## CAN ONLY GET MAX 1000
        #         if real_gain > my_halite * self.data.myVars.support_gain_ratio:  ## MORE THAN 20% GAIN THAN WHAT WE LOST
        #             support_ships.add(support_id)
        #
        # num_support = len(support_ships)
        #
        # # if my_halite < enemy_halite * MyConstants.ATTACK_ENEMY_HALITE_RATIO and num_support >= 1:
        # if num_support >= 1:  ## ATTACK EVEN WHEN HAS HIGH CARGO
        #     s = SupportShip(num_support, ship.id, support_ships, directions_to_enemy)
        #     logging.debug(s)
        #     heapq.heappush(self.heap_support, s)