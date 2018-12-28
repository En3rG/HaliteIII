from hlt.positionals import Position
from hlt.positionals import Direction
from src.common.halite_statistics import BuildType
from src.common.values import MyConstants, Matrix_val, MoveMode, Inequality
from src.common.matrix.functions import populate_manhattan, get_coord_closest
from src.common.points import BuildPoints, BuildShip
from src.common.matrix.functions import get_coord_closest, pad_around, Section
from src.common.astar import a_star, get_goal_in_section
from src.common.orderedSet import OrderedSet
import numpy as np
import logging
import heapq

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
            cell_halite_amount = self.data.myMatrix.halite.amount[ship.position.y][ship.position.x]

            if self.withinLimit_ships():
                if ship.halite_amount + self.data.game.me.halite_amount + cell_halite_amount >= 4000:
                    ## HAVE ENOUGH HALITE TO BUILD DOCK
                    self.data.game.me.halite_amount -= (4000 - ship.halite_amount - cell_halite_amount)
                    logging.debug("Shid id: {} building dock at position: {}".format(ship.id, ship.position))
                    self.data.halite_stats.record_spent(BuildType.DOCK)
                    command = ship.make_dropoff()
                    self.data.command_queue.append(command)

                    ## CLEAR DOCK AREA, SO THAT OTHER SHIPS WILL NOT TRY TO BUILD ON IT
                    populate_manhattan(self.data.init_data.myMatrix.locations.dock_placement,
                                       Matrix_val.ZERO,
                                       ship.position,
                                       MyConstants.DOCK_MANHATTAN)
                else:
                    ## NOT ENOUGH HALITE YET, STAY STILL
                    self.data.myVars.isBuilding = True                                                                      ## PREVENT SPAWNING SHIPS
                    direction = Direction.Still
                    command = ship.move(direction)
                    self.data.command_queue.append(command)

                ## RECORD INFO ALSO SHIP COUNTER PER DOCK
                dock_coord = (ship.position.y, ship.position.x)
                self.ships_building_towards_dock.setdefault(dock_coord, set())
                self.ships_building_towards_dock[dock_coord].add(ship.id)
                self.mark_unsafe(ship, ship.position)
                self.data.mySets.ships_to_move.remove(ship.id)



    def building_later(self):
        """
        MOVE SHIPS RIGHT NEXT TO DOCK POSITION
        """
        i = MyConstants.DOCK_MANHATTAN - 1                                                                              ## CURRENTLY RIGHT NEXT TO THE DOCK

        r, c = np.where(self.data.init_data.myMatrix.locations.dock_placement == i)
        matrixIDs = OrderedSet(self.data.myMatrix.locations.myShipsID[r, c])
        ships_going_dock = matrixIDs & self.data.mySets.ships_to_move

        logging.debug("ship next to dock: {}".format(ships_going_dock))

        for ship_id in ships_going_dock:
            ship = self.data.game.me._ships.get(ship_id)
            dock_coord = self.get_dock_coord(ship)                                                                      ## DOCK COORD IS NONE IF ENEMY BUILT THERE
            self.ships_building_towards_dock.setdefault(dock_coord, set())

            if dock_coord \
                and len(self.ships_building_towards_dock[dock_coord]) < MyConstants.SHIPS_BUILDING_PER_DOCK \
                and self.withinLimit_ships():

                if self.data.game.me.halite_amount < 5000:
                    self.data.myVars.isBuilding = True                                                                  ## PREVENT SPAWNING SHIPS

                dock_position = Position(dock_coord[1], dock_coord[0])
                directions = self.get_directions_target(ship, dock_position)
                dock_halite_amount = self.data.myMatrix.halite.amount[dock_position.y][dock_position.x]

                if ship.halite_amount + self.data.game.me.halite_amount + dock_halite_amount >= 4000 \
                        and self.data.myMatrix.locations.safe[dock_position.y][dock_position.x] != Matrix_val.UNSAFE:
                    ## ENOUGH HALITE TO BUILD
                    direction = self.best_direction(ship, directions, mode=MoveMode.BUILDING,
                                                    avoid_enemy=True, avoid_potential_enemy=False)
                    self.move_mark_unsafe(ship, direction)                                                              ## DIRECTION IS A LIST OF DIRECTIONS
                else:
                    ## POPULATE UNSAFE AROUND DOCK SO NO OTHER SHIPS WILL GO TOWARDS IT
                    # self.data.myMatrix.locations.safe[dock_position.y][dock_position.x] = Matrix_val.UNSAFE
                    self.move_mark_unsafe(ship, Direction.Still)

                ## SHIP COUNTER PER DOCK
                self.ships_building_towards_dock[dock_coord].add(ship.id)


    def go_towards_building(self):
        """
        MOVE SHIPS TOWARD BUILDING DOCK
        """
        heap_halite = []

        if MyConstants.DOCK_MANHATTAN > 2:
            for i in range(MyConstants.DOCK_MANHATTAN - 2, 0, -1):                                                      ## MOVES SHIPS CLOSEST TO DOCK FIRST
                r, c = np.where(self.data.init_data.myMatrix.locations.dock_placement == i)
                matrixIDs = OrderedSet(self.data.myMatrix.locations.myShipsID[r, c])
                ships_going_dock = matrixIDs & self.data.mySets.ships_to_move

                logging.debug("ship going to dock: {} at i {}".format(ships_going_dock, i))

                ## POPULATE HEAP
                for ship_id in ships_going_dock:
                    ship = self.data.game.me._ships.get(ship_id)
                    s = BuildShip(ship.halite_amount, ship_id)
                    heapq.heappush(heap_halite, s)

                while heap_halite:
                    s = heapq.heappop(heap_halite)
                    logging.debug(s)

                    ship = self.data.game.me._ships.get(s.ship_id)
                    dock_coord = self.get_dock_coord(ship)                                                              ## DOCK COORD IS NONE IF ENEMY BUILT THERE
                    self.ships_building_towards_dock.setdefault(dock_coord, set())

                    #if dock_coord and (ship.halite_amount >= 1000 or ship_id in self.prev_data.ships_building):
                    if dock_coord and ship.halite_amount >= MyConstants.HALITE_TOWARDS_BUILDING \
                        and len(self.ships_building_towards_dock[dock_coord]) < MyConstants.SHIPS_BUILDING_PER_DOCK \
                        and self.withinLimit_ships():

                        dock_position = Position(dock_coord[1], dock_coord[0])
                        directions = self.get_directions_target(ship, dock_position)

                        if self.data.game.me.halite_amount < 5000:
                            self.data.myVars.isBuilding = True                                                          ## PREVENT SPAWNING SHIPS

                        ## OLD WAY
                        #direction = self.best_direction(ship, directions, mode=MoveMode.BUILDING, avoid_enemy=False, avoid_potential_enemy=False)
                        ## A STAR WAY
                        direction = self.get_a_star_direction(ship, dock_position, directions)

                        ## RECORD INFO ALSO SHIP COUNTER PER DOCK
                        self.data.mySets.ships_building.add(ship_id)
                        self.ships_building_towards_dock[dock_coord].add(ship.id)
                        self.move_mark_unsafe(ship, direction)


    def get_dock_coord(self, ship):
        curr_cell = (ship.position.y, ship.position.x)
        dock_coord, distance, val = get_coord_closest(MyConstants.DOCK_MANHATTAN,
                                                      self.data.init_data.myMatrix.locations.dock_placement,
                                                      self.data.init_data.myMatrix.distances.cell[curr_cell],
                                                      Inequality.EQUAL)

        return dock_coord


    def withinLimit_ships(self):
        """
        CHECK IF SHIPS BUILDING IS WITHIN PERCENT LIMIT
        """
        num_ships = len(self.data.mySets.ships_all)
        num_ships_allowed = num_ships * MyConstants.SHIPS_BUILDING_PERCENT
        num_ships_building = sum([len(x) for x in self.ships_building_towards_dock.values()])
        num_docks = len(self.data.mySets.dock_coords)
        return (num_ships_building <= num_ships_allowed) and ( ( num_ships / (num_docks + num_ships_building)) >= MyConstants.SHIPS_PER_DOCK_RATIO)


    def get_a_star_direction(self, ship, dock_position, directions):
        ## PATH IS 1 LESS, SINCE WILL BE PADDED
        section = Section(self.data.myMatrix.locations.potential_enemy_collisions,
                          ship.position, MyConstants.DEPOSIT_SEARCH_PERIMETER - 1)
        matrix_path = pad_around(section.matrix)
        section = Section(self.data.myMatrix.halite.amount, ship.position, MyConstants.DEPOSIT_SEARCH_PERIMETER)
        matrix_cost = section.matrix
        goal_position = get_goal_in_section(matrix_path, section.center, ship.position, dock_position, directions)
        path = a_star(matrix_path, matrix_cost, section.center, goal_position, lowest_cost=True)

        if len(path) > 1:
            start_coord = path[-1]
            next_coord = path[-2]
            start = Position(start_coord[1], start_coord[0])
            destination = Position(next_coord[1], next_coord[0])
            directions = self.get_directions_start_target(start, destination)
            direction = self.best_direction(ship, directions, mode=MoveMode.BUILDING,
                                            avoid_enemy=True, avoid_potential_enemy=True)
        else:
            direction = self.best_direction(ship, directions, mode=MoveMode.BUILDING,
                                            avoid_enemy=True, avoid_potential_enemy=False)

        return direction


    def get_move_points_building(self, ship, directions, avoid_enemy, avoid_potential_enemy):
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
            destination = self.get_destination(ship, direction)
            safe = self.data.myMatrix.locations.safe[destination.y][destination.x]
            enemy_occupied = self.data.myMatrix.locations.enemyShips[destination.y][destination.x]
            potential_enemy_collision = self.data.myMatrix.locations.potential_enemy_collisions[destination.y][destination.x]
            cost = self.data.myMatrix.halite.cost[destination.y][destination.x]
            b = BuildPoints(safe, enemy_occupied, potential_enemy_collision, cost, direction,
                            avoid_enemy, avoid_potential_enemy)
            points.append(b)

        ## POINTS FOR STAYING
        safe = self.data.myMatrix.locations.safe[ship.position.y][ship.position.x]
        enemy_occupied = self.data.myMatrix.locations.enemyShips[ship.position.y][ship.position.x]
        potential_enemy_collision = self.data.myMatrix.locations.potential_enemy_collisions[ship.position.y][ship.position.x]
        points.append(BuildPoints(safe=safe,
                                  enemy_occupied=enemy_occupied,
                                  potential_enemy_collision=potential_enemy_collision,
                                  cost=999,
                                  direction=Direction.Still,
                                  avoid_enemy=avoid_enemy,
                                  avoid_potential_enemy=avoid_potential_enemy))

        logging.debug(points)

        return points