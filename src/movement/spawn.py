from hlt import constants
from src.common.values import Matrix_val, MyConstants
import logging

def spawn_ships(data, command_queue):
    """
    CHECK IF ITS SAFE TO SPAWN SHIPS

    :param data:
    :param command_queue:
    :return: command_queue (NOT NECESSARY)
    """
    if data.game.turn_number <= constants.MAX_TURNS * MyConstants.STOP_SPAWNING \
            and data.me.halite_amount >= constants.SHIP_COST \
            and not data.game_map[data.me.shipyard].is_occupied\
            and data.matrix.unsafe[data.game_map[data.me.shipyard].position.y][data.game_map[data.me.shipyard].position.x] != Matrix_val.UNSAFE.value:

        logging.debug("Spawning ship...")
        command_queue.append(data.me.shipyard.spawn())

    return command_queue