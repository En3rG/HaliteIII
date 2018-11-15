from hlt.positionals import Direction, Position
from src.common.points import FarthestShip
from src.common.values import MyConstants, Matrix_val, DirectionHomeMode
from src.common.matrix import Section, print_matrix, get_index_highest_val
import logging
from src.common.movement import Moves
import heapq


class MoveShips(Moves):
    def __init__(self, data, prev_data, halite_stats, command_queue):
        super().__init__(data, prev_data, halite_stats)

        self.command_queue = command_queue
        self.heap_dist = []

        self.get_moves()

    def get_moves(self):
        ## MOVE SHIPS THAT CANNOT MOVE YET
        for ship_id in (self.data.all_ships & self.data.ships_to_move):
            ship = self.data.me._ships.get(ship_id)

            if self.data.matrix.cost[ship.position.y][ship.position.x] > ship.halite_amount:  ## NOT ENOUGH TO LEAVE
                logging.debug("Ship id: {} has not enough halite to move".format(ship.id))
                direction = Direction.Still

                harvesting = self.isHarvesting(direction, ship.id)
                self.move_mark_unsafe(ship, direction)


        ## SHIPS JUST HIT MAX
        for ship_id in (self.data.all_ships & self.data.ships_to_move):
            ship = self.data.me._ships.get(ship_id)

            if ship.is_full:
                self.populate_heap(ship)


        ## SHIPS RETURNING PREVIOUSLY (HIT MAX)
        if self.prev_data:
            for ship_id in (self.prev_data.ships_returning & self.data.ships_to_move):
                ship = self.data.me._ships.get(ship_id)

                if ship and ship.position != self.data.me.shipyard.position:
                    self.populate_heap(ship)


        ## MOVE SHIPS RETURNING (JUST HIT MAX AND PREVIOUSLY RETURNING)
        while self.heap_dist:
            s = heapq.heappop(self.heap_dist)
            ship = self.data.me._ships.get(s.ship_id)
            self.returning(ship, s.directions)


        ## MOVE REST OF THE SHIPS (THAT WILL HARVEST)
        for ship_id in (self.data.all_ships & self.data.ships_to_move):
            ship = self.data.me._ships.get(ship_id)

            direction = self.get_highest_harvest_move(ship)
            if self.isHarvesting(direction, ship.id):
                self.move_mark_unsafe(ship, direction)


        ## MOVE REST OF THE SHIPS
        for ship_id in (self.data.all_ships & self.data.ships_to_move):
            ship = self.data.me._ships.get(ship_id)

            direction = self.get_highest_harvest_move(ship)
            self.move_mark_unsafe(ship, direction)


    def populate_heap(self, ship):
        """
        GET DISTANCE FROM SHIPYARD

        NEED TO ADD GETTING CLOSEST DOCK LATER!!!!!!!!!!!11

        :return:
        """
        distance = self.data.game_map.calculate_distance(ship.position, self.data.me.shipyard.position)
        directions = self.directions_home(ship, self.data.me.shipyard.position)
        num_directions = len(directions)
        s = FarthestShip(distance, num_directions, ship.id, directions)
        heapq.heappush(self.heap_dist, s)


    def isHarvesting(self, direction, ship_id):
        if direction == Direction.Still:
            self.data.ships_harvesting.add(ship_id)
            logging.debug("Ship id: {} is harvesting".format(ship_id))
            return True

        return False


    def returning(self, ship, directions):
        logging.debug("Ship id: {} is returning".format(ship.id))
        direction = self.best_direction_home(ship, directions, mode=DirectionHomeMode.DEPOSIT)
        self.move_mark_unsafe(ship, direction)
        self.data.ships_returning.add(ship.id)


    def get_highest_harvest_move(self, ship):
        """
        ACTUAL HARVEST MATRIX IS THE NEIGHBORING HARVEST VALUE MINUS LEAVING CURRENT CELL

        :param ship:
        :param harvest:
        :param cost:
        :return:
        """
        logging.debug("Getting highest harvest move for ship id: {}".format(ship.id))
        harvest = Section(self.data.matrix.harvest, ship.position, size=1)          ## SECTION OF HARVEST MATRIX
        leave_cost = self.data.matrix.cost[ship.position.y][ship.position.x]        ## COST TO LEAVE CURRENT CELL
        cost_matrix = MyConstants.DIRECT_NEIGHBORS * leave_cost                     ## APPLY COST TO DIRECT NEIGHBORS
        harvest_matrix = harvest.matrix * MyConstants.DIRECT_NEIGHBORS_SELF
        actual_harvest = harvest_matrix - cost_matrix
        unsafe = Section(self.data.matrix.unsafe, ship.position, size=1)
        safe_harvest = actual_harvest * unsafe.matrix

        max_index = get_index_highest_val(safe_harvest)

        if max_index == (0,1):
            return Direction.North

        elif max_index == (1, 2):
            return Direction.East

        elif max_index == (2, 1):
            return Direction.South

        elif max_index == (1, 0):
            return Direction.West
        else:
            return Direction.Still



