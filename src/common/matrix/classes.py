import numpy as np
from src.common.values import MyConstants, Matrix_val, Inequality
from src.common.orderedSet import OrderedSet

class Option():
    """
    USED FOR POPULATE MANHATTAN OPTIONS
    """
    REPLACE = "replace"
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
        self.halite = np.zeros((map_height, map_width), dtype=np.float16)                                               ## WILL CONTAIN THE AVERAGE OF EACH CELL
        self.top_N = np.zeros((map_height, map_width), dtype=np.float16)                                                ## WILL CONTAIN AVERAGE OF TOP N LOCATIONS
        self.enemyCargo = np.zeros((map_height, map_width), dtype=np.float16)


class Halite():
    def __init__(self, map_height, map_width):
        self.amount = np.zeros((map_height, map_width), dtype=np.int16)
        self.updated_amount = np.zeros((map_height, map_width), dtype=np.int16)
        self.top_amount = np.zeros((map_height, map_width), dtype=np.int16)
        self.cost = None
        self.harvest = None
        self.updated_harvest = None
        self.bonus = np.zeros((map_height, map_width), dtype=np.int16)
        self.harvest_with_bonus = None
        self.updated_harvest_with_bonus = None
        self.enemyCargo = np.zeros((map_height, map_width), dtype=np.float16)                                           ## CAUSES AN ERROR WHEN INT16
        self.updated_enemyCargo = np.zeros((map_height, map_width), dtype=np.float16)
        self.enemyCargo_harvest = np.zeros((map_height, map_width), dtype=np.float16)
        self.updated_enemyCargo_harvest = np.zeros((map_height, map_width), dtype=np.float16)
        self.enemyCargo_harvest_with_bonus = np.zeros((map_height, map_width), dtype=np.float16)
        self.updated_enemyCargo_harvest_with_bonus = np.zeros((map_height, map_width), dtype=np.float16)


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
        self.updated_myShipsID = np.zeros((map_height, map_width), dtype=np.int16)
        self.updated_myShipsID.fill(-1)
        self.sunken_ships = np.zeros((map_height, map_width), dtype=np.int16)
        self.enemyShips = np.zeros((map_height, map_width), dtype=np.int16)
        self.enemyShipsID = np.zeros((map_height, map_width), dtype=np.int16)
        self.enemyShipsID.fill(-1)
        self.enemyShipsOwner = np.zeros((map_height, map_width), dtype=np.int16)
        self.enemyShipsOwner.fill(-1)
        self.shipsCargo = np.zeros((map_height, map_width), dtype=np.int16)

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



class Distances():
    """
    CONTAINS DISTANCES MATRIXES
    """
    def __init__(self, map_height, map_width):
        self.cell = {}                                                                                                  ## KEY IS COORD, VALUE IS DISTANCE MATRIX.  ONLY FILLED IN INITIALIZATION
        self.closest_dock = None                                                                                        ## WILL BE A MATRIX REPRESENTING THE DISTANCE OF THE CLOSEST DOCK

class Docks():
    def __init__(self, map_height, map_width):
        self.averages = np.zeros((map_height, map_width), dtype=np.int16)                                               ## THE AVERAGE VALUE OF THE SURROUNDING AREA
        self.placement = np.zeros((map_height, map_width), dtype=np.int16)                                              ## WHERE THE DOCK WILL BE BUILT
        self.manhattan = np.zeros((map_height, map_width), dtype=np.int16)                                              ## IDENTIFIES THE SURROUNDING OF THE DOCKS, SO SHIP GRAVITATES TOWARDS IT
        self.order = np.zeros((map_height, map_width), dtype=np.int16)
        self.order.fill(Matrix_val.NINETY)

class Matrix():
    """
    CONTAINS ALL THE MATRICES
    """
    def __init__(self, map_height, map_width):
        self.halite = Halite(map_height, map_width)
        self.distances = Distances(map_height, map_width)
        self.locations = Locations(map_height, map_width)
        self.cell_average = CellAverage(map_height, map_width)
        self.docks = Docks(map_height, map_width)

        ## NO LONGER USED
        # self.sectioned = Sectioned(map_height, map_width)
        # self.depletion = Depletion(map_height, map_width)


class MySets():
    def __init__(self, game):
        self.ships_all = OrderedSet(sorted(game.me._ships.keys()))                                                      ## ALL SHIPS
        self.ships_to_move = OrderedSet(sorted(game.me._ships.keys()))                                                  ## SHIPS TO MOVE (SORTING TO MATCH ORDER ONLINE)
        self.ships_returning = OrderedSet()                                                                             ## SHIPS RETURNING HALITE
        self.ships_kicked = OrderedSet()
        self.ships_died = set()
        self.ships_ally_collision = set()
        self.ships_enemy_collision = set()
        self.ships_building = set()
        self.dock_coords = set()
        self.deposit_ships = OrderedSet()


class MyVars():
    def __init__(self, data, game):
        self.ratio_left_halite = 0
        self.total_halite = 0
        self.average_halite = 0
        self.median_halite = 0
        self.harvest_percentile = 0
        self.isBuilding = False
        self.isSaving = False
        self.support_gain_ratio = MyConstants.SUPPORT_GAIN_RATIO_2P if (len(game.players) == 2) \
                                    else MyConstants.SUPPORT_GAIN_RATIO_4P                                              ## RATIO OF GAIN BEFORE SUPPORTING
        self.kamikaze_halite_ratio = MyConstants.KAMIKAZE_HALITE_RATIO_2P if (len(game.players) == 2) \
                                    else MyConstants.KAMIKAZE_HALITE_RATIO_4P
        self.explore_disable_bonus = None


class MyDicts():
    def __init__(self):
        self.players_info = {}              ## KEY IS PLAYER ID, VALUE IS PlayerInfo
        self.positions_taken = {}           ## KEY IS COORD, VALUE IS SHIP ID
        self.explore_ship = {}              ## KEY IS SHIP ID, VALUE IS AN ExploreShip
        self.deposit_ship = {}              ## KEY IS SHIP ID, VALUE IS AN FarthestShip
        self.snipe_ship = {}                ## KEY IS SHIP ID, VALUE IS AN ExploreShip
        self.ships_building_dock = {}       ## KEY IS DOCK COORD, VALUES ARE SHIP IDs BUILDING THERE

class MyLists():
    def __init__(self, data):
        self.explore_target = []
        self.snipe_target = []
        self.ratio_left_halite = []


class PlayerInfo():
    def __init__(self):
        self.halite_amount = 0
        self.halite_carried = 0
        self.num_ships = 0

    def __repr__(self):
        return "{} halite_amount {} halite_carried {} num_ships {}".format(self.__class__.__name__,
                         self.halite_amount,
                         self.halite_carried,
                         self.num_ships)



