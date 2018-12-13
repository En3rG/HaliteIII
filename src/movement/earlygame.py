
from src.common.print import print_heading
from src.common.moves import Moves
import logging

"""
TO DO!!!!!!!!!!!


"""

class EarlyGame(Moves):
    def __init__(self, data, prev_data):
        super().__init__(data, prev_data)

        self.move_ships()

    def move_ships(self):
        print_heading("Moving early game......")

        if self.data.game.turn_number == 6:  ## SHIPS SHOULD MOVE OUT ON TURNS 2, 3, 4, 5, 6
            fifth_ship_id = list(sorted(self.data.mySets.ships_all))[-1]
            ship = self.data.game.me._ships.get(fifth_ship_id)
            #self.move_mark_unsafe(ship, direction)


