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

        matrix = self.data.matrix.locations.myShipsID * self.data.init_data.matrix.locations.dock_placement

        r, c = np.where(matrix != 0)

        ships_on_docks = set(self.data.matrix.locations.myShipsID[r, c])
        halite_amount = self.data.game.me.halite_amount

        if len(ships_on_docks) >= 1:
            ships_building = ships_on_docks & self.data.mySets.ships_to_move

            for ship_id in ships_building:
                ship = self.data.game.me._ships.get(ship_id)
                self.mark_unsafe(ship.position)
                self.data.mySets.ships_to_move.remove(ship.id)

                self.data.isBuilding = True

                if halite_amount > 4000:
                    halite_amount -= 4000

                    self.data.command_queue.append(ship.make_dropoff())

                    self.data.init_data.matrix.locations.dock_placement[ship.position.y][ship.position.x] = 0
                else:
                    self.data.command_queue.append(ship.move(Direction.Still))


