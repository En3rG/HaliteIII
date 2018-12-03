#!/usr/bin/env python3
## Python 3.6

from src.initialization.getInitData import GetInitData
from src.initialization.getData import GetData
from src.movement.stuck import Stuck
from src.movement.deposit import Deposit
from src.movement.explore import Explore
from src.movement.harvest_closeby import Harvest
from src.movement.spawn import spawn_ships
from src.movement.retreat import Retreat
from src.movement.attack import Attack
from src.movement.depart import Depart
from src.movement.build import Build
from src.common.halite_statistics import Halite_stats
from src.common.print import print_heading
import copy

## IMPORT THE HALITE SDK, WHICH WILL LET YOU INTERACT WITH THE GAME.
import hlt

## REGULAR STDOUT (PRINT STATEMENTS) ARE RESERVED FOR ENGINE-BOT COMMUNICATION.
import logging

class PrevData():
    """
    USED TO MINIMIZE THE SIZE OF PREVIOUS DATA WHEN COPIED
    SHOULD ONLY CONTAIN NECESSARY INFORMATION FROM DATA
    """
    def __init__(self, data):
        self.me = data.game.me
        self.matrix = data.matrix
        self.ships_all = data.mySets.ships_all
        self.ships_returning = data.mySets.ships_returning

""" <<<Game Begin>>> """

## THIS GAME OBJECT CONTAINS THE INITIAL GAME STATE.
game = hlt.Game()

## AT THIS POINT GAME VARIABLE IS POPULATED WITH INITIAL MAP DATA
## THIS IS A GOOD PLACE TO DO COMPUTATIONALLY EXPENSIVE START-UP PRE-PROCESING (30 secs)
init_data = GetInitData(game)

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

    ## EXTRACT GAME DATA
    data = GetData(game, init_data, prev_data, halite_stats)

    ## RETREAT SHIPS
    A = Retreat(data, prev_data)

    ## STUCK SHIPS
    B = Stuck(data, prev_data)

    ## BUILD DOCK
    C = Build(data, prev_data)

    ## DEPART SHIPS (FROM SHIPYARD/DOCK)
    #D = Depart(data, prev_data)

    ## DEPOSIT SHIPS
    E = Deposit(data, prev_data)

    ## ATTACK SHIPS
    F = Attack(data, prev_data)

    ## HARVEST SHIPS
    #G = Kicked(data, prev_data)

    ## HARVEST SHIPS
    H = Harvest(data, prev_data)

    ## EXPLORE SHIPS
    I = Explore(data, prev_data)

    ## SPAWN SHIPS
    J = spawn_ships(data)

    ## SEND MOVES BACK TO GAME ENVIRONMENT, ENDING THIS TURN.
    logging.debug("command_queue: {}".format(data.command_queue))
    game.end_turn(data.command_queue)

    ## SAVE DATA TO PREV DATA
    #prev_data = copy.deepcopy(data)  ## TAKES 300ms, AND COPYING A LOT OF UNNECESSARY STUFF
    prev_data = copy.deepcopy(PrevData(data))

    ## UPDATE HALITE AMOUNT/CARRIED
    halite_stats.set_halite(game, data)

    ## PRINT HALITE STATS
    print_heading("Halite Stats: {}".format(halite_stats))
