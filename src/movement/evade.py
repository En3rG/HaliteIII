from src.common.move.moves import Moves
from src.common.move.harvests import Harvests
from src.common.print import print_heading
from src.common.orderedSet import OrderedSet
from src.common.values import MyConstants
from src.common.points import ExploreShip
from src.common.values import MoveMode, Matrix_val
from src.common.move.explores import Explores
from hlt import constants
import heapq
import logging
import copy
import numpy as np



class Evade(Moves, Harvests, Explores):
    """
    MOVE HIGH CARGO SHIPS AWAY FROM ENEMY (IF ALONE)
    """
    def __init__(self, data, prev_data):
        Moves.__init__(self, data, prev_data)

        self.move_ships()

    def move_ships(self):
        print_heading("Moving Evading ships......")









