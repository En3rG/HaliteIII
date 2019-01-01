#!/usr/bin/env python3
## Python 3.6

from src.initialization.getInitData import GetInitData
from src.initialization.getData import GetData
from src.movement.stuck import Stuck
from src.movement.deposit import Deposit
from src.movement.influence import Influence
from src.movement.explore import Explore
from src.movement.harvest import Harvest
from src.movement.spawn import spawn_ships
from src.movement.retreat import Retreat
from src.movement.exploreTarget import ExploreTarget
from src.movement.enemyTarget import EnemyTarget
from src.movement.attack import Attack
from src.movement.swap import Swap
from src.movement.evade import Evade
from src.movement.attack2 import Attack2
from src.movement.snipe import Snipe
from src.movement.build import Build
from src.movement.start import Start
from src.common.halite_statistics import Halite_stats
from src.common.print import print_heading
import copy
import hlt                                                                                                              ## IMPORT THE HALITE SDK, WHICH WILL LET YOU INTERACT WITH THE GAME.
import logging                                                                                                          ## REGULAR STDOUT (PRINT STATEMENTS) ARE RESERVED FOR ENGINE-BOT COMMUNICATION.

class PrevData():
    """
    USED TO MINIMIZE THE SIZE OF PREVIOUS DATA WHEN COPIED
    SHOULD ONLY CONTAIN NECESSARY INFORMATION FROM DATA THAT
    ARE NEEDED FOR THE NEXT TURN
    """
    def __init__(self, data):
        self.me = data.game.me
        self.matrix = data.myMatrix
        self.ships_all = data.mySets.ships_all
        self.ships_returning = data.mySets.ships_returning
        self.positions_taken = data.myDicts.positions_taken
        self.ships_building = data.mySets.ships_building
        self.rate_of_decays = data.myLists.rate_of_decays

""" <<<Game Begin>>> """

game = hlt.Game()                                                                                                       ## THIS GAME OBJECT CONTAINS THE INITIAL GAME STATE.

init_data = GetInitData(game)                                                                                           ## CAN HAVE UP TO 30 SECONDS INITIALIZATION TIME

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

    ## START SHIPS
    a = Start(data, prev_data)

    ## BUILD DOCK
    C = Build(data, prev_data)

    ## DEPOSIT SHIPS
    E = Deposit(data, prev_data)

    ## GET EACH SHIP'S TARGET
    M = ExploreTarget(data, prev_data)
    N = EnemyTarget(data, prev_data)

    ## HARVEST SHIPS
    H = Harvest(data, prev_data)

    ## ATTACK SHIPS
    #G = Attack(data, prev_data)
    P = Attack2(data, prev_data)

    ## EVADE SHIPS
    L = Evade(data, prev_data)

    ## SWAP SHIPS
    Q = Swap(data, prev_data)

    ## INFLUENCE SHIPS
    K = Influence(data, prev_data)

    ## TARGET ENEMY SHIP
    O = Snipe(data, prev_data)

    ## EXPLORE SHIPS
    I = Explore(data, prev_data)

    ## SPAWN SHIPS
    J = spawn_ships(data)

    game.end_turn(data.command_queue)

    ## SAVE DATA TO PREV DATA
    #prev_data = copy.deepcopy(data)  ## TAKES 300ms, AND COPYING A LOT OF UNNECESSARY STUFF
    prev_data = copy.deepcopy(PrevData(data))

    ## UPDATE HALITE AMOUNT/CARRIED
    halite_stats.set_halite(game, data)

    ## PRINT HALITE STATS
    print_heading("Halite Stats: {}".format(halite_stats))
