import logging
import heapq
from src.common.move.moves import Moves
from src.common.move.deposits import Deposits
from src.common.move.explores import Explores
from src.common.print import print_heading
from src.movement.collision_prevention import avoid_collision_direction
from src.common.points import FarthestShip, DepositPoints, ExploreShip
from src.common.values import MoveMode, Matrix_val, Inequality, MyConstants
from hlt.positionals import Direction
from src.common.matrix.functions import get_coord_closest
from hlt.positionals import Position
from hlt import constants
import copy
import numpy as np

"""
TO DO!!!!


	            % Harvested 	Efficiency %	 Halite total 	 Enemy 	        percent diff
800_50_no b	    54.62	        42.97	        $119,819.00 	 $63,210.00 	0.527545715
850_50_no b	    58.24	        39.12	        $104,089.00 	 $94,267.00 	0.905638444
900_50_no b	    62	            44.26	        $142,144.00 	 $77,135.00 	0.542653928
950_50_no b	    54.14	        41.83	        $104,256.00 	 $77,246.00 	0.740926182
800_50_b	    57.56	        31.97	        $46,050.00 	     $145,567.00 	3.161064061
850_50_ b	    62.52	        39.32	        $60,909.00 	     $148,069.00 	2.43098721
900_50_b	    53.09	        34.72	        $65,407.00 	     $108,101.00 	1.65274359
950_50_b	    55.2	        42.2	        $107,339.00 	 $75,836.00 	0.706509284
800_75_no b	    57.93	        44.94	        $138,743.00 	 $64,108.00 	0.462062951  <---- best
850_75_no b	    59.07	        44.27	        $134,259.00 	 $79,589.00 	0.592801972
900_75_no b	    58.83	        41.49	        $116,982.00 	 $77,285.00 	0.660657195
950_75_no b	    66.68	        39.13	        $110,550.00 	 $112,112.00 	1.014129353
800_75_b	    62.07	        35.2	        $85,294.00 	     $103,616.00 	1.214809951
850_75_ b	    62.88	        40.88	        $118,263.00 	 $101,298.00 	0.85654854
900_75_b	    56.49	        42.58	        $125,337.00 	 $62,893.00 	0.501791171
950_75_b	    66.81	        38.99	        $109,912.00 	 $118,457.00 	1.077744013



"""

class Deposit(Moves, Deposits, Explores):
    def __init__(self, data, prev_data):
        Moves.__init__(self, data, prev_data)
        self.heap_dist = []
        self.heap_explore = []
        self.heap_set_dist = set()   ## USED TO NOT HAVE DUPLICATE SHIP IDs IN THE HEAP DIST
        self.heap_set = set()

        self.taken_destinations = set()
        if self.data.game.turn_number <= constants.MAX_TURNS * MyConstants.EXPLORE_ENABLE_WITH_BONUS_TURNS_ABOVE:
            self.harvest_matrix = copy.deepcopy(self.data.myMatrix.halite.harvest)
        else:
            self.harvest_matrix = copy.deepcopy(self.data.myMatrix.halite.harvest_with_bonus)  ## WORST THAN JUST DOING HARVEST

        self.taken_matrix = np.zeros((self.data.game.game_map.height, self.data.game.game_map.width), dtype=np.int16)
        self.taken_matrix.fill(1)  ## ZERO WILL BE FOR TAKEN CELL
        r, c = np.where(self.data.myMatrix.locations.safe == Matrix_val.UNSAFE)
        self.taken_matrix[r, c] = Matrix_val.ZERO

        self.move_ships()


    def move_ships(self):
        print_heading("Moving depositing ships......")

        ## MOVE SHIPS THAT ARE FULL OR HAVE ENOUGH CARGO
        self.check_depositing_now()

        ## MOVE SHIPS DEPOSITING PREVIOUSLY
        self.check_depositing_before()

        ## MOVE SHIPS, BASED ON HEAP
        while self.heap_dist:
            ## MOVE KICKED SHIPS FIRST (MAYBE BY BUILDING)
            while self.data.mySets.ships_kicked:
                ship_kicked = self.data.mySets.ships_kicked.pop()
                logging.debug("Moving kicked ship ({}) by a depositing ship".format(ship_kicked))
                ship = self.data.game.me._ships.get(ship_kicked)
                direction = avoid_collision_direction(self, ship, directions=None)
                self.move_mark_unsafe(ship, direction)

            s = heapq.heappop(self.heap_dist)
            if s.ship_id in self.data.mySets.ships_to_move:    ## MEANS IT HAS MOVED BEFORE (MAYBE KICKED)
                ship = self.data.game.me._ships.get(s.ship_id)
                self.depositNow(ship, s.dock_position, s.directions)


    def check_depositing_now(self):
        """
        POPULATE HEAP DIST AND HEAP FOR EXPLORE PURPOSES
        """
        for ship_id in (self.data.mySets.ships_all & self.data.mySets.ships_to_move):
            ship = self.data.game.me._ships.get(ship_id)

            if ship.is_full:                                                                                            ## SHIPS JUST HIT MAX
                self.populate_heap_dist(ship)
            elif ship.halite_amount >= MyConstants.POTENTIALLY_ENOUGH_CARGO:                                            ## MIGHT BE ENOUGH
                self.populate_heap(ship_id)

        ## CHECK EACH SHIP IN HEAP EXPLORE, IF DEPOSITING NOW
        self.verify_depositing_now()


    def check_depositing_before(self):
        """
        POPULATE HEAP REGARDING SHIPS DEPOSITING BEFORE
        """
        if self.prev_data:
            for ship_id in (self.prev_data.ships_returning & self.data.mySets.ships_to_move):
                ship = self.data.game.me._ships.get(ship_id)

                if ship and (
                ship.position.y, ship.position.x) not in self.data.mySets.dock_coords:  ## SHIP ALREADY IN DOCK
                    self.populate_heap_dist(ship)


    def verify_depositing_now(self):
        """
        CHECK IF SHIPS IN HEAP EXPLORE IS ENOUGH TO GO HOME
        """
        while self.heap_explore:
            s = heapq.heappop(self.heap_explore)

            ship = self.data.game.me._ships.get(s.ship_id)
            explore_destination = self.isDestination_untaken(s)

            if explore_destination:
                current_harvest = self.data.myMatrix.halite.harvest_with_bonus[ship.position.y][ship.position.x]
                target_harvest = self.data.myMatrix.halite.harvest[explore_destination.y][explore_destination.x]

                if ship.halite_amount + (current_harvest * MyConstants.DEPOSIT_HARVEST_CHECK_PERCENT) >= 1000:
                    self.mark_taken_udpate_top_halite(ship.position)
                    self.populate_heap_dist(ship)

                elif ship.halite_amount + (target_harvest * MyConstants.DEPOSIT_HARVEST_CHECK_PERCENT) >= 1000:
                    self.mark_taken_udpate_top_halite(explore_destination)
                    self.populate_heap_dist(ship)



    def populate_heap_dist(self, ship):
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


    def populate_heap(self, ship_id):
        if ship_id not in self.heap_set:
            self.heap_set.add(ship_id)

            ship = self.data.game.me._ships.get(ship_id)
            matrix_highest_ratio, max_ratio, destination = self.get_matrix_ratio(ship)
            s = ExploreShip(max_ratio, ship.halite_amount, ship_id, destination, matrix_highest_ratio)
            heapq.heappush(self.heap_explore, s)