from src.common.movement import Moves
from src.common.values import MoveMode, MyConstants
import logging
from src.common.print import print_heading
from hlt.positionals import Direction

class Explore(Moves):
    def __init__(self, data, prev_data):
        super().__init__(data, prev_data)

        self.move_ships()

    def move_ships(self):
        print_heading("Moving exploring ships......")

        ## MOVE REST OF THE SHIPS
        for ship_id in (self.data.all_ships & self.data.ships_to_move):
            ship = self.data.me._ships.get(ship_id)

            #direction = self.get_highest_harvest_move(ship)
            direction = self.best_direction(ship, mode=MoveMode.EXPLORE)
            self.move_mark_unsafe(ship, direction)


    def get_points_explore(self, ship):
        """
        GET POINTS FOR EXPLORING

        :param ship:
        :param directions: DIRECTIONS TO CONSIDER
        :return:
        """
        points = []
        leave_cost, harvest_stay = self.get_harvest(ship, Direction.Still)

        for direction in MyConstants.DIRECTIONS:
            cost, harvest = self.get_harvest(ship, direction, leave_cost, harvest_stay)
            self.get_points(ship, direction, harvest, points)

        logging.debug("Ship id: {} harvest points: {}".format(ship.id, points))

        return points