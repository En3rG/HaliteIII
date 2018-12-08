from src.common.print import print_heading
from src.common.moves import Moves
from src.common.values import MyConstants, Matrix_val
import numpy as np

"""
TO DO!!!!!!!!!!!!

BLOCK ENEMY DOCKS

ONLY ATTACK WHEN THERES SUPPORT
DONT ATTACK WHEN HAVE HIGH CARGO


TRY TO NOT INFLUENCE ENEMY IF POSSIBLE


"""


class Attack(Moves):
    def __init__(self, data, prev_data):
        super().__init__(data, prev_data)

        self.move_ships()

    def move_ships(self):
        print_heading("Moving attack ships......")

        if self.data.myVars.canAttack and len(self.data.mySets.ships_all) > MyConstants.NUM_SHIPS_BEFORE_ATTACKING:
            r, c = np.where(self.data.myMatrix.locations.engage_enemy == Matrix_val.ONE)
