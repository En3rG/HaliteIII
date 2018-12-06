from src.common.print import print_heading
from src.common.moves import Moves


"""
TO DO!!!!!!!!!!!!

BLOCK ENEMY DOCKS


TRY TO NOT INFLUENCE ENEMY IF POSSIBLE


"""


class Attack(Moves):
    def __init__(self, data, prev_data):
        super().__init__(data, prev_data)

        self.move_ships()

    def move_ships(self):
        print_heading("Moving attack ships......")