from src.common.print import print_heading, print_matrix
from src.common.move.moves import Moves
from src.common.move.attacks import Attacks
from src.common.values import MyConstants, Matrix_val, MoveMode, Inequality
from hlt.positionals import Direction
from src.common.orderedSet import OrderedSet
from src.common.move.harvests import Harvests
from src.common.move.explores import Explores
from src.common.points import SupportShip, SupportPoints, AttackPoints, KamikazeShip
from src.common.matrix.functions import count_manhattan, get_manhattan, calculate_distance
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

        self.harvest_matrix = copy.deepcopy(self.data.myMatrix.halite.harvest_with_bonus)

        self.taken_matrix = np.zeros((self.data.game.game_map.height, self.data.game.game_map.width), dtype=np.int16)
        self.taken_matrix.fill(1)                                                                                       ## ZERO WILL BE FOR TAKEN CELL
        r, c = np.where(self.data.myMatrix.locations.safe == Matrix_val.UNSAFE)
        self.taken_matrix[r, c] = Matrix_val.ZERO
        self.taken_destinations = set()

        self.considered_already = OrderedSet()
        self.move_ships()


    def move_ships(self):
        print_heading("Moving attack ships......")

        allowAttack = (constants.MAX_TURNS * MyConstants.ATTACK_TURNS_LOWER_LIMIT <= self.data.game.turn_number <= constants.MAX_TURNS * MyConstants.ATTACK_TURNS_UPPER_LIMIT) \
                           and len(self.data.mySets.ships_all) > MyConstants.NUM_SHIPS_BEFORE_ATTACKING


        ## MOVE SHIPS CLOSEST TO ENEMY FIRST (WITH ITS SUPPORT SHIP)
        if allowAttack:
            considered_prev_i = OrderedSet()                                                                            ## USED TO NOT CONSIDER PREVIOUS i

            for i in range(1, MyConstants.ENGAGE_ENEMY_DISTANCE):                                                       ## DONT NEED TO MOVE FURTHEST ONES (WILL BE MOVED AS SUPPORT)
                matrixIDs = self.data.myMatrix.locations.engage_enemy[i] * self.data.myMatrix.locations.myShipsID
                r, c = np.where(matrixIDs > Matrix_val.ZERO)
                ships_engaging = OrderedSet(self.data.myMatrix.locations.myShipsID[r, c]) - considered_prev_i
                ships_attacking = ships_engaging & self.data.mySets.ships_to_move
                considered_prev_i.update(ships_attacking)
                self.considered_already.update(ships_attacking)

                self.heap_kamikaze = []
                self.heap_support = []                                                                                  ## RESET PER ITERATION

                for ship_id in ships_attacking:
                    self.populate_heap(ship_id, i)

                ## MOVE ATTACK/SUPPORT SHIPS
                self.move_attack_suppport()

                ## MOVE KAMIKAZE SHIPS
                self.move_kamikaze()


    def move_attack_suppport(self):
        while self.heap_support:
            s = heapq.heappop(self.heap_support)
            logging.debug(s)

            first_ship = self.data.game.me._ships.get(s.ship_id)
            direction = self.best_direction(first_ship, s.directions, mode=MoveMode.ATTACKING)

            if direction != Direction.Still:
                ## IF STAYING STILL, NO NEED TO MOVE
                ## FIRST SHIP WILL JUST HARVEST/EXPLORE
                ## SUPPORT SHIP MOVE WILL BE DETERMINED LATER
                destination = self.get_destination(first_ship, direction)
                self.mark_taken_udpate_top_halite(destination)
                self.move_mark_unsafe(first_ship, direction)

                logging.debug("Attacking ship id: {} support ships: {}".format(first_ship.id, s.support_ships))

                for support_id in s.support_ships:
                    if support_id in self.data.mySets.ships_to_move:
                        support_ship = self.data.game.me._ships.get(support_id)
                        support_directions = self.get_directions_target(support_ship, first_ship.position)
                        direction = self.best_direction(support_ship, support_directions, mode=MoveMode.SUPPORTING)
                        destination = self.get_destination(support_ship, direction)
                        self.mark_taken_udpate_top_halite(destination)
                        self.move_mark_unsafe(support_ship, direction)


    def move_kamikaze(self):
        while self.heap_kamikaze:
            s = heapq.heappop(self.heap_kamikaze)
            logging.debug(s)

            ship = self.data.game.me._ships.get(s.ship_id)

            if s.ship_id in self.data.mySets.ships_to_move:
                canHarvest, harvest_direction = self.check_harvestLater(s.ship_id, MyConstants.DIRECTIONS,
                                                                        kicked=False, moveNow=False, avoid_enemy=False,
                                                                        avoid_potential_enemy=False)
                harvest_destination = self.get_destination(ship, harvest_direction)
                if harvest_destination == s.explore_destination:
                    self.move_mark_unsafe(ship, harvest_direction)

                    for support_id in s.support_ships:
                        if support_id in self.data.mySets.ships_to_move:
                            support_ship = self.data.game.me._ships.get(support_id)
                            support_directions = self.get_directions_target(support_ship, ship.position)
                            direction = self.best_direction(support_ship, support_directions, mode=MoveMode.SUPPORTING)
                            destination = self.get_destination(support_ship, direction)
                            self.mark_taken_udpate_top_halite(destination)
                            self.move_mark_unsafe(support_ship, direction)


    def populate_heap(self, ship_id, i):
        """
        POPULATE HEAP, SHIP WITH LEAST SUPPORT WILL MOVE FIRST
        SO SHIPS WITH 2 SUPPORT WILL NOT TAKE A SUPPORT FOR ANOTHER

        WILL NOT BE ADDED TO HEAP IF IT HAS TOO MUCH HALITE CARGO
        """
        ship = self.data.game.me._ships.get(ship_id)
        directions_to_enemy, enemy_position = self.get_enemy_position(ship)
        ship_distance = calculate_distance(ship.position, enemy_position, self.data)
        enemy_ship, enemy_shipID = self.get_enemy_ship(enemy_position)
        potential_support = get_manhattan(self.data.myMatrix.locations.myShipsID,
                                          enemy_position, MyConstants.ENGAGE_ENEMY_DISTANCE)
        potential_support_IDs = potential_support - {-1} - self.considered_already                                      ## myShipsID contains -1
        num_enemy_ships = count_manhattan(self.data.myMatrix.locations.enemyShips, Matrix_val.ONE,
                                          enemy_position, MyConstants.ENEMY_BACKUP_DISTANCE)
        enemy_halite = self.data.myMatrix.locations.shipsCargo[enemy_position.y][enemy_position.x]
        my_halite = ship.halite_amount

        canHarvest, harvest_direction = self.check_harvestNow(ship_id, moveNow=False,
                                                              avoid_enemy=True, avoid_potential_enemy=True)
        if not (canHarvest): canHarvest, harvest_direction = self.check_harvestLater(ship_id,
                                                                                     MyConstants.DIRECTIONS,
                                                                                     kicked=False,
                                                                                     moveNow=False,
                                                                                     avoid_enemy=True,
																					 avoid_potential_enemy=True)

        matrix_highest_ratio, max_ratio, explore_destination, harvest_value = self.get_matrix_ratio(ship)

        # directions = self.get_directions_target(ship, explore_destination)
        # explore_direction, points = self.best_direction(ship, directions, mode=MoveMode.EXPLORE, avoid_enemy=False)

        harvest_destination = self.get_destination(ship, harvest_direction)
        harvest_ratio = matrix_highest_ratio[harvest_destination.y][harvest_destination.x]

        if max_ratio > harvest_ratio * MyConstants.HARVEST_RATIO_TO_EXPLORE \
                and len(potential_support_IDs) > num_enemy_ships \
                and (len(self.data.game.players) == 2):
        #if max_ratio > harvest_ratio * MyConstants.HARVEST_RATIO_TO_EXPLORE and len(potential_support_IDs) > num_enemy_ships and my_halite <= 500:
            ## ATTACKING (NOT HARVESTING)
            support_ships = OrderedSet()
            for support_id in sorted(potential_support_IDs):
                support_ship = self.data.game.me._ships.get(support_id)
                support_distance = calculate_distance(support_ship.position, enemy_position, self.data)

                canHarvest, harvest_direction = self.check_harvestNow(support_id, moveNow=False,
                                                                      avoid_enemy=True, avoid_potential_enemy=True)
                if not (canHarvest): canHarvest, harvest_direction = self.check_harvestLater(support_id,
                                                                                             MyConstants.DIRECTIONS,
                                                                                             kicked=False,
                                                                                             moveNow=False,
                                                                                             avoid_enemy=True,
																							 avoid_potential_enemy=True)

                matrix_highest_ratio, max_ratio, explore_destination, harvest_value = self.get_matrix_ratio(support_ship)

                # directions = self.get_directions_target(ship, explore_destination)
                # explore_direction, points = self.best_direction(support_ship, directions, mode=MoveMode.EXPLORE, avoid_enemy=False)

                harvest_destination = self.get_destination(support_ship, harvest_direction)
                harvest_ratio = matrix_highest_ratio[harvest_destination.y][harvest_destination.x]

                if support_id in self.data.mySets.ships_to_move \
                        and max_ratio > harvest_ratio * MyConstants.HARVEST_RATIO_TO_EXPLORE \
                        and support_distance <= ship_distance + 1:                                                      ## HAVE TO BE JUST 1 DISTANCE AWAY OR CLOSER
                    potental_harvest = (my_halite + enemy_halite) * 0.25                                                ## POTENTIAL HARVEST
                    real_gain = (support_ship.halite_amount + potental_harvest) % 1000                                  ## CAN ONLY GET MAX 1000
                    if real_gain > my_halite * self.data.myVars.support_gain_ratio:                                     ## MORE THAN 20% GAIN THAN WHAT WE LOST
                        support_ships.add(support_id)

            num_support = len(support_ships)

            # if my_halite < enemy_halite * MyConstants.ATTACK_ENEMY_HALITE_RATIO and num_support >= 1:
            if num_support >= 1:                                                                                        ## ATTACK EVEN WHEN HAS HIGH CARGO
                s = SupportShip(num_support, ship.id, support_ships, directions_to_enemy)
                heapq.heappush(self.heap_support, s)

        elif i == 2:
            support_ships = OrderedSet()
            for support_id in sorted(potential_support_IDs):
                if support_id in self.data.mySets.ships_to_move:
                    support_ships.add(support_id)

            s = KamikazeShip(ship.halite_amount, ship.id, support_ships, explore_destination)
            heapq.heappush(self.heap_kamikaze, s)





