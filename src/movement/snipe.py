from src.common.move.moves import Moves
from src.common.move.explores import Explores
from src.common.move.harvests import Harvests
from src.common.values import MoveMode, MyConstants, Matrix_val, Inequality
import logging
from src.common.print import print_heading, print_matrix
from src.common.points import ExploreShip, ExplorePoints
from src.common.astar import a_star, get_goal_in_section
from src.movement.collision_prevention import move_kicked_ship
from hlt.positionals import Direction
from src.common.matrix.functions import get_coord_closest, get_n_closest_masked, populate_manhattan, \
    get_coord_max_closest, pad_around, Section
from hlt.positionals import Position
from hlt import constants
import heapq
import copy
import numpy as np



class Snipe(Moves, Explores, Harvests):
    def __init__(self, data, prev_data):
        Moves.__init__(self, data, prev_data)

        allowSnipe = (constants.MAX_TURNS * MyConstants.SNIPE_TURNS_LOWER_LIMIT <= self.data.game.turn_number <= constants.MAX_TURNS * MyConstants.SNIPE_TURNS_UPPER_LIMIT)
                       # and len(data.game.players) == 2

        if allowSnipe:
            self.move_ships()

    ## NOT RECALCULATING EXPLORE TARGETS
    def move_ships(self):
        print_heading("Moving sniping ships......")

        for target in self.data.myLists.snipe_target:
            ship_id = target.ship_id
            ship = self.data.game.me._ships.get(ship_id)

            if ship_id in self.data.mySets.ships_to_move:
                explore_target = self.data.myDicts.explore_ship[ship_id]
                explore_destination = explore_target.destination
                snipe_destination = target.destination

                directions = self.get_directions_target(ship, snipe_destination)
                ## OLD WAY
                snipe_direction = self.best_direction(ship, directions, mode=MoveMode.EXPLORE)
                ## USING ASTAR
                #snipe_direction = self.get_Astar_direction(ship, explore_destination, directions)


                if -target.ratio > -explore_target.ratio * MyConstants.EXPLORE_RATIO_TO_SNIPE:
                    destination = snipe_destination
                    direction = snipe_direction

                    logging.debug("snipe_destination {} -target.ratio {} explore_destination {} explore_target.ratio {}".format(snipe_destination, -target.ratio, explore_destination, explore_target.ratio))

                    if direction == Direction.Still and self.data.myMatrix.locations.myDocks[ship.position.y][
                        ship.position.x] == Matrix_val.ONE:
                        ## IF STILL AND AT A DOCK (MOVE!!)
                        move_kicked_ship(self, ship)  ## NOT REALLY KICKED
                    else:
                        #self.mark_taken_udpate_top_halite(destination)
                        self.move_mark_unsafe(ship, direction)


    def get_Astar_direction(self, ship, target_position, directions):
        ## PATH IS 1 LESS, SINCE WILL BE PADDED
        # section_enemy = Section(self.data.myMatrix.locations.potential_enemy_collisions, ship.position,
        #                         MyConstants.RETREAT_SEARCH_PERIMETER - 1)
        # section_ally = Section(self.data.myMatrix.locations.safe, ship.position,
        #                        MyConstants.RETREAT_SEARCH_PERIMETER - 1)
        # section = section_enemy.matrix + section_ally.matrix
        # matrix_path = pad_around(section)
        section = Section(self.data.myMatrix.locations.potential_enemy_collisions, ship.position,
                          MyConstants.EXPLORE_SEARCH_PERIMETER - 1)
        matrix_path = pad_around(section.matrix)
        section = Section(self.data.myMatrix.halite.amount, ship.position,
                          MyConstants.EXPLORE_SEARCH_PERIMETER)
        matrix_cost = section.matrix
        goal_position = get_goal_in_section(matrix_path, section.center, ship.position, target_position, directions)
        path = a_star(matrix_path, matrix_cost, section.center, goal_position, lowest_cost=True)

        if len(path) > 1:
            start_coord = path[-1]
            next_coord = path[-2]
            start = Position(start_coord[1], start_coord[0])
            destination = Position(next_coord[1], next_coord[0])
            directions = self.get_directions_start_target(start, destination)
            direction = self.best_direction(ship, directions, mode=MoveMode.EXPLORE,
                                            avoid_enemy=True, avoid_potential_enemy=True)
        else:
            direction = self.best_direction(ship, directions, mode=MoveMode.EXPLORE,
                                            avoid_enemy=True, avoid_potential_enemy=False)

        return direction









