from enum import Enum
import numpy as np


class Matrix_val(Enum):
    OCCUPIED = 1
    UNSAFE = -1

    # ALLY_SHIP = -2
    # ALLY_DOCK = -3
    # ALLY_SHIPYARD = -4
    # ENEMY_SHIP = -5
    # ENEMY_DOCK = -6
    # ENEMY_SHIPYARD = -7
    # INFLUENCED = -8


class MyConstants():
    STOP_SPAWNING = 0.70    ## PERCENTAGE OF MAX TURNS TO STOP SPAWNING SHIPS

    DIRECT_NEIGHBORS_SELF = np.array([[0, 1, 0],
                                      [1, 1, 1],
                                      [0, 1, 0]])

    DIRECT_NEIGHBORS = np.array([[0,1,0],
                                 [1,0,1],
                                 [0,1,0]])





