#!/usr/bin/env python3
## Python 3.6

## Import the Halite SDK, which will let you interact with the game.
import hlt

## This library contains constant values.
from hlt import constants

## This library contains direction metadata to better interface with the game.
from hlt.positionals import Direction

## This library allows you to generate random numbers.
import random

## Logging allows you to save messages for yourself. This is required because the regular STDOUT
##  (print statements) are reserved for the engine-bot communication.
import logging

from src.initialization.start import Start
from src.initialization.explore import Data
from src.movement.move import Move

""" <<<Game Begin>>> """

## This game object contains the initial game state.
game = hlt.Game()
## At this point "game" variable is populated with initial map data.
## This is a good place to do computationally expensive start-up pre-processing (30000 ms).
S = Start(game)

## As soon as you call "ready" function below, the 2 second per turn timer will start.
game.ready("En3rG")

## Now that your bot is initialized, save a message to yourself in the log file with some important information.
##  Here, you log here your id, which you can always fetch from the game object by using my_id.
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

""" <<<Game Loop>>> """

prev_data = None

while True:
    ## This loop handles each turn of the game. The game object changes every turn, and you refresh that state by
    ##   running update_frame().
    game.update_frame()
    ## You extract player metadata and the updated map metadata here for convenience.

    data = Data(game)

    me = game.me
    game_map = game.game_map

    M = Move(data, prev_data)
    command_queue = M.get_moves()

    ## If the game is in the first 200 turns and you have enough halite, spawn a ship.
    ## Don't spawn a ship if you currently have a ship at port, though - the ships will collide.
    if game.turn_number <= 200 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        command_queue.append(me.shipyard.spawn())

    ## Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)

    ## SAVE DATA TO PREV DATA
    prev_data = data
