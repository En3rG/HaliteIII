from src.common.print import print_heading
from src.common.movement import Moves


class Attack(Moves):
    def __init__(self, data, prev_data, command_queue, halite_stats, ):
        super().__init__(data, prev_data, halite_stats)
        self.command_queue = command_queue

        self.move_ships()

    def move_ships(self):
        print_heading("Moving attack ships......")