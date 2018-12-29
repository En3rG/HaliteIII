import numpy as np
from src.common.values import MyConstants, Matrix_val, Inequality
from src.common.orderedSet import OrderedSet


class Option():
    """
    USED FOR POPULATE MANHATTAN OPTIONS
    """
    REGULAR = "regular"
    CUMMULATIVE = "cummulative"
    MINIMUM = "minimum"
    MAXIMUM = "maximum"


class CellAverage():
    """
    USED TO GET THE AVERAGE HALITE PER CELL IN THE MAP
    BASED ON THE MANHATTAN DISTANCE DEFINED IN COMMON VALUES
    USED FOR DOCK PLACEMENT
    """
    def __init__(self, map_height, map_width):
        self.manhattan = np.zeros((map_height, map_width), dtype=np.float16)
        self.top_N = np.zeros((map_height, map_width), dtype=np.float16)


class Halite():
    def __init__(self, map_height, map_width):
        self.amount = np.zeros((map_height, map_width), dtype=np.int16)
        self.top_amount = np.zeros((map_height, map_width), dtype=np.int16)
        self.cost = None
        self.harvest = None
        self.bonus = np.zeros((map_height, map_width), dtype=np.int16)
        self.harvest_with_bonus = None


class Locations():
    def __init__(self, map_height, map_width):
        ## SHIPYARDS
        self.myShipyard = np.zeros((map_height, map_width), dtype=np.int16)
        self.enemyShipyard = np.zeros((map_height, map_width), dtype=np.int16)

        ## SHIPYARDS/DOCKS
        self.myDocks = np.zeros((map_height, map_width), dtype=np.int16)
        self.enemyDocks = np.zeros((map_height, map_width), dtype=np.int16)

        ## SHIPS
        self.myShips = np.zeros((map_height, map_width), dtype=np.int16)
        self.myShipsID = np.zeros((map_height, map_width), dtype=np.int16)
        self.myShipsID.fill(-1)                                                                                         ## CANT FIND SHIP ID 0 IF ZEROES
        self.enemyShips = np.zeros((map_height, map_width), dtype=np.int16)
        self.enemyShipsID = np.zeros((map_height, map_width), dtype=np.int16)
        self.enemyShipsID.fill(-1)
        self.enemyShipsOwner = np.zeros((map_height, map_width), dtype=np.int16)
        self.enemyShipsOwner.fill(-1)
        self.shipsCargo = np.zeros((map_height, map_width), dtype=np.int16)
        self.enemyCargo = np.zeros((map_height, map_width), dtype=np.float16)                                           ## CAUSES AN ERROR WHEN INT16

        ## ATTACK
        self.engage_enemy = {}
        for i in range(1, MyConstants.ENGAGE_ENEMY_DISTANCE + 1):                                                       ## WHEN i IS 1, MEANS RIGHT NEXT TO ENEMY
            self.engage_enemy[i] = np.zeros((map_height, map_width), dtype=np.int16)

        self.engage_influence = np.zeros((map_height, map_width), dtype=np.int16)

        self.influenced = np.zeros((map_height, map_width), dtype=np.int16)

        self.stuck = np.zeros((map_height, map_width), dtype=np.int16)

        self.safe = np.zeros((map_height, map_width), dtype=np.int16)
        self.safe.fill(1)                                                                                               ## FILLED WITH 1, -1 FOR UNSAFE

        ## OCCUPIED IS DIFFERENT FROM MYSHIPS LOCATIONS BECAUSE IT GETS UPDATED
        ## AS THE SHIP MOVES, WHERE AS MYSHIPS IS THE STARTING LOCATIONS OF THE SHIPS
        self.occupied = np.zeros((map_height, map_width), dtype=np.int16)

        self.potential_ally_collisions = np.zeros((map_height, map_width), dtype=np.int16)
        self.potential_enemy_collisions = np.zeros((map_height, map_width), dtype=np.int16)
        self.potential_enemy_cargo = np.zeros((map_height, map_width), dtype=np.int16)

        self.dock_placement = np.zeros((map_height, map_width), dtype=np.int16)


class Distances():
    """
    CONTAINS DISTANCES MATRIXES
    """
    def __init__(self, map_height, map_width):
        self.cell = {}                                                                                                  ## ONLY FILLED IN INIT
        self.closest_dock = None


class Matrix():
    """
    CONTAINS ALL THE MATRICES
    """
    def __init__(self, map_height, map_width):
        self.halite = Halite(map_height, map_width)
        self.distances = Distances(map_height, map_width)
        self.locations = Locations(map_height, map_width)
        self.cell_average = CellAverage(map_height, map_width)
        self.dock_averages = np.zeros((map_height, map_width), dtype=np.int16)

        ## NO LONGER USED
        # self.sectioned = Sectioned(map_height, map_width)
        # self.depletion = Depletion(map_height, map_width)


class MySets():
    def __init__(self, game):
        self.ships_all = OrderedSet(game.me._ships.keys())                                                              ## ALL SHIPS
        self.ships_to_move = OrderedSet(sorted(game.me._ships.keys()))                                                  ## SHIPS TO MOVE (SORTING TO MATCH ORDER ONLINE)
        self.ships_returning = OrderedSet()                                                                             ## SHIPS RETURNING HALITE
        self.ships_kicked = OrderedSet()
        self.ships_died = set()
        self.ships_ally_collision = set()
        self.ships_enemy_collision = set()
        self.ships_building = set()
        self.dock_coords = set()


class MyVars():
    def __init__(self, data, game):
        self.ratio_left_halite = 0
        self.total_halite = 0
        self.average_halite = 0
        self.median_halite = 0
        self.harvest_percentile = 0
        self.isBuilding = False
        self.dontSpawn = False
        self.support_gain_ratio = MyConstants.SUPPORT_GAIN_RATIO_2P if (len(game.players) == 2) \
                                    else MyConstants.SUPPORT_GAIN_RATIO_4P                                              ## RATIO OF GAIN BEFORE SUPPORTING


class MyDicts():
    def __init__(self):
        self.players_halite = {}
        self.positions_taken = {}
        self.explore_ship = {}
        self.explore_enemy_ship = {}
        self.ships_building_dock = {}

class MyLists():
    def __init__(self):
        self.explore_target = []
        self.enemy_target = []


class HaliteInfo():
    def __init__(self):
        self.halite_amount = 0
        self.halite_carried = 0


