from src.common.print import print_heading
from src.common.move.moves import Moves


class Harass(Moves):
    def __init__(self, data, prev_data):
        Moves.__init__(self, data, prev_data)

        self.move_ships()

    def move_ships(self):
        print_heading("Moving harass ships......")