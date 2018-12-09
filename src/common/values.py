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
    TEN = 10                        ## JUST USED FOR BETTER READABILITY WITH A LOT OF 0s
    OCCUPIED = -1
    UNSAFE = -1
    POTENTIAL_COLLISION = -1


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
    STOP_BUILDING_TURNS_LEFT = 0.70
    STOP_BUILDING_HALITE_LEFT = 0.30
    NUM_SHIPS_BEFORE_BUILDING = 10

    DOCK_MANHATTAN = 1                              ## 0 MEANS JUST ITSELF, 1 MEANS INCLUDING ITS DIRECT NEIGHBORS
    AVERAGE_MANHATTAN_DISTANCE = 6                  ## DISTANCE USED WHEN GETTING MANHATTAN AVERAGE
    TOP_N = 20                                      ## TOP N BASED ON AVERAGE MANHATTAN.  USED FOR DOCK PLACEMENT
                                                    ## USED TO BE:
                                                    ## V19: 20
    MIN_DIST_BTW_DOCKS = 12                         ## MINIMUM DISTANCE BETWEEN DOCKS/SHIPYARD
                                                    ## USED TO BE:
                                                    ## V19: 12


    ## ATTACKING
    ENGAGE_ENEMY_DISTANCE = 3                       ## DISTANCE TO ENGAGE WITH ENEMY
    NUM_SHIPS_BEFORE_ATTACKING = 20
    ATTACK_ENEMY_HALITE_RATIO = 0.5                 ## ONLY ATTACK ENEMY IF OUR SHIP HALITE HAS LESS THAN THE RATIO
    ATTACK_TURNS_LEFT = 0.80


    ## HARVEST
    ## THE HIGHER THE NUMBER, THE MORE TUNNELING EFFECT IT'LL HAVE
    ## AND WILL HARVEST SMALLER AREAS LATER
    DONT_HARVEST_PERCENT = .12                      ## PERCENTAGE OF AVERAGE HALITE TO NOT HARVEST
                                                    ## USED TO BE:
                                                    ## V14: 0.12


    ## EXPLORING
    ## TOP N HALITE (PERCENTAGE OF MAX CELLS IN MAP)
    TOP_N_HALITE = 0.04                             ## USED TO BE:
                                                    ## V13: 0.10
                                                    ## V14: 0.04

    ENABLE_TOP_HARVEST_TURNS_LEFT = 0.8             ## SWTICH TO TOP HARVEST FROM TOP HALITE (FOR EXPLORING)


    ## SPAWNING
    STOP_SPAWNING_HALITE_LEFT = 0.40

    STOP_SPAWNING_2P_32_TURNS_LEFT = 0.60
    STOP_SPAWNING_2P_40_TURNS_LEFT = 0.62
    STOP_SPAWNING_2P_48_TURNS_LEFT = 0.64
    STOP_SPAWNING_2P_56_TURNS_LEFT = 0.66
    STOP_SPAWNING_2P_64_TURNS_LEFT = 0.65
    STOP_SPAWNING_4P_32_TURNS_LEFT = 0.40
    STOP_SPAWNING_4P_40_TURNS_LEFT = 0.45
    STOP_SPAWNING_4P_48_TURNS_LEFT = 0.50
    STOP_SPAWNING_4P_56_TURNS_LEFT = 0.55
    STOP_SPAWNING_4P_64_TURNS_LEFT = 0.60


    ## NO LONGER USED
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







