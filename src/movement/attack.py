from src.common.print import print_heading
from src.common.move.moves import Moves
from src.common.move.attacks import Attacks
from src.common.values import MyConstants, Matrix_val, MoveMode, Inequality
from hlt.positionals import Direction
from src.common.classes import OrderedSet
from src.common.move.harvests import Harvests
import numpy as np
import logging
import heapq

"""
TO DO!!!!!!!!!!!!

BLOCK ENEMY DOCKS

ONLY ATTACK WHEN THERES SUPPORT
DONT ATTACK WHEN HAVE HIGH CARGO


TRY TO NOT INFLUENCE ENEMY IF POSSIBLE


"""


class Attack(Moves, Attacks, Harvests):
    def __init__(self, data, prev_data):
        Moves.__init__(self, data, prev_data)

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
                        self.move_mark_unsafe(first_ship, direction, points)

                        logging.debug("Attacking ship id: {} support ships: {}".format(first_ship.id, s.support_ships))

                        for support_id in sorted(s.support_ships):                      ## ADD SORTED TO HAVE SAME ORDER ONLINE
                            if support_id in self.data.mySets.ships_to_move:            ## DONT MOVE SHIPS THAT ALREADY MOVED
                                support_ship = self.data.game.me._ships.get(support_id)
                                support_directions = self.get_directions_target(support_ship, first_ship.position)
                                direction, points = self.best_direction(support_ship, support_directions, mode=MoveMode.SUPPORTING)
                                self.move_mark_unsafe(support_ship, direction, points)


