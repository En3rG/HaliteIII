
import hlt
import json
import logging
import numpy as np
import traceback
import sys
import time

name = "p0"

with open('moves/' + name + '.txt') as json_data:
    moves = json.load(json_data)
    player_name = moves.pop(0)
    _ = moves.pop(0)  ## EXTRA MOVE?
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






