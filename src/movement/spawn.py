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
    # max_turn_percent = None
    #
    # if len(data.game.players) == 2:
    #     if data.game.game_map.height == 32:
    #         max_turn_percent = MyConstants.ALLOW_SPAWNING_2P_32_TURNS
    #     elif data.game.game_map.height == 40:
    #         max_turn_percent = MyConstants.ALLOW_SPAWNING_2P_40_TURNS
    #     elif data.game.game_map.height == 48:
    #         max_turn_percent = MyConstants.ALLOW_SPAWNING_2P_48_TURNS
    #     elif data.game.game_map.height == 56:
    #         max_turn_percent = MyConstants.ALLOW_SPAWNING_2P_56_TURNS
    #     elif data.game.game_map.height == 64:
    #         max_turn_percent = MyConstants.ALLOW_SPAWNING_2P_64_TURNS
    #
    # else:  ## 4 PLAYERS
    #     if data.game.game_map.height == 32:
    #         max_turn_percent = MyConstants.ALLOW_SPAWNING_4P_32_TURNS
    #     elif data.game.game_map.height == 40:
    #         max_turn_percent = MyConstants.ALLOW_SPAWNING_4P_40_TURNS
    #     elif data.game.game_map.height == 48:
    #         max_turn_percent = MyConstants.ALLOW_SPAWNING_4P_48_TURNS
    #     elif data.game.game_map.height == 56:
    #         max_turn_percent = MyConstants.ALLOW_SPAWNING_4P_56_TURNS
    #     elif data.game.game_map.height == 64:
    #         max_turn_percent = MyConstants.ALLOW_SPAWNING_4P_64_TURNS
    #
    # allowSpawn = data.game.turn_number <= constants.MAX_TURNS * max_turn_percent \
    #                          and data.myVars.ratio_left_halite > MyConstants.STOP_SPAWNING_HALITE_LEFT

    ## NEW WAY
    depletion_time = get_time_of_depletion(data)
    max_turn_percent = 0.75

    allowSpawn = data.game.turn_number <= constants.MAX_TURNS * max_turn_percent \
                             and depletion_time > constants.MAX_TURNS


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
    ## CURRENT RATE OF DECAY
    rate_of_decay = np.log(data.myVars.ratio_left_halite) / data.game.turn_number

    ## LIMIT NUMBER OF RATE OF DECAYS
    if len(data.myLists.rate_of_decays) < MyConstants.NUM_RATE_OF_DECAY:
        data.myLists.rate_of_decays.append(rate_of_decay)
    else:
        data.myLists.rate_of_decays.pop(0)                                                                              ## TAKE FIRST ELEMENT OFF
        data.myLists.rate_of_decays.append(rate_of_decay)

    logging.debug("data.myLists.rate_of_decays {}".format(data.myLists.rate_of_decays))

    ave_rate_of_decay = sum(data.myLists.rate_of_decays) / len(data.myLists.rate_of_decays)

    logging.debug("ave_rate_of_decay {}".format(ave_rate_of_decay))

    ## DETERMINE DEPLETION TIME USING AVERAGE RATE OF DECAY
    if ave_rate_of_decay != 0:
        depletion_time = -np.log(MyConstants.DEPLETED_RATIO) / -ave_rate_of_decay
    else:
        depletion_time = 100000

    logging.debug("depletion_time {} to depleted_ratio {}".format(depletion_time, MyConstants.DEPLETED_RATIO))

    return depletion_time