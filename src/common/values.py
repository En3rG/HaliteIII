import numpy as np
from hlt.positionals import Direction


class Inequality:
    EQUAL = "="
    GREATERTHAN = ">"
    LESSTHAN = "<"


class MoveMode():
    RETREAT = "retreat"
    DEPOSIT = "deposit"
    HARVEST = "harvest"
    EXPLORE = "explore"
    DEPART = "depart"
    BUILDING = "building"
    ATTACKING = "attacking"
    SUPPORTING = "supporting"


class Matrix_val():
    ZERO = 0
    ONE = 1
    TEN = 10                                        ## JUST USED FOR BETTER READABILITY WITH A LOT OF 0s
    OCCUPIED = -1
    UNSAFE = -1
    POTENTIAL_COLLISION = -1
    UNAVAILABLE = -1
    NINETY = 90


## ------ PARAMETERS ------
class Influence():
    def __init__(self):
        self.min_num = 2                            ## INFLUENCE NUMBER (# OF ENEMY) TO GET BONUS
        self.engage_distance = 6                    ## DISTANCE TO ENGAGE WITH ENEMY FOR INFLUENCE

class Retreat():
    def __init__(self):
        self.extra_turns = 5                        ## EXTRA TURNS ADDED TO FURTHEST SHIP WHEN TO START RETREATING
        self.search_perimeter = 5

class Build():
    def __init__(self):
        ## DOCKS
        self.top_n_halite = 0.04                    ## TOP N HALITE (PERCENTAGE OF MAX CELLS IN MAP)
        self.top_n = 20                             ## TOP N BASED ON AVERAGE MANHATTAN.  USED FOR DOCK PLACEMENT
        self.dock_manhattan = 12                    ## MANHATTAN DISTANCE OF WHEN DOCK BUILD IS EXECUTED
        self.average_manhattan_distance = 6         ## DISTANCE USED WHEN GETTING MANHATTAN AVERAGE
        self.min_dist_btw_enemy_docks = 18
        self.min_dist_btw_docks = 15                ## MINIMUM DISTANCE BETWEEN DOCKS/SHIPYARD
        self.dock_anywhere_halite = 3500
        self.dock_far_halite = 1500
        self.considered_far_distance = 10
        self.far_enemy_perimeter = 3


        ## BUILDING
        self.allowed_turns = 0.70
        self.stop_when_halite_left = 0.40
        self.min_num_ships = 10
        self.min_dock_halite_average = 0.50         ## WILL NO LONGER BUILD IF BELOW THIS PERCENTAGE, FROM ORIGINAL AVERAGE
        self.min_halite_amount = 500                ## MINIMUM HALITE AMOUNT TO GO TOWARDS BUILDING
        self.ships_per_dock_ratio = 10
        self.ships_percent = 0.15                   ## PERCENTAGE OF SHIPS ALLOWED TO BUILD (BASED ON TOTAL NUMBER OF SHIPS)
        self.ships_per_dock = 1                     ## NUMBER OF SHIPS CONSIDERED TO BUILD PER DOCK


class Deposit():
    def __init__(self):
        self.search_perimeter = 5
        self.potentially_enough_cargo = 950         ## MAYBE ENOUGH TO GO HOME
        self.over_harvest_percent = 0.85            ## ONLY TAKES PERCENTAGE OF HARVEST INTO ACCOUNT, BUT IF ITS OVER 1000 ALREADY, GO HOME
        self.enemy_check_manhattan = 3
        self.enemy_check_num = 3
        self.harvest_above_percentile = 40
        self.harvest_min = 0

class Harvest():
    def __init__(self):
        self.ratio_to_explore_2p = 3                ## IF EXPLORE RATIO IS THIS MUCH GREATER THAN HARVEST RATIO, DONT HARVEST
        self.ratio_to_explore_4p = 3
        self.harvest_above_percentile = 40
        self.enable_bonus_turns_above = 0.00        ## WHEN TO SWITCH WITH HARVEST+BONUS FOR HARVEST LATER
                                                    ## 0 MEANS ALWAYS WILL USE IT

class Attack():
    def __init__(self):
        ## ATTACKING
        self.enemy_backup_distance = 2
        self.engage_enemy_distance = 3              ## DISTANCE TO ENGAGE WITH ENEMY
        self.min_ships_before_attacking = 0
        self.allowed_turns_upper_limit = 0.95
        self.allowed_turns_lower_limit = 0.00

        ## SUPPORT
        self.support_gain_ratio_2p = 0.70
        self.support_gain_ratio_4p = 1.00

        ## KAMIKAZE
        self.kamikaze_halite_ratio_2p = 0.00
        self.kamikaze_halite_ratio_4p = 1.25
        self.kamikaze_halite_max = 800
        self.kamikaze_retreat_distance = 2

class Snipe():
    def __init__(self):
        self.ratio_to_snipe = 5
        self.allowed_turns_upper_limit = 0.95
        self.allowed_turns_lower_limit = 0.70
        self.killing_spree_halite_left = 0.50
        self.killing_spree_halite_ratio = 1.25

class Explore():
    def __init__(self):
        self.search_perimeter = 5
        self.average_manhattan_distance = 3
        self.enable_bonus_halite_left = 0.25
        self.enable_bonus_turns_above = 0.25        ## WHEN TO SWITCH WITH HARVEST+BONUS FOR EXPLORING
                                                    ## 1 MEANS NEVER WILL USE IT
        self.score_harvest_ratio = 0.90
        self.score_average_ratio = 0.10

class Spawn():
    def __init__(self):
        self.stop_halite_left = 0.40
        self.max_allowed_turn_2p = 0.75
        self.max_allowed_turn_4p = 0.68
        self.percent_more_ships = 1.10

        ## DECAY (NO LONGER USED)
        self.depleted_ratio = 0.10                  ## RATIO OF HALITE LEFT WHEN ITS CONSIDERED DEPLETED (SINCE IT NEVER BE 0)
        self.num_rate_of_decay = 20
        self.min_turn_percent = 0.35
        self.max_turn_percent = 0.70

class MyConstants():
    retreat = Retreat()
    build = Build()
    deposit = Deposit()
    harvest = Harvest()
    attack = Attack()
    influence = Influence()
    snipe = Snipe()
    explore = Explore()
    spawn = Spawn()

    ## DIRECTIONS
    DIRECTIONS = [Direction.North, Direction.East, Direction.South, Direction.West]
    ALL_DIRECTIONS = [Direction.North, Direction.East, Direction.South, Direction.West, Direction.Still]

    ## DISTANCES
    DIRECT_NEIGHBOR_DISTANCE = 1


    ## NO LONGER USED
    # DONT_HARVEST_PERCENT = .12  ## PERCENTAGE OF AVERAGE HALITE TO NOT HARVEST
    #                             ## USED TO BE:
    #                             ## V14: 0.12
    #
    # SECTION_SIZE = 4  ## SIZE OF EACH SECTIONS
    #
    # DONT_HARVEST_BELOW = 5  ## DONT HARVEST BELOW THIS NUMBER (USED TO BE 5 FOR V6 BELOW)
    # HARVEST_AREA_PERCENT = 0.60  ## 60%, HARVEST AREA THAT IS NOT TOP 40% TO HARVEST
    #
    # ## (BASED ON NUMBER OF TURNS REQUIRED TO HARVEST THE CELL)
    # EARLY_GAME_TURNS = 80  ## TURNS CONSIDERED AT EARLY GAME
    # TOP_N_HALITE_EARLY_GAME = 0.20  ## PERCENTAGE OF TOP HALITE USED IN EARLY GAME
    #
    # DIRECT_NEIGHBORS_SELF = np.array([[0, 1, 0],
    #                                   [1, 1, 1],
    #                                   [0, 1,0]])
    #
    # DIRECT_NEIGHBORS = np.array([[0,1,0],
    #                              [1,0,1],
    #                              [0,1,0]])
    #
    #
    #
    # ATTACK_ENEMY_HALITE_RATIO = 0.5  ## ONLY ATTACK ENEMY IF OUR SHIP HALITE HAS LESS THAN THE RATIO
    #
    # ALLOW_SPAWNING_2P_32_TURNS = 0.70
    # ALLOW_SPAWNING_2P_40_TURNS = 0.70
    # ALLOW_SPAWNING_2P_48_TURNS = 0.75
    # ALLOW_SPAWNING_2P_56_TURNS = 0.75
    # ALLOW_SPAWNING_2P_64_TURNS = 0.75
    # ALLOW_SPAWNING_4P_32_TURNS = 0.40
    # ALLOW_SPAWNING_4P_40_TURNS = 0.45
    # ALLOW_SPAWNING_4P_48_TURNS = 0.50
    # ALLOW_SPAWNING_4P_56_TURNS = 0.55
    # ALLOW_SPAWNING_4P_64_TURNS = 0.60




