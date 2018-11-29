import logging
from hlt.positionals import Direction
from src.common.points import CollisionPoints
from src.common.values import MyConstants, MoveMode

def avoid_collision_direction(Moves, ship, directions):
    """
    GET BEST DIRECTION FOR KICKED SHIP

    :param Moves: MOVES OBJECT, TO ACCESS data AND OTHER MOVES FUNCTIONS
    :param ship: SHIP OBJECT
    :param directions: DIRECTIONS DETERMINED BEFORE, BUT BEST ONE WILL COLLIDE
    :return: BEST DIRECTION
    """
    points = get_points_collision(Moves, ship, directions)
    best = max(points)
    return best.direction

def get_points_collision(Moves, ship, directions):
    """
    GET POINTS FOR IMMINENT COLLISION PREVENTION
    """

    points = []
    try: directions_set = set(directions)
    except: directions_set = set()

    for direction in MyConstants.DIRECTIONS:
        destination = Moves.get_destination(ship, direction)

        safe = Moves.data.matrix.safe[destination.y][destination.x]
        occupied = Moves.data.matrix.occupied[destination.y][destination.x]
        priority_direction = 1 if direction in directions_set else 0
        cost = Moves.data.matrix.cost[ship.position.y][ship.position.x]
        harvest = Moves.data.matrix.harvest[destination.y][destination.x]
        harvest_amnt = harvest - cost

        c = CollisionPoints(safe, occupied, priority_direction, harvest_amnt, direction)
        points.append(c)

    logging.debug(points)

    return points
