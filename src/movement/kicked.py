from src.common.print import print_heading
from src.common.moves import Moves
import logging


class Kicked(Moves):
    def __init__(self, data, prev_data):
        super().__init__(data, prev_data)

        self.move_ships()

    def move_ships(self):
        print_heading("Moving kicked ships......")
        logging.debug("Ships kicked: {}".format(self.data.ships_kicked))