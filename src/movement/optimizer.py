
from hlt.positionals import Direction
import logging

def optimize_moves(commands):
    for ship_id, action in commands.ships_moves.items():
        harvest = commands.data.myMatrix.halite.amount[action.destination.y][action.destination.x]
        logging.debug("ship id: {} command: {} destination: {} harvest: {} points: {}".format(ship_id,
                                                                                              action.command,
                                                                                              action.destination,
                                                                                              harvest,
                                                                                              action.points))
        if action.direction and harvest == 0 and ship_id != -1 and action.direction == Direction.Still:
            logging.debug("ship id: {} bad move, need to optomize".format(ship_id))