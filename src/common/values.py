from enum import Enum
import numpy as np

class DirectionHomeMode():
    RETREAT = "retreat"
    DEPOSIT = "deposit"


class Matrix_val():
    OCCUPIED = 1
    UNSAFE = -1
    POTENTIAL_COLLISION = -1

class MyConstants():
    DIRECT_NEIGHBOR_RADIUS = 1  ## DISTANCE OF DIRECT NEIGHBOR
    STOP_SPAWNING = 0.70        ## PERCENTAGE OF MAX TURNS TO STOP SPAWNING SHIPS

    DIRECT_NEIGHBORS_SELF = np.array([[0, 1, 0],
                                      [1, 1, 1],
                                      [0, 1, 0]])

    DIRECT_NEIGHBORS = np.array([[0,1,0],
                                 [1,0,1],
                                 [0,1,0]])





