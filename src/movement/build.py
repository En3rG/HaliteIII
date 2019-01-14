from src.common.print import print_heading, print_matrix
from src.common.move.moves import Moves
from src.common.move.builds import Builds
from src.common.values import MyConstants
from hlt import constants
from src.common.orderedSet import OrderedSet
import numpy as np
import logging


"""
TO DO!!!!!111

BEST TO HAVE DOCKS CLOSE TO ENEMY AND GAIN ALOT OF INFLUENCE

DONT BUILD DOCK WHEN AREA HAS BEEN HARVESTED


ADD BUILD DOCK WHEN CLOSE ENOUGH TO DOCK PLACEMENT AND FULL, BUILD RATHER THAN GO HOME



"""

class Build(Moves, Builds):
    def __init__(self, data, prev_data):
        Moves.__init__(self, data, prev_data)

        self.move_ships()

        if self.data.myVars.isBuilding:
            self.data.forecast_distance_docks()
        # self.data.forecast_distance_docks()


    def move_ships(self):
        print_heading("Moving build (dock) ships......")

        allowBuild = self.data.game.turn_number <= constants.MAX_TURNS * MyConstants.build.allowed_turns \
                                 and self.data.myVars.ratio_left_halite > MyConstants.build.stop_when_halite_left \
                                 and len(self.data.mySets.ships_all) > MyConstants.build.min_num_ships

        if allowBuild:
            self.building_now()
            self.building_later()
            self.go_towards_building()





