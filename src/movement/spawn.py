from hlt import constants
from src.common.values import Matrix_val, MyConstants
from src.common.halite_statistics import BuildType
import logging
from src.common.print import print_heading
import numpy as np




def spawn_ships(data):
    """
    CHECK IF ITS SAFE TO SPAWN SHIPS

    -BELOW STOP SPAWNING PERCENTAGE
    -HAVE ENOUGH HALITE TO BUILD
    -NOT BUILDING DOCKS
    -SHIPYARD NOT OCCUPIED
    -NO SHIP GOING TO SHIPYARD

    :param data:
    """
    ## OLD WAY
    max_turn_percent = None
    
    if len(data.game.players) == 2:
        if data.game.game_map.height == 32:
            max_turn_percent = MyConstants.ALLOW_SPAWNING_2P_32_TURNS
        elif data.game.game_map.height == 40:
            max_turn_percent = MyConstants.ALLOW_SPAWNING_2P_40_TURNS
        elif data.game.game_map.height == 48:
            max_turn_percent = MyConstants.ALLOW_SPAWNING_2P_48_TURNS
        elif data.game.game_map.height == 56:
            max_turn_percent = MyConstants.ALLOW_SPAWNING_2P_56_TURNS
        elif data.game.game_map.height == 64:
            max_turn_percent = MyConstants.ALLOW_SPAWNING_2P_64_TURNS

    else:  ## 4 PLAYERS
        if data.game.game_map.height == 32:
            max_turn_percent = MyConstants.ALLOW_SPAWNING_4P_32_TURNS
        elif data.game.game_map.height == 40:
            max_turn_percent = MyConstants.ALLOW_SPAWNING_4P_40_TURNS
        elif data.game.game_map.height == 48:
            max_turn_percent = MyConstants.ALLOW_SPAWNING_4P_48_TURNS
        elif data.game.game_map.height == 56:
            max_turn_percent = MyConstants.ALLOW_SPAWNING_4P_56_TURNS
        elif data.game.game_map.height == 64:
            max_turn_percent = MyConstants.ALLOW_SPAWNING_4P_64_TURNS

    allowSpawn = data.game.turn_number <= constants.MAX_TURNS * max_turn_percent \
                             and data.myVars.ratio_left_halite > MyConstants.STOP_SPAWNING_HALITE_LEFT

    ## NEW WAY USING DEPLETION TIME
    # depletion_time = get_time_of_depletion(data)
    #
    # allowSpawn = data.game.turn_number <= constants.MAX_TURNS * MyConstants.MIN_TURN_PERCENT or \
    #              (data.game.turn_number <= constants.MAX_TURNS * MyConstants.MAX_TURN_PERCENT
    #               and depletion_time > constants.MAX_TURNS
    #               and data.myVars.ratio_left_halite > MyConstants.STOP_SPAWNING_HALITE_LEFT)


    shipyard = data.game.game_map[data.game.me.shipyard]
    if allowSpawn \
            and data.myVars.dontSpawn == False \
            and data.game.me.halite_amount >= constants.SHIP_COST \
            and data.myMatrix.locations.safe[shipyard.position.y][shipyard.position.x] != Matrix_val.UNSAFE:
            # and not data.game.game_map[data.game.me.shipyard].is_occupied\                                            ## NOT ACCURATE? LOOKS AT CURRENT TURN BUT SPAWN HAPPENS NEXT TURN

        print_heading("Safe to spawn ship......")
        data.halite_stats.record_spent(BuildType.SHIP)
        command = data.game.me.shipyard.spawn()
        data.command_queue.append(command)


def get_time_of_depletion(data):
    """
    GET THE TIME OF DEPLETION UP TO A CERTAIN VALUE
    SINCE IT WILL NEVER HIT 0

    USING RATE OF DECAY

    ln(N/Nt) = -λt

    where N/Nt is the percent left
    """
    ## LIMIT NUMBER OF RATIO LEFT HALITE
    if len(data.myLists.ratio_left_halite) < MyConstants.NUM_RATE_OF_DECAY:
        data.myLists.ratio_left_halite.append(data.myVars.ratio_left_halite)
    else:
        data.myLists.ratio_left_halite.pop(0)  ## TAKE FIRST ELEMENT OFF
        data.myLists.ratio_left_halite.append(data.myVars.ratio_left_halite)

    ## CURRENT RATE OF DECAY
    change = data.myLists.ratio_left_halite[-1] - data.myLists.ratio_left_halite[0]
    rate_of_decay = np.log(1.00 - change) / MyConstants.NUM_RATE_OF_DECAY

    logging.debug("data.myLists.ratio_left_halite {}".format(data.myLists.ratio_left_halite))


    ## DETERMINE DEPLETION TIME USING AVERAGE RATE OF DECAY
    if rate_of_decay != 0:
        depletion_time = np.log(MyConstants.DEPLETED_RATIO) / -rate_of_decay
    else:
        depletion_time = 100000

    logging.debug("depletion_time {} to depleted_ratio {}".format(depletion_time, MyConstants.DEPLETED_RATIO))

    return depletion_time