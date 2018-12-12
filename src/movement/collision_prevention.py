import logging
from hlt.positionals import Direction
from src.common.points import CollisionPoints
from src.common.values import MyConstants, MoveMode
from src.common.classes import OrderedSet

def avoid_collision_direction(Moves, ship, directions):
    """
    GET BEST DIRECTION FOR KICKED SHIP

    :param Moves: Moves OBJECT, TO ACCESS data AND OTHER MOVES FUNCTIONS
    :param ship: SHIP OBJECT
    :param directions: DIRECTIONS DETERMINED BEFORE, BUT BEST ONE WILL COLLIDE
    :return: BEST DIRECTION
    """
    points = get_move_points_collision(Moves, ship, directions)
    best = max(points)
    return best.direction


def get_move_points_collision(Moves, ship, directions):
    """
    GET POINTS FOR IMMINENT COLLISION PREVENTION

    :param Moves:
    :param ship:
    :param directions: DIRECTIONS SHIP WAS ORIGINALLY GOING
    :return:
    """
    points = []
    try: directions_set = OrderedSet(directions)
    except: directions_set = OrderedSet()

    for direction in MyConstants.DIRECTIONS:  ## HAS NO STILL (KICKED, NEED TO MOVE)
        destination = Moves.get_destination(ship, direction)

        safe = Moves.data.myMatrix.locations.safe[destination.y][destination.x]
        occupied = Moves.data.myMatrix.locations.occupied[destination.y][destination.x]
        priority_direction = 1 if direction in directions_set else 0
        cost = Moves.data.myMatrix.halite.cost[ship.position.y][ship.position.x]
        harvest = Moves.data.myMatrix.halite.harvest_with_bonus[destination.y][destination.x]
        harvest_amnt = harvest - cost

        c = CollisionPoints(safe, occupied, priority_direction, harvest_amnt, direction)
        points.append(c)

    logging.debug(points)

    return points
