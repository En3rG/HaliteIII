import logging
from hlt.positionals import Direction
from src.common.movement import Moves


class Stuck(Moves):
    def __init__(self, data, prev_data, command_queue, halite_stats,):
        super().__init__(data, prev_data, halite_stats)
        self.command_queue = command_queue

        self.get_moves()

    def get_moves(self):
        ## MOVE SHIPS THAT CANNOT MOVE YET
        for ship_id in (self.data.all_ships & self.data.ships_to_move):
            ship = self.data.me._ships.get(ship_id)

            if self.data.matrix.cost[ship.position.y][ship.position.x] > ship.halite_amount:  ## NOT ENOUGH TO LEAVE
                logging.debug("Ship id: {} has not enough halite to move".format(ship.id))
                direction = Direction.Still

                self.move_mark_unsafe(ship, direction)