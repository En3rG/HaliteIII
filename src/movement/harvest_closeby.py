from hlt.positionals import Direction, Position
import logging
from src.common.movement import Moves
from src.common.values import MyConstants, MoveMode
from src.common.print import print_heading

class Harvest(Moves):
    def __init__(self, data, prev_data, command_queue, halite_stats):
        super().__init__(data, prev_data, halite_stats)
        self.command_queue = command_queue

        self.move_ships()

    def move_ships(self):
        print_heading("Moving harvesting ships......")

        ## MOVE REST OF THE SHIPS (THAT WILL HARVEST)
        for ship_id in (self.data.all_ships & self.data.ships_to_move):
            ship = self.data.me._ships.get(ship_id)

            #direction = self.get_highest_harvest_move(ship)
            direction = self.best_direction(ship, mode=MoveMode.HARVEST)
            if self.moveNow(direction, ship):
                self.move_mark_unsafe(ship, direction)


    def moveNow(self, direction, ship):
        """
        WILL ONLY LET IT HARVEST IF HARVEST AMOUNT IS > DONT_HARVEST_BELOW OR IS BLOCKED (SURROUNDED)

        :param direction:
        :param ship:
        :return:
        """
        if direction == Direction.Still and \
                (self.data.matrix.harvest[ship.position.y][ship.position.x] > MyConstants.DONT_HARVEST_BELOW or self.isBlocked(ship)):
            self.data.ships_harvesting.add(ship.id)
            logging.debug("Ship id: {} is harvesting".format(ship.id))
            return True
        elif self.isGoodHarvest(ship, direction):
            return True

        return False


    def get_points_harvest(self, ship):
        """
        GET POINTS FOR HARVESTING

        :param ship:
        :param directions: DIRECTIONS TO CONSIDER
        :return:
        """
        points = []
        leave_cost, harvest_stay = self.get_harvest(ship, Direction.Still)
        self.get_points(ship, Direction.Still, harvest_stay, points)

        for direction in MyConstants.DIRECTIONS:
            cost, harvest = self.get_harvest(ship, direction, leave_cost, harvest_stay)
            self.get_points(ship, direction, harvest, points)

        logging.debug("Ship id: {} harvest points: {}".format(ship.id, points))

        return points


    def isBlocked(self, ship):
        """
        IF ALL 4 DIRECTIONS ARE NOT SAFE

        :return:
        """
        unsafe_num = 0
        for direction in MyConstants.DIRECTIONS:
            destination = self.get_destination(ship, direction)
            if self.data.matrix.safe[destination.y][destination.x] == -1: unsafe_num += 1

        return unsafe_num == 4


    def isGoodHarvest(self, ship, direction):
        destination = self.get_destination(ship, direction)
        return self.data.matrix.harvest[destination.y][destination.x] > MyConstants.DONT_HARVEST_BELOW









