from src.common.print import print_heading, print_matrix
from src.common.moves import Moves
from hlt.positionals import Position
from hlt.positionals import Direction
from src.common.halite_statistics import BuildType
from src.common.values import MyConstants, Matrix_val, MoveMode
from src.common.matrix.functions import populate_manhattan, get_coord_closest
from src.common.points import BuildPoints
import numpy as np
import logging


"""
TO DO!!!!!111

BEST TO HAVE DOCKS CLOSE TO ENEMY AND GAIN ALOT OF INFLUENCE

DONT BUILD DOCK WHEN AREA HAS BEEN HARVESTED



"""

class Build(Moves):
    def __init__(self, data, prev_data):
        super().__init__(data, prev_data)

        self.dock_value = MyConstants.DOCK_MANHATTAN + 1
        self.move_ships()

    def move_ships(self):
        print_heading("Moving build (dock) ships......")

        if self.data.myVars.canBuild and len(self.data.mySets.ships_all) > MyConstants.NUM_SHIPS_BEFORE_BUILDING:
            self.building_now()
            self.building_later()


    def building_now(self):
        """
        MOVE SHIPS BUILDING NOW (AT DOCK POSITION)
        """
        r, c = np.where(self.data.init_data.myMatrix.locations.dock_placement == self.dock_value)
        ships_on_docks = set(self.data.myMatrix.locations.myShipsID[r, c])

        if len(ships_on_docks) >= 1:
            ships_building = ships_on_docks & self.data.mySets.ships_to_move

            for ship_id in ships_building:
                ship = self.data.game.me._ships.get(ship_id)
                self.mark_unsafe(ship, ship.position)
                self.data.mySets.ships_to_move.remove(ship.id)

                self.data.myVars.isBuilding = True  ## SET TO TRUE, SO THAT IF WE DONT HAVE ENOUGH HALITE NOW, WILL NOT SPAWN SHIPS STILL

                ## TAKE INTO ACCOUNT SHIP.HALITE_AMOUNT, DOCK HALITE AMOUNT, PLUS CURRENT PLAYER HALITE AMOUNT
                if ship.halite_amount + self.data.game.me.halite_amount + self.data.myMatrix.halite.amount[ship.position.y][ship.position.x] > 4000:
                    self.data.game.me.halite_amount -= (4000 - ship.halite_amount - self.data.myMatrix.halite.amount[ship.position.y][ship.position.x])

                    logging.debug("Shid id: {} building dock at position: {}".format(ship.id, ship.position))
                    self.data.halite_stats.record_spent(BuildType.DOCK)
                    self.data.command_queue.append(ship.make_dropoff())

                    ## CLEAR DOCK AREA, SO THAT OTHER SHIPS WILL NOT TRY TO BUILD ON IT
                    #self.data.init_data.myMatrix.locations.dock_placement[ship.position.y][ship.position.x] = 0
                    populate_manhattan(self.data.init_data.myMatrix.locations.dock_placement,
                                       Matrix_val.ZERO,
                                       ship.position,
                                       MyConstants.DOCK_MANHATTAN)
                else:
                    ## NOT ENOUGH HALITE YET, STAY STILL
                    self.data.command_queue.append(ship.move(Direction.Still))


    def building_later(self):
        """
        MOVE SHIPS BUILDING LATER
        """
        for i in range(MyConstants.DOCK_MANHATTAN, 0, -1): ## MOVES SHIPS CLOSEST TO DOCK FIRST
            r, c = np.where(self.data.init_data.myMatrix.locations.dock_placement == i)
            matrixIDs = set(self.data.myMatrix.locations.myShipsID[r, c])
            ships_going_dock = matrixIDs & self.data.mySets.ships_to_move

            if len(ships_going_dock) >= 1:
                for ship_id in ships_going_dock:
                    ship = self.data.game.me._ships.get(ship_id)

                    self.data.myVars.isBuilding = True  ## SET TO TRUE, SO THAT IF WE DONT HAVE ENOUGH HALITE NOW, WILL NOT SPAWN SHIPS STILL

                    ## GET DOCK POSITION
                    curr_cell = (ship.position.y, ship.position.x)
                    coord, distance, val = get_coord_closest(self.dock_value,
                                                             self.data.init_data.myMatrix.locations.dock_placement,
                                                             self.data.init_data.myMatrix.distances[curr_cell])
                    dock_position = Position(coord[1], coord[0])
                    directions = self.get_directions_target(ship, dock_position)

                    if i ==  MyConstants.DOCK_MANHATTAN: ## CURRENTLY RIGHT NEXT TO THE DOCK
                        ## TAKE INTO ACCOUNT SHIP.HALITE_AMOUNT, DOCK HALITE AMOUNT, PLUS CURRENT PLAYER HALITE AMOUNT
                        ## ALSO MAKE SURE ITS SAFE TO GO THERE
                        if ship.halite_amount + self.data.game.me.halite_amount + self.data.myMatrix.halite.amount[dock_position.y][dock_position.x] > 4000 \
                                and self.data.myMatrix.locations.safe[dock_position.y][dock_position.x] != Matrix_val.UNSAFE:
                            self.move_mark_unsafe(ship, directions[0]) ## DIRECTION IS A LIST OF DIRECTIONS
                        else:
                            self.move_mark_unsafe(ship, Direction.Still)
                    else:
                        direction = self.best_direction(ship, directions, mode=MoveMode.BUILDING)
                        self.move_mark_unsafe(ship, direction)


    def get_points_building(self, ship, directions):
        """
        GET POINTS FOR BULDING

        :param ship:
        :param directions:
        :return: POINTS
        """
        points = []

        for direction in directions:
            ## POINTS FOR MOVING
            destination = self.get_destination(ship, direction)
            safe = self.data.myMatrix.locations.safe[destination.y][destination.x]
            full = 0
            leave_cost = self.data.myMatrix.halite.cost[ship.position.y][ship.position.x]
            harvest = self.data.myMatrix.halite.harvest[destination.y][destination.x]
            influenced = True if self.data.myMatrix.locations.influenced[destination.y][destination.x] >= MyConstants.INFLUENCED else False
            bonus = (harvest * 2) if influenced else 0
            potential_harvest = harvest + bonus
            final_harvest = potential_harvest - leave_cost
            b = BuildPoints(safe, full, final_harvest, direction)
            points.append(b)

        ## POINTS FOR STAYING
        safe = self.data.myMatrix.locations.safe[ship.position.y][ship.position.x]
        full = -1 if ship.halite_amount > 800 else 0  ## ALMOST FULL IS ENOUGH, DONT WANT TO STAY TO JUST GET SMALL AMOUNT
        harvest_stay = self.data.myMatrix.halite.harvest[ship.position.y][ship.position.x]
        harvest = harvest_stay + harvest_stay * 0.75  ## SECOND HARVEST IS 0.75 OF FIRST HARVEST
        points.append(BuildPoints(safe=safe, full=full, harvest=harvest, direction=Direction.Still))

        logging.debug(points)

        return points
