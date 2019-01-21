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
    ## NEW WAY USING DEPLETION TIME
    # depletion_time = get_time_of_depletion(data)
    #
    # allowSpawn = data.game.turn_number <= constants.MAX_TURNS * MyConstants.spawn.min_turn_percent or \
    #              (data.game.turn_number <= constants.MAX_TURNS * MyConstants.spawn.max_turn_percent
    #               and depletion_time > constants.MAX_TURNS
    #               and data.myVars.ratio_left_halite > MyConstants.spawn.stop_halite_left)


    ## NEWER WAY (KEEP BUILDING IF BELOW THE ENEMY)
    numMyShips = data.myDicts.players_info[data.game.me.id].num_ships
    numEnemyShips, enemyID = min([ (v.num_ships, k) for k, v in data.myDicts.players_info.items() if k != data.game.me.id ])          ## LOWEST ENEMY SHIPS NUMBER
    ## KEEP MAKING SHIPS AS LONG AS ITS BELOW THE THRESHOLD TURNS
    ## AND WE HAVE MORE MONEY THAN LOWEST ENEMY
    ## AND WE HAVE LESS SHIPS THAN THE LOWEST ENEMY
    logging.debug("allowSpawn nummyships {} numenemyships {} ratio {}".format(numMyShips, numEnemyShips, numMyShips <= numEnemyShips * MyConstants.spawn.percent_more_ships))
    allowSpawn = data.game.turn_number <= constants.MAX_TURNS * data.myVars.max_allowed_turn \
                  and ( data.myVars.ratio_left_halite > MyConstants.spawn.stop_halite_left
                        or numMyShips < numEnemyShips * MyConstants.spawn.percent_more_ships)
                        #or ( len(data.game.players) == 2) and numMyShips < numEnemyShips * MyConstants.spawn.percent_more_ships )



    shipyard = data.game.game_map[data.game.me.shipyard]
    if allowSpawn \
            and data.myVars.isSaving == False \
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
    if len(data.myLists.ratio_left_halite) < MyConstants.spawn.num_rate_of_decay:
        data.myLists.ratio_left_halite.append(data.myVars.ratio_left_halite)
    else:
        data.myLists.ratio_left_halite.pop(0)  ## TAKE FIRST ELEMENT OFF
        data.myLists.ratio_left_halite.append(data.myVars.ratio_left_halite)

    ## CURRENT RATE OF DECAY
    change = data.myLists.ratio_left_halite[-1] - data.myLists.ratio_left_halite[0]
    rate_of_decay = np.log(1.00 - change) / MyConstants.spawn.num_rate_of_decay

    logging.debug("data.myLists.ratio_left_halite {}".format(data.myLists.ratio_left_halite))


    ## DETERMINE DEPLETION TIME USING AVERAGE RATE OF DECAY
    if rate_of_decay != 0:
        depletion_time = np.log(MyConstants.spawn.depleted_ratio) / -rate_of_decay
    else:
        depletion_time = 100000

    logging.debug("depletion_time {} to depleted_ratio {}".format(depletion_time, MyConstants.spawn.depleted_ratio))

    return depletion_time