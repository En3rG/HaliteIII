from hlt import constants
from src.common.values import Matrix_val, MyConstants
from src.common.halite_statistics import BuildType
import logging
from src.common.print import print_heading


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

    shipyard = data.game.game_map[data.game.me.shipyard]
    if allowSpawn \
            and data.myVars.isBuilding == False \
            and data.game.me.halite_amount >= constants.SHIP_COST \
            and data.myMatrix.locations.safe[shipyard.position.y][shipyard.position.x] != Matrix_val.UNSAFE:
            # and not data.game.game_map[data.game.me.shipyard].is_occupied\                                            ## NOT ACCURATE? LOOKS AT CURRENT TURN BUT SPAWN HAPPENS NEXT TURN

        print_heading("Safe to spawn ship......")
        data.halite_stats.record_spent(BuildType.SHIP)
        command = data.game.me.shipyard.spawn()
        data.command_queue.append(command)
