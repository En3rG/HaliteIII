from src.common.print import print_heading, print_matrix
from src.common.move.moves import Moves
from src.common.move.builds import Builds
from src.common.values import MyConstants
from hlt import constants


"""
TO DO!!!!!111

BEST TO HAVE DOCKS CLOSE TO ENEMY AND GAIN ALOT OF INFLUENCE

DONT BUILD DOCK WHEN AREA HAS BEEN HARVESTED


ADD BUILD DOCK WHEN CLOSE ENOUGH TO DOCK PLACEMENT AND FULL, BUILD RATHER THAN GO HOME



"""

class Build(Moves, Builds):
    def __init__(self, data, prev_data):
        Moves.__init__(self, data, prev_data)

        self.ships_building_towards_dock = {} ## KEY AS DOCK COORD, VALUES ARE SHIP IDs GOING THERE
        self.move_ships()


    def move_ships(self):
        print_heading("Moving build (dock) ships......")

        allowBuild = self.data.game.turn_number <= constants.MAX_TURNS * MyConstants.ALLOW_BUILDING_TURNS \
                                 and self.data.myVars.ratio_left_halite > MyConstants.STOP_BUILDING_HALITE_LEFT \
                                 and len(self.data.mySets.ships_all) > MyConstants.NUM_SHIPS_BEFORE_BUILDING

        if allowBuild:
            self.building_now()
            self.building_later()
            self.go_towards_building()


