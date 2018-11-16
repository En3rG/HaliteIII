from hlt import constants
from src.common.values import Matrix_val, MyConstants
from src.common.halite_statistics import BuildType
import logging


def spawn_ships(data, command_queue, halite_stats):
    """
    CHECK IF ITS SAFE TO SPAWN SHIPS

    -BELOW STOP SPAWNING PERCENTAGE
    -HAVE ENOUGH HALITE TO BUILD
    -SHIPYARD NOT OCCUPIED
    -NO SHIP GOING TO SHIPYARD

    :param data:
    :param command_queue:
    :return: command_queue (NOT NECESSARY)
    """
    if data.game.turn_number <= constants.MAX_TURNS * MyConstants.STOP_SPAWNING \
            and data.me.halite_amount >= constants.SHIP_COST \
            and not data.game_map[data.me.shipyard].is_occupied\
            and data.matrix.unsafe[data.game_map[data.me.shipyard].position.y][data.game_map[data.me.shipyard].position.x] != Matrix_val.UNSAFE:

        logging.debug("Safe to spawn ship...")
        halite_stats.record_spent(BuildType.SHIP)
        command_queue.append(data.me.shipyard.spawn())