
from hlt.positionals import Direction
import heapq
from src.common.values import MoveMode, MyConstants, Matrix_val, Inequality
from src.common.points import FarthestShip, RetreatPoints
from src.common.astar import a_star, get_goal_in_section
from src.common.matrix.functions import get_coord_closest, pad_around, Section
from hlt.positionals import Position
import logging

class Retreats():
    def move_ships(self):
        """
        MOVE ALL SHIPS TO RETREAT BACK TO SHIPYARD/DOCKS
        """
        while self.heap_dist:
            s = heapq.heappop(self.heap_dist)                                                                           ## MOVE CLOSEST SHIPS FIRST, TO PREVENT COLLISIONS
            logging.debug(s)                                                                                            ## FARTHEST SHIP OBJECT

            ship = self.data.game.me.get_ship(s.ship_id)

            ## OLD WAY
            #direction = self.best_direction(ship, s.directions, mode=MoveMode.RETREAT)
            ## USING ASTAR
            direction = self.get_Astar_direction(ship, s.dock_position, s.directions)

            self.move_mark_unsafe(ship, direction)


    def get_Astar_direction(self, ship, dock_position, directions):
        ## WILL NOW ALWAYS USE A STAR (WITH OR WITHOUT ENEMY AROUND)
        # if self.isEnemy_closeby(ship):
        ## PATH IS 1 LESS, SINCE WILL BE PADDED
        section_enemy = Section(self.data.myMatrix.locations.potential_enemy_collisions, ship.position, MyConstants.RETREAT_SEARCH_PERIMETER - 1)
        section_ally = Section(self.data.myMatrix.locations.safe, ship.position, MyConstants.RETREAT_SEARCH_PERIMETER - 1)
        section = section_enemy.matrix + section_ally.matrix
        matrix_path = pad_around(section)
        section = Section(self.data.myMatrix.halite.amount, ship.position, MyConstants.RETREAT_SEARCH_PERIMETER)
        matrix_cost = section.matrix
        goal_position = get_goal_in_section(matrix_path, section.center, ship.position, dock_position, directions)
        path = a_star(matrix_path, matrix_cost, section.center, goal_position, lowest_cost=True)

        if len(path) > 1:
            start_coord = path[-1]
            next_coord = path[-2]
            start = Position(start_coord[1], start_coord[0])
            destination = Position(next_coord[1], next_coord[0])
            directions = self.get_directions_start_target(start, destination)
            direction = self.best_direction(ship, directions, mode=MoveMode.RETREAT,
                                            avoid_enemy=True, avoid_potential_enemy=True)
        else:
            direction = self.best_direction(ship, directions, mode=MoveMode.RETREAT,
                                            avoid_enemy=True, avoid_potential_enemy=True)

        return direction

    def get_move_points_retreat(self, ship, directions):
        """
        GET POINTS FOR RETREATING

        :param ship:
        :param directions: CLEAN POSSIBLE DIRECTIONS
        :return:
        """
        ## IF OTHER ARE UNSAFE, PICK THIS DIRECTION (STILL)
        points = [RetreatPoints(shipyard=0,
                                safe=1,
                                stuck=0,
                                potential_ally_collision=-999,
                                direction=Direction.Still)]

        for direction in directions:
            # for direction in MyConstants.DIRECTIONS:

            destination = self.get_destination(ship, direction)

            shipyard = self.data.myMatrix.locations.myDocks[destination.y][destination.x]
            safe = self.data.myMatrix.locations.safe[destination.y][destination.x]
            potential_ally_collision = self.data.myMatrix.locations.potential_ally_collisions[destination.y][destination.x]
            stuck = self.data.myMatrix.locations.stuck[ship.position.y][ship.position.x]                                ## STUCK BASED ON SHIPS CURRENT POSITION

            c = RetreatPoints(shipyard, safe, stuck, potential_ally_collision, direction)
            points.append(c)

        logging.debug(points)

        return points