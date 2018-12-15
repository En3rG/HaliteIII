from src.common.values import Matrix_val
from hlt.positionals import Direction
import logging
from src.common.points import RetreatPoints, DepositPoints, HarvestPoints, ExplorePoints, CollisionPoints, BuildPoints,\
                        AttackPoints, SupportPoints, StartPoints

def optimize_moves(commands):
    pass

    # for ship_id, action in commands.ships_moves.items():
    #     harvest = commands.data.myMatrix.halite.amount[action.destination.y][action.destination.x]
    #
    #     if action.direction \
    #             and harvest == 0 \
    #             and ship_id != -1 \
    #             and action.direction == Direction.Still \
    #             and action.points \
    #             and not isinstance(action.points[0], StartPoints):
    #             #and not isinstance(action.points[0], RetreatPoints) \
    #
    #
    #         logging.debug("ship id: {} bad move, need to optomize".format(ship_id))
    #
    #         logging.debug("ship id: {} command: {} destination: {} harvest: {} points: {}".format(ship_id,
    #                                                                                               action.command,
    #                                                                                               action.destination,
    #                                                                                               harvest,
    #                                                                                               action.points))
    #         if isinstance(action.points[0], DepositPoints):
    #             pass
    #
    #         elif isinstance(action.points[0], HarvestPoints):
    #             pass
    #
    #         elif isinstance(action.points[0], ExplorePoints):
    #             pass
    #             # priority_directions = get_priority_directions(action.points)
    #             # if len(priority_directions) == 1:
    #             #     acceptable_directions = get_adjacent_directions(priority_directions[0])
    #             #
    #             #     for i in range(1,len(action.points)): ## SKIPPING FIRST SINCE THATS THE ORIGINAL PICK
    #             #         point = action.points[i]
    #             #         new_direction = point.direction
    #             #         if point.safe == Matrix_val.UNSAFE:
    #             #             continue
    #             #         elif new_direction in acceptable_directions:
    #             #             ship = commands.data.game.me._ships.get(ship_id)
    #             #             commands.ships_moves[ship_id].command = ship.move(new_direction)
    #             #             #commands.ships_moves[ship_id].direction = new_direction
    #             #             #commands.ships_moves[ship_id].destination = new_destination
    #
    #
    #
    #         elif isinstance(action.points[0], CollisionPoints):
    #             pass
    #
    #         elif isinstance(action.points[0], BuildPoints):
    #             pass
    #
    #         elif isinstance(action.points[0], AttackPoints):
    #             pass
    #
    #         elif isinstance(action.points[0], SupportPoints):
    #             pass






def get_priority_directions(points):
    """
    GET PRIORITY DIRECTIONS
    """
    directions = []

    for point in points:
        if point.priority_direction == 1 and point.direction != Direction.Still:
            directions.append(point.direction)

    return directions

def get_adjacent_directions(direction):
    """
    GET ITS SIDE DIRECTIONS (NOT THE OPPOSITE THOUGH)
    """
    if direction == Direction.North:
        return { Direction.West, Direction.East }
    elif direction == Direction.East:
        return { Direction.North, Direction.South }
    elif direction == Direction.South:
        return { Direction.East, Direction.West }
    elif direction == Direction.West:
        return { Direction.South, Direction.North }


