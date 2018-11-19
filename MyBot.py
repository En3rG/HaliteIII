#!/usr/bin/env python3
## Python 3.6

from src.initialization.start import Start
from src.initialization.gather import Data
from src.movement.stuck import Stuck
from src.movement.deposit import Deposit
from src.movement.explore import Explore
from src.movement.harvest_closeby import Harvest
from src.movement.spawn import spawn_ships
from src.movement.retreat import Retreat
from src.movement.attack import Attack
from src.movement.build import Build
from src.common.halite_statistics import Halite_stats
from src.common.print import print_heading
import copy

## IMPORT THE HALITE SDK, WHICH WILL LET YOU INTERACT WITH THE GAME.
import hlt

## REGULAR STDOUT (PRINT STATEMENTS) ARE RESERVED FOR ENGINE-BOT COMMUNICATION.
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
halite_stats = Halite_stats()

while True:
    ## THIS LOOP HANDLES EACH TURN OF THE GAME
    ## REFRESH STATE OF GAME
    game.update_frame()
    command_queue = []

    ## EXTRACT GAME DATA
    data = Data(game, prev_data, halite_stats)

    ## RETREAT SHIPS
    A = Retreat(data, prev_data, command_queue, halite_stats)

    ## STUCK SHIPS
    B = Stuck(data, prev_data, command_queue, halite_stats)

    ## BUILD DOCK
    C = Build(data, prev_data, command_queue, halite_stats)

    ## DEPOSIT SHIPS
    D = Deposit(data, prev_data, command_queue, halite_stats)

    ## ATTACK SHIPS
    E = Attack(data, prev_data, command_queue, halite_stats)

    ## HARVEST SHIPS
    F = Harvest(data, prev_data, command_queue, halite_stats)

    ## EXPLORE SHIPS
    G = Explore(data, prev_data, command_queue, halite_stats)

    ## SPAWN SHIPS
    H = spawn_ships(data, command_queue, halite_stats)

    ## SEND MOVES BACK TO GAME ENVIRONMENT, ENDING THIS TURN.
    game.end_turn(command_queue)

    ## SAVE DATA TO PREV DATA
    prev_data = copy.deepcopy(data)

    ## UPDATE HALITE AMOUNT/CARRIED
    halite_stats.set_halite(game.me.halite_amount)

    ## PRINT HALITE STATS
    print_heading("Halite Stats: {}".format(halite_stats))
