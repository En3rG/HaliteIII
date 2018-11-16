from hlt.positionals import Direction, Position
import logging
from src.common.movement import Moves


class Harvest(Moves):
    def __init__(self, data, prev_data, command_queue, halite_stats,):
        super().__init__(data, prev_data, halite_stats)

        self.command_queue = command_queue

        self.get_moves()

    def get_moves(self):
        ## MOVE REST OF THE SHIPS (THAT WILL HARVEST)
        for ship_id in (self.data.all_ships & self.data.ships_to_move):
            ship = self.data.me._ships.get(ship_id)

            direction = self.get_highest_harvest_move(ship)
            if self.isHarvesting(direction, ship.id):
                self.move_mark_unsafe(ship, direction)


    def isHarvesting(self, direction, ship_id):
        if direction == Direction.Still:
            self.data.ships_harvesting.add(ship_id)
            logging.debug("Ship id: {} is harvesting".format(ship_id))
            return True

        return False







