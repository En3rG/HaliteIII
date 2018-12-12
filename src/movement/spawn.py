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
    if data.myVars.allowSpawn \
            and data.myVars.isBuilding == False \
            and data.game.me.halite_amount >= constants.SHIP_COST \
            and data.myMatrix.locations.safe[data.game.game_map[data.game.me.shipyard].position.y][data.game.game_map[data.game.me.shipyard].position.x] != Matrix_val.UNSAFE:
            # and not data.game.game_map[data.game.me.shipyard].is_occupied\ ## NOT ACCURATE? LOOKS AT CURRENT TURN BUT SPAWN HAPPENS NEXT TURN

        print_heading("Safe to spawn ship......")
        data.halite_stats.record_spent(BuildType.SHIP)
        data.command_queue.append(data.game.me.shipyard.spawn())
