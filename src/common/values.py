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

    STOP_SPAWNING = 0.60            ## PERCENTAGE OF MAX TURNS WHEN TO STOP SPAWNING SHIPS

    INFLUENCED = 2                  ## INFLUENCE NUMBER (# OF ENEMY) TO GET BONUS

    SECTION_SIZE = 4                ## SIZE OF EACH SECTIONS

    DONT_HARVEST_BELOW = 5          ## DONT HARVEST BELOW THIS NUMBER
    HARVEST_AREA_PERCENT = 0.60     ## 60%, HARVEST AREA THAT IS NOT TOP 40% TO HARVEST
                                    ##   (BASED ON NUMBER OF TURNS REQUIRED TO HARVEST THE CELL)

    TOP_N_HALITE = 0.10             ## TOP N HALITE (PERCENTAGE OF MAX CELLS IN MAP)

    AVERAGE_MANHATTAN_DISTANCE = 6  ## DISTANCE USED WHEN GETTING MANHATTAN AVERAGE
    TOP_N = 20                      ## TOP N BASED ON AVERAGE MANHATTAN

    DIRECT_NEIGHBORS_SELF = np.array([[0, 1, 0],
                                      [1, 1, 1],
                                      [0, 1,0]])

    DIRECT_NEIGHBORS = np.array([[0,1,0],
                                 [1,0,1],
                                 [0,1,0]])

    DIRECTIONS = [ Direction.North, Direction.East, Direction.South, Direction.West ]





