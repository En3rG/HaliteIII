from src.common.print import print_heading
from src.common.moves import Moves
from hlt.positionals import Direction
from src.common.halite_statistics import BuildType
import numpy as np
import logging

class Build(Moves):
    def __init__(self, data, prev_data):
        super().__init__(data, prev_data)

        self.move_ships()

    def move_ships(self):
        print_heading("Moving build (dock) ships......")

        matrixIDs = self.data.matrix.locations.myShipsID * self.data.init_data.matrix.locations.dock_placement

        r, c = np.where(matrixIDs != 0)

        ships_on_docks = set(self.data.matrix.locations.myShipsID[r, c])
        myHalite_amnt = self.data.game.me.halite_amount

        if len(ships_on_docks) >= 1 and self.data.canBuild:
            ships_building = ships_on_docks & self.data.mySets.ships_to_move

            for ship_id in ships_building:
                ship = self.data.game.me._ships.get(ship_id)
                self.mark_unsafe(ship.position)
                self.data.mySets.ships_to_move.remove(ship.id)

                self.data.isBuilding = True ## SET TO TRUE, SO THAT IF WE DONT HAVE ENOUGH HALITE NOW, WILL NOT SPAWN SHIPS STILL

                if myHalite_amnt > 4000:
                    myHalite_amnt -= 4000

                    logging.debug("Ship id: {} building dock".format(ship.id))
                    self.data.halite_stats.record_spent(BuildType.DOCK)

                    self.data.command_queue.append(ship.make_dropoff())

                    self.data.init_data.matrix.locations.dock_placement[ship.position.y][ship.position.x] = 0
                else:
                    self.data.command_queue.append(ship.move(Direction.Still))


