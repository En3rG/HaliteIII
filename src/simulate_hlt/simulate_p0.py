
import hlt
import json
import logging
import numpy as np
import traceback
import sys

player_name = "p0"

with open('moves/' + player_name + '.txt') as json_data:
    moves = json.load(json_data)

    game = hlt.Game()
    game.ready(player_name)
    logging.info("Starting my bot!")

    turn = 0

    while True:
        game.update_frame()

        command_queue = moves.pop(0)
        logging.debug("Turn: {} command_queue: {}".format(turn, command_queue))
        game.end_turn(command_queue)
        turn += 1






