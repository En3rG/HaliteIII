#!/usr/bin/env python3
## Python 3.6

from src.initialization.start import Start
from src.initialization.explore import Data
from src.movement.ships import MoveShips
from src.movement.spawn import spawn_ships

## IMPORT THE HALITE SDK, WHICH WILL LET YOU INTERACT WITH THE GAME.
import hlt

## REGULAR STDOUT (PRINT STATEMENTS) ARE RSERVED FOR ENGINE-BOT COMMUNICATION.
import logging

""" <<<Game Begin>>> """

## THIS GAME OBJECT CONTAINS THE INITIAL GAME STATE.
game = hlt.Game()

## AT THIS POINT GAME VARIABLE IS POPULATED WITH INITIAL MAP DATA
## THIS IS A GOOD PLACE TO DO COMPUTATIONALLY EXPENSIVE START-UP PRE-PROCESING (30 secs)
ST = Start(game)

## AS SOON AS YOU CALL "ready" FUNCTION BELOW, THE 2 SECOND PER TURN TIMER WILL START.,
game.ready("En3rG")

logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

""" <<<Game Loop>>> """

prev_data = None

while True:
    ## THIS LOOP HANDLES EACH TURN OF THE GAME
    ## REFRESH STATE OF GAME
    game.update_frame()

    ## EXTRACT GAME DATA
    data = Data(game)

    ## MOVE SHIPS
    MS = MoveShips(data, prev_data)
    command_queue = MS.get_moves()

    ## SPAWN SHIPS
    command_queue = spawn_ships(data, command_queue)

    ## SEND MOVES BACK TO GAME ENVIRONMENT, ENDING THIS TURN.
    game.end_turn(command_queue)

    ## SAVE DATA TO PREV DATA
    prev_data = data
