import numpy as np
from hlt.positionals import Direction

class MoveMode():
    RETREAT = "retreat"
    DEPOSIT = "deposit"
    HARVEST = "harvest"
    EXPLORE = "explore"


class Matrix_val():
    OCCUPIED = 1
    UNSAFE = -1
    POTENTIAL_COLLISION = -1


class MyConstants():
    DIRECT_NEIGHBOR_RADIUS = 1      ## DISTANCE OF DIRECT NEIGHBOR
    STOP_SPAWNING = 0.70            ## PERCENTAGE OF MAX TURNS TO STOP SPAWNING SHIPS
    INFLUENCED = 2                  ## INFLUENCE NUMBER (ENEMY) TO GET BONUS
    DONT_HARVEST_BELOW = 5          ## DONT HARVEST BELOW THIS NUMBER
    SECTION_SIZE = 4
    AVERAGE_MANHATTAN_DISTANCE = 1  ## DISTANCE USED WHEN GETTING MANHATTAN AVERAGE

    DIRECT_NEIGHBORS_SELF = np.array([[0, 1, 0],
                                      [1, 1, 1],
                                      [0, 1, 0]])

    DIRECT_NEIGHBORS = np.array([[0,1,0],
                                 [1,0,1],
                                 [0,1,0]])

    DIRECTIONS = [ Direction.North, Direction.East, Direction.South, Direction.West ]





