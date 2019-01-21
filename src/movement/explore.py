from src.common.move.moves import Moves
from src.common.move.explores import Explores
from src.common.move.harvests import Harvests
from src.common.values import MoveMode, MyConstants, Matrix_val, Inequality
import logging
from src.common.print import print_heading, print_matrix
from src.common.points import ExploreShip, ExplorePoints
from src.movement.collision_prevention import move_kicked_ship
from hlt.positionals import Direction
from src.common.astar import a_star, get_goal_in_section
from src.common.matrix.functions import get_coord_closest, get_n_closest_masked, populate_manhattan, \
    get_coord_max_closest, pad_around, Section
from hlt.positionals import Position
from hlt import constants
import heapq
import copy
import numpy as np

class Explore(Moves, Explores, Harvests):
    def __init__(self, data, prev_data):
        Moves.__init__(self, data, prev_data)

        self.move_ships()

    ## NOT RECALCULATING EXPLORE TARGETS
    def move_ships(self):
        print_heading("Moving exploring ships......")

        for target in self.data.myLists.explore_target:
            ship_id = target.ship_id
            ship = self.data.game.me._ships.get(ship_id)

            if ship_id in self.data.mySets.ships_to_move:
                explore_destination = target.destination

                canHarvest, harvest_direction = self.check_harvestNow(ship_id, moveNow=False)
                # if not(canHarvest): canHarvest, harvest_direction = self.check_harvestLater(ship_id,
                #                                                                             MyConstants.DIRECTIONS,
                #                                                                             kicked=False,
                #                                                                             moveNow=False)

                directions = self.get_directions_target(ship, explore_destination)
                ## OLD WAY
                explore_direction = self.best_direction(ship, directions, mode=MoveMode.EXPLORE)
                ## USING ASTAR
                #explore_direction = self.get_Astar_direction(ship, explore_destination, directions)

                harvest_destination = self.get_destination(ship, harvest_direction)
                harvest_ratio = target.matrix_ratio[harvest_destination.y][harvest_destination.x]

                if canHarvest and -target.ratio < harvest_ratio * self.data.myVars.harvest_ratio_to_explore:
                    destination = harvest_destination
                    direction = harvest_direction
                else:
                    destination = explore_destination
                    direction = explore_direction

                logging.debug("explore_destination {} -s.ratio {} harvest_destination {} harvest_ratio {}".format(explore_destination, -target.ratio, harvest_destination, harvest_ratio))

                if direction == Direction.Still and self.data.myMatrix.locations.myDocks[ship.position.y][ship.position.x] == Matrix_val.ONE:
                    ## IF STILL AND AT A DOCK (MOVE!!)
                    move_kicked_ship(self, ship, all_directions=True)  ## NOT REALLY KICKED
                else:
                    #self.mark_taken_udpate_top_halite(destination)
                    self.move_mark_unsafe(ship, direction)


    def get_Astar_direction(self, ship, target_position, directions):
        ## PATH IS 1 LESS, SINCE WILL BE PADDED
        section_enemy = Section(self.data.myMatrix.locations.potential_enemy_collisions, ship.position, MyConstants.explore.search_perimeter - 1)
        section_ally = Section(self.data.myMatrix.locations.safe, ship.position, MyConstants.explore.search_perimeter - 1)
        section = section_enemy.matrix + section_ally.matrix
        matrix_path = pad_around(section)
        # section = Section(self.data.myMatrix.locations.potential_enemy_collisions, ship.position,
        #                   MyConstants.explore.search_perimter - 1)
        # matrix_path = pad_around(section.matrix)
        section = Section(self.data.myMatrix.halite.amount, ship.position,
                          MyConstants.explore.search_perimeter)
        matrix_cost = section.matrix
        goal_position = get_goal_in_section(matrix_path, section.center, ship.position, target_position,
                                            directions)
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





