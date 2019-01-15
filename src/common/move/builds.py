from hlt.positionals import Position
from hlt.positionals import Direction
from src.common.halite_statistics import BuildType
from src.common.values import MyConstants, Matrix_val, MoveMode, Inequality
from src.common.matrix.functions import populate_manhattan, get_coord_closest
from src.common.points import BuildPoints, BuildShip
from src.common.matrix.functions import get_coord_closest, pad_around, Section, count_manhattan
from src.common.astar import a_star, get_goal_in_section
from src.common.orderedSet import OrderedSet
from src.common.matrix.classes import Option
import numpy as np
import logging
import abc
import heapq

class Builds(abc.ABC):
    def build_on_high_halite(self):
        """
        BUILD A DOCK RIGHT AWAY ON A HIGH COLLISION CELL, TO PREVENT ENEMY FROM HARVESTING IT
        """
        ## BUILD ANYWHERE WHERE HALITE IS HIGH
        r, c = np.where(self.data.myMatrix.halite.amount >= MyConstants.build.dock_anywhere_halite)
        ships_on_high_halite = OrderedSet(self.data.myMatrix.locations.myShipsID[r, c])
        ships_building = ships_on_high_halite & self.data.mySets.ships_to_move

        self.building_aggressively(ships_building, check_close_docks=False)

        ## BUILD WHERE HALITE IS MEDIUM AND NO CLOSE DOCKS
        r, c = np.where(self.data.myMatrix.halite.amount >= MyConstants.build.dock_far_halite)
        ships_on_high_halite = OrderedSet(self.data.myMatrix.locations.myShipsID[r, c])
        ships_building = ships_on_high_halite & self.data.mySets.ships_to_move

        self.building_aggressively(ships_building, check_close_docks=True)


    def building_aggressively(self, ships_building, check_close_docks):
        for ship_id in sorted(ships_building):
            ship = self.data.game.me._ships.get(ship_id)
            cell_halite_amount = self.data.myMatrix.halite.amount[ship.position.y][ship.position.x]

            if check_close_docks:
                passCriteria = self.get_criteria(ship)
            else:
                passCriteria = True

            if ship.halite_amount + self.data.game.me.halite_amount + cell_halite_amount >= 4000 \
                    and passCriteria:
                ## HAVE ENOUGH HALITE TO BUILD DOCK
                halite_used = 0 if ship.halite_amount + cell_halite_amount >= 4000 else (4000 - ship.halite_amount - cell_halite_amount)
                self.data.game.me.halite_amount -= halite_used
                logging.debug("Shid id: {} building dock on high halite at position: {}".format(ship.id, ship.position))
                self.data.halite_stats.record_spent(BuildType.DOCK)
                command = ship.make_dropoff()
                self.data.command_queue.append(command)

                ## RECORD INFO ALSO SHIP COUNTER PER DOCK
                dock_coord = (ship.position.y, ship.position.x)
                self.data.myDicts.ships_building_dock.setdefault(dock_coord, set())
                self.data.myDicts.ships_building_dock[dock_coord].add(ship.id)
                self.mark_unsafe(ship, ship.position)
                self.data.mySets.ships_to_move.remove(ship.id)


    def get_criteria(self, ship):
        curr_cell = (ship.position.y, ship.position.x)
        coord, distance, val = get_coord_closest(Matrix_val.ONE,
                                                 self.data.myMatrix.locations.myDocks,
                                                 self.data.init_data.myMatrix.distances.cell[curr_cell],
                                                 Inequality.EQUAL)

        ally_count = count_manhattan(self.data.myMatrix.locations.myShips,
                                      Matrix_val.ONE,
                                      ship.position,
                                      MyConstants.build.far_enemy_perimeter)

        enemy_count = count_manhattan(self.data.myMatrix.locations.enemyShips,
                                      Matrix_val.ONE,
                                      ship.position,
                                      MyConstants.build.far_enemy_perimeter)

        if distance >= MyConstants.build.considered_far_distance \
                and enemy_count > ally_count:
            passCriteria = True
        else:
            passCriteria = False

        return passCriteria


    def building_now(self):
        """
        MOVE SHIPS BUILDING NOW (CURRENTLY AT DOCK POSITION)
        """
        r, c = np.where(self.data.myMatrix.docks.manhattan == MyConstants.build.dock_manhattan)
        ships_on_docks = OrderedSet(self.data.myMatrix.locations.myShipsID[r, c])
        ships_building = ships_on_docks & self.data.mySets.ships_to_move

        for ship_id in sorted(ships_building):
            ship = self.data.game.me._ships.get(ship_id)
            cell_halite_amount = self.data.myMatrix.halite.amount[ship.position.y][ship.position.x]

            if self.withinLimit_ships():
                self.data.myVars.isBuilding = True
                if ship.halite_amount + self.data.game.me.halite_amount + cell_halite_amount >= 4000:
                    ## HAVE ENOUGH HALITE TO BUILD DOCK
                    self.data.game.me.halite_amount -= (4000 - ship.halite_amount - cell_halite_amount)
                    logging.debug("Shid id: {} building dock at position: {}".format(ship.id, ship.position))
                    self.data.halite_stats.record_spent(BuildType.DOCK)
                    command = ship.make_dropoff()
                    self.data.command_queue.append(command)

                    ## CLEAR DOCK AREA, SO THAT OTHER SHIPS WILL NOT TRY TO BUILD ON IT
                    populate_manhattan(self.data.myMatrix.docks.manhattan,
                                       Matrix_val.ZERO,
                                       ship.position,
                                       MyConstants.build.dock_manhattan, Option.REPLACE)

                    self.data.init_data.myMatrix.docks.placement[ship.position.y][ship.position.x] = Matrix_val.ZERO
                    self.data.init_data.myMatrix.docks.order[ship.position.y][ship.position.x] = Matrix_val.NINETY
                else:
                    ## NOT ENOUGH HALITE YET, STAY STILL
                    self.data.myVars.isSaving = True                                                                      ## PREVENT SPAWNING SHIPS
                    direction = Direction.Still
                    command = ship.move(direction)
                    self.data.command_queue.append(command)

                ## RECORD INFO ALSO SHIP COUNTER PER DOCK
                dock_coord = (ship.position.y, ship.position.x)
                self.data.myDicts.ships_building_dock.setdefault(dock_coord, set())
                self.data.myDicts.ships_building_dock[dock_coord].add(ship.id)
                self.mark_unsafe(ship, ship.position)
                self.data.mySets.ships_to_move.remove(ship.id)



    def building_later(self):
        """
        MOVE SHIPS RIGHT NEXT TO DOCK POSITION
        """
        i = MyConstants.build.dock_manhattan - 1                                                                              ## CURRENTLY RIGHT NEXT TO THE DOCK

        r, c = np.where(self.data.myMatrix.docks.manhattan == i)
        matrixIDs = OrderedSet(self.data.myMatrix.locations.myShipsID[r, c])
        ships_going_dock = matrixIDs & self.data.mySets.ships_to_move

        logging.debug("ship next to dock: {}".format(ships_going_dock))

        for ship_id in sorted(ships_going_dock):
            ship = self.data.game.me._ships.get(ship_id)
            dock_coord = self.get_closest_dock_coord(ship)                                                                      ## DOCK COORD IS NONE IF ENEMY BUILT THERE
            self.data.myDicts.ships_building_dock.setdefault(dock_coord, set())

            if dock_coord \
                and len(self.data.myDicts.ships_building_dock[dock_coord]) < MyConstants.build.ships_per_dock \
                and self.withinLimit_ships():

                self.data.myVars.isBuilding = True

                if self.data.game.me.halite_amount < 5000:
                    self.data.myVars.isSaving = True                                                                  ## PREVENT SPAWNING SHIPS

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
                self.data.myDicts.ships_building_dock[dock_coord].add(ship.id)


    def go_towards_building(self):
        """
        MOVE SHIPS TOWARD BUILDING DOCK
        """
        heap_halite = []

        if MyConstants.build.dock_manhattan > 2:
            for i in range(MyConstants.build.dock_manhattan - 2, 0, -1):                                                      ## MOVES SHIPS CLOSEST TO DOCK FIRST
                r, c = np.where(self.data.myMatrix.docks.manhattan == i)
                matrixIDs = OrderedSet(self.data.myMatrix.locations.myShipsID[r, c])
                ships_going_dock = matrixIDs & self.data.mySets.ships_to_move

                logging.debug("ship going to dock: {} at i {}".format(ships_going_dock, i))

                ## POPULATE HEAP
                for ship_id in sorted(ships_going_dock):
                    ship = self.data.game.me._ships.get(ship_id)
                    s = BuildShip(ship.halite_amount, ship_id)
                    heapq.heappush(heap_halite, s)

                while heap_halite:
                    s = heapq.heappop(heap_halite)
                    logging.debug(s)

                    ship = self.data.game.me._ships.get(s.ship_id)
                    dock_coord = self.get_closest_dock_coord(ship)                                                              ## DOCK COORD IS NONE IF ENEMY BUILT THERE
                    self.data.myDicts.ships_building_dock.setdefault(dock_coord, set())

                    #if dock_coord and (ship.halite_amount >= 1000 or ship_id in self.prev_data.ships_building):
                    if dock_coord and ship.halite_amount >= MyConstants.build.min_halite_amount \
                        and len(self.data.myDicts.ships_building_dock[dock_coord]) < MyConstants.build.ships_per_dock \
                        and self.withinLimit_ships():

                        self.data.myVars.isBuilding = True

                        dock_position = Position(dock_coord[1], dock_coord[0])
                        directions = self.get_directions_target(ship, dock_position)

                        if self.data.game.me.halite_amount < 5000:
                            self.data.myVars.isSaving = True                                                          ## PREVENT SPAWNING SHIPS

                        ## OLD WAY
                        #direction = self.best_direction(ship, directions, mode=MoveMode.BUILDING, avoid_enemy=False, avoid_potential_enemy=False)
                        ## A STAR WAY
                        direction = self.get_Astar_direction(ship, dock_position, directions)

                        ## RECORD INFO ALSO SHIP COUNTER PER DOCK
                        self.data.mySets.ships_building.add(ship_id)
                        self.data.myDicts.ships_building_dock[dock_coord].add(ship.id)
                        self.move_mark_unsafe(ship, direction)


    def get_closest_dock_coord(self, ship):
        curr_cell = (ship.position.y, ship.position.x)
        dock_coord, distance, val = get_coord_closest(MyConstants.build.dock_manhattan,
                                                      self.data.myMatrix.docks.manhattan,
                                                      self.data.init_data.myMatrix.distances.cell[curr_cell],
                                                      Inequality.EQUAL)

        return dock_coord


    def withinLimit_ships(self):
        """
        CHECK IF SHIPS BUILDING IS WITHIN PERCENT LIMIT
        """
        num_ships = len(self.data.mySets.ships_all)
        num_ships_allowed = num_ships * MyConstants.build.ships_percent
        num_ships_building = sum([len(x) for x in self.data.myDicts.ships_building_dock.values()])
        num_docks = len(self.data.mySets.dock_coords)
        return (num_ships_building <= num_ships_allowed) and ( ( num_ships / (num_docks + num_ships_building)) >= MyConstants.build.ships_per_dock_ratio)


    def get_Astar_direction(self, ship, dock_position, directions):
        ## PATH IS 1 LESS, SINCE WILL BE PADDED
        # section_enemy = Section(self.data.myMatrix.locations.potential_enemy_collisions, ship.position,
        #                         MyConstants.RETREAT_SEARCH_PERIMETER - 1)
        # section_ally = Section(self.data.myMatrix.locations.safe, ship.position,
        #                        MyConstants.RETREAT_SEARCH_PERIMETER - 1)
        # section = section_enemy.matrix + section_ally.matrix
        # matrix_path = pad_around(section)
        section = Section(self.data.myMatrix.locations.potential_enemy_collisions,
                          ship.position, MyConstants.deposit.search_perimeter - 1)
        matrix_path = pad_around(section.matrix)
        section = Section(self.data.myMatrix.halite.amount, ship.position, MyConstants.deposit.search_perimeter)
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