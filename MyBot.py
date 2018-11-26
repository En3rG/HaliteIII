#!/usr/bin/env python3
## Python 3.6

from src.initialization.prestart import Init
from src.initialization.gather import MyData
from src.movement.stuck import Stuck
from src.movement.deposit import Deposit
from src.movement.explore import Explore
from src.movement.harvest_closeby import Harvest
from src.movement.spawn import spawn_ships
from src.movement.retreat import Retreat
from src.movement.attack import Attack
from src.movement.kicked import Kicked
from src.movement.build import Build
from src.common.halite_statistics import Halite_stats
from src.common.print import print_heading
import copy

## IMPORT THE HALITE SDK, WHICH WILL LET YOU INTERACT WITH THE GAME.
import hlt

## REGULAR STDOUT (PRINT STATEMENTS) ARE RESERVED FOR ENGINE-BOT COMMUNICATION.
import logging

class PrevData():
    def __init__(self, data):
        self.me = data.me
        self.all_ships = data.all_ships
        self.ships_returning = data.ships_returning

""" <<<Game Begin>>> """

## THIS GAME OBJECT CONTAINS THE INITIAL GAME STATE.
game = hlt.Game()

## AT THIS POINT GAME VARIABLE IS POPULATED WITH INITIAL MAP DATA
## THIS IS A GOOD PLACE TO DO COMPUTATIONALLY EXPENSIVE START-UP PRE-PROCESING (30 secs)
INIT_DATA = Init(game)

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
    data = MyData(game, INIT_DATA, prev_data, halite_stats)

    ## RETREAT SHIPS
    A = Retreat(data, prev_data)

    ## STUCK SHIPS
    B = Stuck(data, prev_data)

    ## BUILD DOCK
    C = Build(data, prev_data)

    ## DEPOSIT SHIPS
    D = Deposit(data, prev_data)

    ## ATTACK SHIPS
    E = Attack(data, prev_data)

    ## HARVEST SHIPS
    F = Kicked(data, prev_data)

    ## HARVEST SHIPS
    G = Harvest(data, prev_data)

    ## EXPLORE SHIPS
    H = Explore(data, prev_data)

    ## SPAWN SHIPS
    I = spawn_ships(data)

    ## SEND MOVES BACK TO GAME ENVIRONMENT, ENDING THIS TURN.
    game.end_turn(data.command_queue)

    ## SAVE DATA TO PREV DATA
    #prev_data = copy.deepcopy(data)  ## TAKES 300ms, AND COPYING A LOT OF UNNECESSARY STUFF
    prev_data = copy.deepcopy(PrevData(data))

    ## UPDATE HALITE AMOUNT/CARRIED
    halite_stats.set_halite(game.me.halite_amount)

    ## PRINT HALITE STATS
    print_heading("Halite Stats: {}".format(halite_stats))
