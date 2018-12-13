import logging
from hlt.positionals import Direction
from src.common.values import MyConstants, MoveMode


def avoid_collision_direction(Moves, ship, directions):
    """
    GET BEST DIRECTION FOR KICKED SHIP

    :param Moves: Moves OBJECT, TO ACCESS data AND OTHER MOVES FUNCTIONS
    :param ship: SHIP OBJECT
    :param directions: DIRECTIONS DETERMINED BEFORE, BUT BEST ONE WILL COLLIDE
    :return: BEST DIRECTION
    """
    points = Moves.get_move_points_collision(ship, directions)
    best = max(points)
    return best.direction





