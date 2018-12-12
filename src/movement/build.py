from src.common.print import print_heading, print_matrix
from src.common.moves import Moves
from hlt.positionals import Position
from hlt.positionals import Direction
from src.common.halite_statistics import BuildType
from src.common.values import MyConstants, Matrix_val, MoveMode, Inequality
from src.common.matrix.functions import populate_manhattan, get_coord_closest
from src.common.points import BuildPoints
from src.common.classes import OrderedSet
import numpy as np
import logging


"""
TO DO!!!!!111

BEST TO HAVE DOCKS CLOSE TO ENEMY AND GAIN ALOT OF INFLUENCE

DONT BUILD DOCK WHEN AREA HAS BEEN HARVESTED


ADD BUILD DOCK WHEN CLOSE ENOUGH TO DOCK PLACEMENT AND FULL, BUILD RATHER THAN GO HOME



"""

class Build(Moves):
    def __init__(self, data, prev_data):
        super().__init__(data, prev_data)

        self.move_ships()

    def move_ships(self):
        print_heading("Moving build (dock) ships......")

        if self.data.myVars.allowBuild:
            self.building_now()
            self.building_later()
            self.go_towards_building()


    def building_now(self):
        """
        MOVE SHIPS BUILDING NOW (AT DOCK POSITION)
        """
        r, c = np.where(self.data.init_data.myMatrix.locations.dock_placement == MyConstants.DOCK_MANHATTAN)
        ships_on_docks = OrderedSet(self.data.myMatrix.locations.myShipsID[r, c])

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
        MOVE SHIPS NEXT TO DOCK POSITION
        """
        i = MyConstants.DOCK_MANHATTAN - 1  ## CURRENTLY RIGHT NEXT TO THE DOCK

        r, c = np.where(self.data.init_data.myMatrix.locations.dock_placement == i)
        matrixIDs = OrderedSet(self.data.myMatrix.locations.myShipsID[r, c])
        ships_going_dock = matrixIDs & self.data.mySets.ships_to_move

        for ship_id in ships_going_dock:
            ship = self.data.game.me._ships.get(ship_id)

            ## GET DOCK POSITION
            curr_cell = (ship.position.y, ship.position.x)
            coord, distance, val = get_coord_closest(MyConstants.DOCK_MANHATTAN,
                                                     self.data.init_data.myMatrix.locations.dock_placement,
                                                     self.data.init_data.myMatrix.distances.cell[curr_cell],
                                                     Inequality.EQUAL)

            dock_position = Position(coord[1], coord[0])
            directions = self.get_directions_target(ship, dock_position)

            if coord:  ## THIS WILL BE NONE IF ENEMY CREATED A DOCK IN OUR DOCK LOCATION
                self.data.myVars.isBuilding = True  ## SET TO TRUE, SO THAT IF WE DONT HAVE ENOUGH HALITE NOW, WILL NOT SPAWN SHIPS STILL

                ## TAKE INTO ACCOUNT SHIP.HALITE_AMOUNT, DOCK HALITE AMOUNT, PLUS CURRENT PLAYER HALITE AMOUNT
                ## ALSO MAKE SURE ITS SAFE TO GO THERE
                if ship.halite_amount + self.data.game.me.halite_amount + self.data.myMatrix.halite.amount[dock_position.y][dock_position.x] > 4000 \
                        and self.data.myMatrix.locations.safe[dock_position.y][dock_position.x] != Matrix_val.UNSAFE:
                    self.move_mark_unsafe(ship, directions[0]) ## DIRECTION IS A LIST OF DIRECTIONS
                else:
                    self.move_mark_unsafe(ship, Direction.Still)


    def go_towards_building(self):
        """
        MOVE SHIPS TOWARD BUILDING DOCK
        """
        if MyConstants.DOCK_MANHATTAN > 2:
            for i in range(MyConstants.DOCK_MANHATTAN - 2, 0, -1):  ## MOVES SHIPS CLOSEST TO DOCK FIRST
                r, c = np.where(self.data.init_data.myMatrix.locations.dock_placement == i)
                matrixIDs = OrderedSet(self.data.myMatrix.locations.myShipsID[r, c])
                ships_going_dock = matrixIDs & self.data.mySets.ships_to_move

                for ship_id in ships_going_dock:
                    ship = self.data.game.me._ships.get(ship_id)

                    if ship.halite_amount > 1000 or ship_id in self.prev_data.ships_returning:
                        ## GET DOCK POSITION
                        curr_cell = (ship.position.y, ship.position.x)
                        coord, distance, val = get_coord_closest(self.MyConstants.DOCK_MANHATTAN,
                                                                 self.data.init_data.myMatrix.locations.dock_placement,
                                                                 self.data.init_data.myMatrix.distances.cell[curr_cell],
                                                                 Inequality.EQUAL)

                        if coord:  ## THIS WILL BE NONE IF ENEMY CREATED A DOCK IN OUR DOCK LOCATION
                            dock_position = Position(coord[1], coord[0])
                            directions = self.get_directions_target(ship, dock_position)

                            if coord:  ## THIS WILL BE NONE IF ENEMY CREATED A DOCK IN OUR DOCK LOCATION
                                # self.data.myVars.isBuilding = True  ## SET TO TRUE, SO THAT IF WE DONT HAVE ENOUGH HALITE NOW, WILL NOT SPAWN SHIPS STILL
                                direction = self.best_direction(ship, directions, mode=MoveMode.BUILDING)
                                self.move_mark_unsafe(ship, direction)


    def get_move_points_building(self, ship, directions):
        """
        GET POINTS FOR BULDING
        GET DIRECTION WITH LEAST COST

        :param ship:
        :param directions:
        :return: POINTS
        """
        points = []

        for direction in directions:
            ## POINTS FOR MOVING
            destination = self.get_destination(ship, direction)
            safe = self.data.myMatrix.locations.safe[destination.y][destination.x]
            cost = self.data.myMatrix.halite.cost[destination.y][destination.x]
            b = BuildPoints(safe, cost, direction)
            points.append(b)

        ## POINTS FOR STAYING
        safe = self.data.myMatrix.locations.safe[ship.position.y][ship.position.x]
        points.append(BuildPoints(safe=safe, cost=0, direction=Direction.Still))

        logging.debug(points)

        return points
