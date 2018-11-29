import logging
from hlt.positionals import Direction
from src.common.points import KickedPoints
from src.common.values import MyConstants, MoveMode

def get_direction_kicked(Moves, ship, mode, directions):
    points = get_points_kicked(Moves, ship, mode, directions)
    best = max(points)
    return best.direction

def get_points_kicked(Moves, ship, mode, directions):
    """
    GET POINTS FOR KICKED
    """

    points = []
    directions_set = set(directions)

    for direction in MyConstants.DIRECTIONS:
        destination = Moves.get_destination(ship, direction)

        safe = Moves.data.matrix.safe[destination.y][destination.x]
        occupied = Moves.data.matrix.occupied[destination.y][destination.x]
        if mode == MoveMode.EXPLORE: priority_direction = 1 if direction in directions_set else 0 ## IS THIS NECESSARY?????
        else: priority_direction = 0
        cost = Moves.data.matrix.cost[ship.position.y][ship.position.x]
        harvest = Moves.data.matrix.harvest[destination.y][destination.x]
        harvest_amnt = harvest - cost

        c = KickedPoints(safe, occupied, priority_direction, harvest_amnt, direction)
        points.append(c)

    logging.debug(points)

    return points
