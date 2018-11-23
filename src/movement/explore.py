from src.common.moves import Moves
from src.common.values import MoveMode, MyConstants
import logging
from src.common.print import print_heading, print_matrix
from src.common.matrix import get_position_highest_section
from hlt.positionals import Direction
from src.common.points import ExplorePoints

class Explore(Moves):
    def __init__(self, data, prev_data):
        super().__init__(data, prev_data)

        self.move_ships()

    def move_ships(self):
        print_heading("Moving exploring ships......")

        ## MOVE REST OF THE SHIPS
        ships = (self.data.all_ships & self.data.ships_to_move)  ## SAVING SINCE ships_to_move WILL BE UPDATED DURING ITERATION
        for ship_id in ships:
            ## MOVE KICKED SHIPS FIRST (IF ANY)
            while self.data.ships_kicked:
                logging.debug("ships kicked: {}".format(self.data.ships_kicked))
                ship_kicked = self.data.ships_kicked.pop()
                logging.debug("Moving kicked ship ({}) for explore".format(ship_kicked))
                self.exploreNow(ship_kicked)

            ## DOUBLE CHECK SHIP IS STILL IN SHIPS TO MOVE
            if ship_id in self.data.ships_to_move:
                self.exploreNow(ship_id)


    def exploreNow(self, ship_id):
        """
        SHIP IS EXPLORING, PERFORM NECESSARY STEPS
        """
        ship = self.data.me._ships.get(ship_id)

        #direction = self.get_highest_harvest_move(ship)
        destination = get_position_highest_section(self.data)
        directions = self.get_directions_target(ship, destination)
        direction = self.best_direction(ship, directions, mode=MoveMode.EXPLORE)
        self.move_mark_unsafe(ship, direction)


    def get_points_explore(self, ship, directions):
        """
        GET POINTS FOR EXPLORING

        :param ship:
        :param directions: DIRECTIONS TO CONSIDER
        :return:
        """
        points = []


        for direction in directions:
            destination = self.get_destination(ship, direction)

            safe = self.data.matrix.safe[destination.y][destination.x]
            occupied = self.data.matrix.occupied[destination.y][destination.x]
            cost = self.data.matrix.cost[destination.y][destination.x]
            potential_enemy_collision = self.data.matrix.potential_enemy_collisions[destination.y][destination.x]

            c = ExplorePoints(safe, occupied, potential_enemy_collision, cost, direction)
            points.append(c)

        safe = self.data.matrix.safe[ship.position.y][ship.position.x]
        occupied = 0 if self.data.matrix.occupied[ship.position.y][ship.position.x] >= -1 else -1
        potential_enemy_collision = self.data.matrix.potential_enemy_collisions[ship.position.y][ship.position.x]

        points.append(ExplorePoints(safe=safe,
                                    occupied=occupied,
                                    potential_enemy_collision=potential_enemy_collision,
                                    cost=999,
                                    direction=Direction.Still))

        logging.debug(points)

        return points