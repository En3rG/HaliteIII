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
    MAXSTART = "maxstart"
    MINSTART = "minstart"


class Matrix_val():
    ZERO = 0
    ONE = 1
    TEN = 10                        ## JUST USED FOR BETTER READABILITY WITH A LOT OF 0s
    OCCUPIED = -1
    UNSAFE = -1
    POTENTIAL_COLLISION = -1
    UNAVAILABLE = -1


class MyConstants():

    ## DIRECTIONS
    DIRECTIONS = [Direction.North, Direction.East, Direction.South, Direction.West]

    ## DISTANCES
    DIRECT_NEIGHBOR_DISTANCE = 1

    ## ENEMY
    INFLUENCED = 2                                  ## INFLUENCE NUMBER (# OF ENEMY) TO GET BONUS

    ## RETREAT
    RETREAT_EXTRA_TURNS = 5                         ## EXTRA TURNS ADDED TO FURTHEST SHIP WHEN TO START RETREATING

    ## BUILDING / DOCK PLACEMENT
    ALLOW_BUILDING_TURNS = 0.70                     ## USED TO BE:
                                                    ## V28: 0.70
    STOP_BUILDING_HALITE_LEFT = 0.30
    NUM_SHIPS_BEFORE_BUILDING = 10

    SHIPS_BUILDING_PERCENT = 0.25                   ## PERCENTAGE OF SHIPS ALLOWED TO BUILD (BASED ON TOTAL NUMBER OF SHIPS)
    SHIPS_BUILDING_PER_DOCK = 3                     ## NUMBER OF SHIPS CONSIDERED TO BUILD PER DOCK
    DOCK_MANHATTAN = 7                              ## MANHATTAN DISTANCE OF WHEN DOCK BUILD IS EXECUTED
                                                    ## USED TO BE:
                                                    ## V28: 2
    AVERAGE_MANHATTAN_DISTANCE = 6                  ## DISTANCE USED WHEN GETTING MANHATTAN AVERAGE
    TOP_N = 20                                      ## TOP N BASED ON AVERAGE MANHATTAN.  USED FOR DOCK PLACEMENT
                                                    ## USED TO BE:
                                                    ## V19: 20
    MIN_DIST_BTW_DOCKS = 12                         ## MINIMUM DISTANCE BETWEEN DOCKS/SHIPYARD
                                                    ## USED TO BE:
                                                    ## V19: 12


    ## ATTACKING
    SUPPORT_GAIN_RATIO = 1.20                       ## RATIO OF GAIN BEFORE SUPPORTING
    ENGAGE_ENEMY_DISTANCE = 3                       ## DISTANCE TO ENGAGE WITH ENEMY
    NUM_SHIPS_BEFORE_ATTACKING = 20
    ATTACK_ENEMY_HALITE_RATIO = 0.5                 ## ONLY ATTACK ENEMY IF OUR SHIP HALITE HAS LESS THAN THE RATIO
    ALLOW_ATTACK_TURNS = 0.80                       ## 0 MEANS NEVER ATTACKING
                                                    ## USED TO BE:
                                                    ## V28: 0.80



    ## HARVEST
    ## THE HIGHER THE NUMBER, THE MORE TUNNELING EFFECT IT'LL HAVE
    ## AND WILL HARVEST SMALLER AREAS LATER
    HARVEST_ABOVE_PERCENTILE = 35                   ## USED TO BE:
                                                    ## V28: 35


    ## EXPLORING
    ## TOP N HALITE (PERCENTAGE OF MAX CELLS IN MAP)
    TOP_N_HALITE = 0.04                             ## USED TO BE:
                                                    ## V13: 0.10
                                                    ## V14: 0.04


    EXPLORE_ENABLE_WITH_BONUS_TURNS_ABOVE = 1.00    ## WHEN TO SWITCH WITH HARVEST+BONUS FOR EXPLORING
                                                    ## 1 MEANS NEVER WILL USE IT
    HARVEST_ENABLE_WITH_BONUS_TURNS_ABOVE = 0.00    ## WHEN TO SWITCH WITH HARVEST+BONUS FOR HARVEST LATER
                                                    ## 0 MEANS ALWAYS WILL USE IT

    ## SPAWNING
    STOP_SPAWNING_HALITE_LEFT = 0.40                ## USED TO BE:
                                                    ## V28: 0.40
    ALLOW_SPAWNING_2P_32_TURNS = 0.60
    ALLOW_SPAWNING_2P_40_TURNS = 0.62
    ALLOW_SPAWNING_2P_48_TURNS = 0.64
    ALLOW_SPAWNING_2P_56_TURNS = 0.66
    ALLOW_SPAWNING_2P_64_TURNS = 0.68
    ALLOW_SPAWNING_4P_32_TURNS = 0.40
    ALLOW_SPAWNING_4P_40_TURNS = 0.45
    ALLOW_SPAWNING_4P_48_TURNS = 0.50
    ALLOW_SPAWNING_4P_56_TURNS = 0.55
    ALLOW_SPAWNING_4P_64_TURNS = 0.60


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







