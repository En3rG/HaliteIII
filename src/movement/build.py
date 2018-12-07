from src.common.print import print_heading, print_matrix
from src.common.moves import Moves
from hlt.positionals import Position
from hlt.positionals import Direction
from src.common.halite_statistics import BuildType
from src.common.values import MyConstants, Matrix_val
from src.common.matrix.functions import populate_manhattan, get_coord_closest
import numpy as np
import logging


"""
TO DO!!!!!111

BEST TO HAVE DOCKS CLOSE TO ENEMY AND GAIN ALOT OF INFLUENCE

DONT HARVEST WHERE DOCK WILL BE BUILT

DONT BUILD DOCK WHEN WE HAVE SMALL NUMBER OF SHIPS


"""

class Build(Moves):
    def __init__(self, data, prev_data):
        super().__init__(data, prev_data)

        self.move_ships()

    def move_ships(self):
        print_heading("Moving build (dock) ships......")

        self.building_now()
        self.building_later()


    def building_now(self):
        """
        MOVE SHIPS BUILDING NOW
        """
        r, c = np.where(self.data.init_data.myMatrix.locations.dock_placement == 2)

        ships_on_docks = set(self.data.myMatrix.locations.myShipsID[r, c])

        if len(ships_on_docks) >= 1 and self.data.myVars.canBuild and len(self.data.mySets.ships_all) > MyConstants.NUM_SHIPS_BEFORE_BUILDING:
            ships_building = ships_on_docks & self.data.mySets.ships_to_move

            for ship_id in ships_building:
                ship = self.data.game.me._ships.get(ship_id)
                self.mark_unsafe(ship.position)
                self.data.mySets.ships_to_move.remove(ship.id)

                self.data.myVars.isBuilding = True  ## SET TO TRUE, SO THAT IF WE DONT HAVE ENOUGH HALITE NOW, WILL NOT SPAWN SHIPS STILL

                ## TAKE INTO ACCOUNT SHIP.HALITE_AMOUNT, DOCK HALITE AMOUNT, PLUS CURRENT PLAYER HALITE AMOUNT
                if ship.halite_amount + self.data.game.me.halite_amount + self.data.myMatrix.halite.amount[ship.position.y][ship.position.x] > 4000:
                    self.data.game.me.halite_amount -= (4000 - ship.halite_amount - self.data.myMatrix.halite.amount[ship.position.y][ship.position.x])
                    self.data.halite_stats.record_spent(BuildType.DOCK)

                    self.data.command_queue.append(ship.make_dropoff())

                    ## CLEAR DOCK AREA, SO THAT OTHER SHIPS WILL NOT TRY TO BUILD ON IT
                    #self.data.init_data.myMatrix.locations.dock_placement[ship.position.y][ship.position.x] = 0
                    populate_manhattan(self.data.init_data.myMatrix.locations.dock_placement, Matrix_val.ZERO, ship.position, MyConstants.DOCK_MANHATTAN)
                else:
                    self.data.command_queue.append(ship.move(Direction.Still))


    def building_later(self):
        """
        MOVE SHIPS BUILDING LATER
        """
        matrixIDs = self.data.myMatrix.locations.myShipsID * self.data.init_data.myMatrix.locations.dock_placement

        r, c = np.where(matrixIDs != 0)

        ships_on_docks = set(self.data.myMatrix.locations.myShipsID[r, c])

        if len(ships_on_docks) >= 1 and self.data.myVars.canBuild and len(self.data.mySets.ships_all) > MyConstants.NUM_SHIPS_BEFORE_BUILDING:
            ships_building = ships_on_docks & self.data.mySets.ships_to_move

            for ship_id in ships_building:
                ship = self.data.game.me._ships.get(ship_id)

                self.data.myVars.isBuilding = True  ## SET TO TRUE, SO THAT IF WE DONT HAVE ENOUGH HALITE NOW, WILL NOT SPAWN SHIPS STILL

                ## GET DOCK POSITION
                curr_cell = (ship.position.y, ship.position.x)
                coord, distance, val = get_coord_closest(2, self.data.init_data.myMatrix.locations.dock_placement, self.data.init_data.myMatrix.distances[curr_cell])
                dock_position = Position(coord[1], coord[0])

                ## TAKE INTO ACCOUNT SHIP.HALITE_AMOUNT, DOCK HALITE AMOUNT, PLUS CURRENT PLAYER HALITE AMOUNT
                ## ALSO MAKE SURE ITS SAFE TO GO THERE
                if ship.halite_amount + self.data.game.me.halite_amount + self.data.myMatrix.halite.amount[dock_position.y][dock_position.x] > 4000 \
                        and self.data.myMatrix.locations.safe[dock_position.y][dock_position.x] != Matrix_val.UNSAFE:
                    direction = self.get_directions_target(ship, dock_position) ## RETURNS A LIST OF DIRECTIONS
                    self.move_mark_unsafe(ship, direction[0])
                else:
                    self.move_mark_unsafe(ship, Direction.Still)



