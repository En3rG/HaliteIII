from hlt.positionals import Position
from hlt.positionals import Direction
from src.common.halite_statistics import BuildType
from src.common.values import MyConstants, Matrix_val, MoveMode, Inequality
from src.common.matrix.functions import populate_manhattan, get_coord_closest
from src.common.points import BuildPoints
from src.common.classes import OrderedSet
import numpy as np
import logging

class Builds():
    def building_now(self):
        """
        MOVE SHIPS BUILDING NOW (CURRENTLY AT DOCK POSITION)
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
                command = ship.make_dropoff()
                self.data.commands.set_ships_move(ship.id, command, None, ship.position, None)
                self.data.commands.set_coords_taken((ship.position.y, ship.position.x), ship.id)
                self.data.command_queue.append(command)

                ## CLEAR DOCK AREA, SO THAT OTHER SHIPS WILL NOT TRY TO BUILD ON IT
                # self.data.init_data.myMatrix.locations.dock_placement[ship.position.y][ship.position.x] = 0
                populate_manhattan(self.data.init_data.myMatrix.locations.dock_placement,
                                   Matrix_val.ZERO,
                                   ship.position,
                                   MyConstants.DOCK_MANHATTAN)
            else:
                ## NOT ENOUGH HALITE YET, STAY STILL
                direction = Direction.Still
                command = ship.move(direction)
                self.data.commands.set_ships_move(ship.id, command, direction, ship.position, None)
                self.data.commands.set_coords_taken((ship.position.y, ship.position.x), ship.id)
                self.data.command_queue.append(command)


    def building_later(self):
        """
        MOVE SHIPS RIGHT NEXT TO DOCK POSITION
        """
        i = MyConstants.DOCK_MANHATTAN - 1  ## CURRENTLY RIGHT NEXT TO THE DOCK

        r, c = np.where(self.data.init_data.myMatrix.locations.dock_placement == i)
        matrixIDs = OrderedSet(self.data.myMatrix.locations.myShipsID[r, c])
        ships_going_dock = matrixIDs & self.data.mySets.ships_to_move

        for ship_id in ships_going_dock:
            ship = self.data.game.me._ships.get(ship_id)

            ## GET DOCK POSITION
            curr_cell = (ship.position.y, ship.position.x)
            dock_coord, distance, val = get_coord_closest(MyConstants.DOCK_MANHATTAN,
                                                     self.data.init_data.myMatrix.locations.dock_placement,
                                                     self.data.init_data.myMatrix.distances.cell[curr_cell],
                                                     Inequality.EQUAL)

            if dock_coord:  ## THIS WILL BE NONE IF ENEMY CREATED A DOCK IN OUR DOCK LOCATION
                dock_position = Position(dock_coord[1], dock_coord[0])
                directions = self.get_directions_target(ship, dock_position)

                self.ships_building_towards_dock.setdefault(dock_coord, set())
                if len(self.ships_building_towards_dock[dock_coord]) <= MyConstants.SHIPS_BUILDING_PER_DOCK and self.withinLimit_ships():
                    self.data.myVars.isBuilding = True  ## SET TO TRUE, SO THAT IF WE DONT HAVE ENOUGH HALITE NOW, WILL NOT SPAWN SHIPS STILL

                    ## TAKE INTO ACCOUNT SHIP.HALITE_AMOUNT, DOCK HALITE AMOUNT, PLUS CURRENT PLAYER HALITE AMOUNT
                    ## ALSO MAKE SURE ITS SAFE TO GO THERE
                    if ship.halite_amount + self.data.game.me.halite_amount + self.data.myMatrix.halite.amount[dock_position.y][dock_position.x] > 4000 \
                            and self.data.myMatrix.locations.safe[dock_position.y][dock_position.x] != Matrix_val.UNSAFE:
                        self.move_mark_unsafe(ship, directions[0], [])  ## DIRECTION IS A LIST OF DIRECTIONS
                    else:
                        ## POPULATE UNSAFE AROUND DOCK SO NO OTHER SHIPS WILL GO TOWARDS IT
                        # self.data.myMatrix.locations.safe[dock_position.y][dock_position.x] = Matrix_val.UNSAFE
                        self.move_mark_unsafe(ship, Direction.Still, [])

                    ## SHIP COUNTER PER DOCK
                    self.ships_building_towards_dock[dock_coord].add(ship.id)


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

                    curr_cell = (ship.position.y, ship.position.x)
                    dock_coord, distance, val = get_coord_closest(MyConstants.DOCK_MANHATTAN,
                                                                  self.data.init_data.myMatrix.locations.dock_placement,
                                                                  self.data.init_data.myMatrix.distances.cell[curr_cell],
                                                                  Inequality.EQUAL)

                    ## dock_coord WILL BE NONE IF ENEMY CREATED A DOCK IN OUR DOCK LOCATION
                    if dock_coord and (ship.halite_amount == 1000 or ship_id in self.prev_data.ships_building):
                        self.ships_building_towards_dock.setdefault(dock_coord, set())

                        if len(self.ships_building_towards_dock[dock_coord]) <= MyConstants.SHIPS_BUILDING_PER_DOCK and self.withinLimit_ships():
                            dock_position = Position(dock_coord[1], dock_coord[0])
                            directions = self.get_directions_target(ship, dock_position)

                            self.data.myVars.isBuilding = True  ## SET TO TRUE, SO THAT IF WE DONT HAVE ENOUGH HALITE NOW, WILL NOT SPAWN SHIPS STILL

                            self.data.mySets.ships_building.add(ship_id)
                            direction, points = self.best_direction(ship, directions, mode=MoveMode.BUILDING)
                            self.move_mark_unsafe(ship, direction, points)

                            ## SHIP COUNTER PER DOCK
                            self.ships_building_towards_dock[dock_coord].add(ship.id)


    def withinLimit_ships(self):
        """
        CHECK IF SHIPS BUILDING IS WITHIN PERCENT LIMIT
        """
        return sum([len(x) for x in self.ships_building_towards_dock.values()]) <= len(self.data.mySets.ships_all) * MyConstants.SHIPS_BUILDING_PERCENT


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
            # for direction in MyConstants.DIRECTIONS:
            ## POINTS FOR MOVING
            priority_direction = 1 if direction in directions else 0
            destination = self.get_destination(ship, direction)
            safe = self.data.myMatrix.locations.safe[destination.y][destination.x]
            cost = self.data.myMatrix.halite.cost[destination.y][destination.x]
            b = BuildPoints(priority_direction, safe, cost, direction)
            points.append(b)

        ## POINTS FOR STAYING
        safe = self.data.myMatrix.locations.safe[ship.position.y][ship.position.x]
        points.append(BuildPoints(priority_direction=1, safe=safe, cost=999, direction=Direction.Still))

        logging.debug(points)

        return points