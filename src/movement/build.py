from src.common.print import print_heading
from src.common.moves import Moves
from hlt.positionals import Direction
import numpy as np
import logging

class Build(Moves):
    def __init__(self, data, prev_data):
        super().__init__(data, prev_data)

        self.move_ships()

    def move_ships(self):
        print_heading("Moving build (dock) ships......")

        matrix = self.data.matrix.myShipsID * self.data.init_data.matrix.dock_placement

        r, c = np.where(matrix != 0)

        ships = self.data.matrix.myShipsID[r, c]
        halite_amount = self.data.me.halite_amount

        if len(ships) >= 1:
            for ship_id in ships:
                ship = self.data.me._ships.get(ship_id)
                self.mark_unsafe(ship.position)
                self.data.ships_to_move.remove(ship.id)

                if halite_amount > 4000:
                    halite_amount -= 4000
                    self.data.command_queue.append(ship.make_dropoff())

                    self.data.init_data.matrix.dock_placement[ship.position.y][ship.position.x] = 0
                else:
                    self.data.command_queue.append(ship.move(Direction.Still))


