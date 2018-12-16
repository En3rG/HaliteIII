
from src.common.print import print_heading
from src.common.move.moves import Moves
from src.common.move.starts import Starts
from src.common.values import MoveMode, MyConstants


"""
TO DO!!!!!!!!!!!


"""

class Start(Moves, Starts):
    def __init__(self, data, prev_data):
        Moves.__init__(self, data, prev_data)

        self.move_ships()

    def move_ships(self):
        print_heading("Moving early game......")

        if self.data.game.turn_number <= 6:  ## SHIPS SHOULD MOVE OUT ON TURNS 2, 3, 4, 5, 6
            if self.data.game.turn_number == 6:
                new_ship_id = list(sorted(self.data.mySets.ships_all))[-1]
                ship = self.data.game.me._ships.get(new_ship_id)
                direction, points = self.best_direction(ship, mode=MoveMode.MINSTART)
                self.move_mark_unsafe(ship, direction, points)
            elif len(self.data.mySets.ships_all) >= 1:
                out_ship_id = list(sorted(self.data.mySets.ships_all))[-1]
                ship = self.data.game.me._ships.get(out_ship_id)
                direction, points = self.best_direction(ship, mode=MoveMode.MAXSTART)
                self.move_mark_unsafe(ship, direction, points)




