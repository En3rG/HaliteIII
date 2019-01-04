import logging
from hlt.positionals import Direction
from src.common.values import MyConstants, MoveMode
from src.common.points import CollisionPoints
from src.common.orderedSet import OrderedSet

def get_adjacent_directions(direction):
    """
    GET ITS SIDE DIRECTIONS (NOT THE OPPOSITE THOUGH)
    """
    if direction == Direction.North:
        return [Direction.West, Direction.East]
    elif direction == Direction.East:
        return [Direction.North, Direction.South]
    elif direction == Direction.South:
        return [Direction.East, Direction.West]
    elif direction == Direction.West:
        return [Direction.South, Direction.North]


def move_kicked_ship(Moves, ship):
    """
    GO TOWARDS EXPLORE TARGET FIRST
    IT THAT IS NOT SAFE, GO ANYWHERE SAFE
    """
    explore_ship = Moves.data.myDicts.explore_ship[ship.id]
    explore_destination = explore_ship.destination
    explore_ratio = -explore_ship.ratio

    snipe_ship = Moves.data.myDicts.snipe_ship[ship.id]
    snipe_destination = snipe_ship.destination
    snipe_ratio = -snipe_ship.ratio

    ## DETERMINE WHETHER TO SNIPE OR EXPLORE
    if snipe_ratio > explore_ratio * MyConstants.EXPLORE_RATIO_TO_SNIPE:
        directions = Moves.get_directions_target(ship, snipe_destination)
    else:
        directions = Moves.get_directions_target(ship, explore_destination)

    direction = avoid_collision_direction(Moves, ship, directions=directions)
    Moves.move_mark_unsafe(ship, direction)


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

    :param ship:
    :param directions: DIRECTIONS SHIP WAS ORIGINALLY GOING
    :return:
    """
    points = []

    ## SET FIRST PRIORITY DIRECTIONS
    try: first_priority = OrderedSet(directions)
    except: first_priority = OrderedSet()

    ## SET SECOND PRIORITY DIRECTIONS
    second_priority = OrderedSet()
    for direction in directions:
        directions = set(get_adjacent_directions(direction))
        second_priority.update(directions)

    for direction in MyConstants.DIRECTIONS:                                                                            ## HAS NO STILL (KICKED, NEED TO MOVE)
        destination = Moves.get_destination(ship, direction)

        safe = Moves.data.myMatrix.locations.safe[destination.y][destination.x]
        occupied = Moves.data.myMatrix.locations.occupied[destination.y][destination.x]
        priority_direction = 2 if direction in first_priority else 1 if direction in second_priority else 0
        cost = Moves.data.myMatrix.halite.cost[ship.position.y][ship.position.x]
        harvest = Moves.data.myMatrix.halite.harvest_with_bonus[destination.y][destination.x]
        harvest_amnt = harvest - cost

        c = CollisionPoints(safe, occupied, priority_direction, harvest_amnt, direction)
        points.append(c)

    logging.debug(points)

    return points



