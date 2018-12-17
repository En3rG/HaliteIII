from hlt.positionals import Direction

def get_adjacent_directions(direction):
    """
    GET ITS SIDE DIRECTIONS (NOT THE OPPOSITE THOUGH)
    """
    if direction == Direction.North:
        return {Direction.West, Direction.East}
    elif direction == Direction.East:
        return {Direction.North, Direction.South}
    elif direction == Direction.South:
        return {Direction.East, Direction.West}
    elif direction == Direction.West:
        return {Direction.South, Direction.North}