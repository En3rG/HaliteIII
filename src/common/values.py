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


class Matrix_val():
    ZERO = 0
    ONE = 1
    TEN = 10                        ## JUST USED FOR BETTER READABILITY WITH A LOT OF 0s
    OCCUPIED = -1
    UNSAFE = -1
    POTENTIAL_COLLISION = -1


class MyConstants():
    EXTRA_TURNS_RETREAT = 5         ## EXTRA TURNS ADDED TO FURTHEST SHIP WHEN TO START RETREATING

    DIRECT_NEIGHBOR_RADIUS = 1      ## DISTANCE OF DIRECT NEIGHBOR

    STOP_SPAWNING_2P = 0.60         ## PERCENTAGE OF MAX TURNS WHEN TO STOP SPAWNING SHIPS
    STOP_SPAWNING_4P = 0.40         ## FOR 4 PLAYERS

    INFLUENCED = 2                  ## INFLUENCE NUMBER (# OF ENEMY) TO GET BONUS

    SECTION_SIZE = 4                ## SIZE OF EACH SECTIONS

    DONT_HARVEST_PERCENT = .05      ## PERCENTAGE OF AVERAGE HALITE TO NOT HARVEST
    DONT_HARVEST_BELOW = 5         ## DONT HARVEST BELOW THIS NUMBER (USED TO BE 5 FOR V6 BELOW)
    HARVEST_AREA_PERCENT = 0.60     ## 60%, HARVEST AREA THAT IS NOT TOP 40% TO HARVEST
                                    ##   (BASED ON NUMBER OF TURNS REQUIRED TO HARVEST THE CELL)

    TOP_N_HALITE = 0.10             ## TOP N HALITE (PERCENTAGE OF MAX CELLS IN MAP) USED TO BE .10 FOR V6 BELOW

    AVERAGE_MANHATTAN_DISTANCE = 6  ## DISTANCE USED WHEN GETTING MANHATTAN AVERAGE
    TOP_N = 20                      ## TOP N BASED ON AVERAGE MANHATTAN

    MIN_DIST_BTW_DOCKS = 12         ## MINIMUM DISTANCE BETWEEN DOCKS/SHIPYARD (12 for V7)


    DIRECT_NEIGHBORS_SELF = np.array([[0, 1, 0],
                                      [1, 1, 1],
                                      [0, 1,0]])

    DIRECT_NEIGHBORS = np.array([[0,1,0],
                                 [1,0,1],
                                 [0,1,0]])

    DIRECTIONS = [ Direction.North, Direction.East, Direction.South, Direction.West ]





