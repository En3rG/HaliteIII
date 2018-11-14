
class FarthestShip:
    """
    USED TO DETERMINE FARTHEST SHIP FOR RETREAT
    ALSO USED FOR HEAPQ PURPOSES IN RETREAT

    distance > num_directions > ship_id
    """
    def __init__(self, dist, num_directions, id, directions):
        self.distance = dist
        self.num_directions = num_directions
        self.ship_id = id
        self.directions = directions

    def __gt__(self, other):
        if isinstance(other, FarthestShip):
            if self.distance > other.distance:
                return True
            elif self.distance < other.distance:
                return False
            elif self.num_directions > other.num_directions:
                return True
            elif self.num_directions < other.num_directions:
                return False
            elif self.ship_id > other.ship_id:
                return True
            elif self.ship_id < other.ship_id:
                return False

    def __lt__(self, other):
        if isinstance(other, FarthestShip):
            if self.distance < other.distance:
                return True
            elif self.distance > other.distance:
                return False
            elif self.num_directions < other.num_directions:
                return True
            elif self.num_directions > other.num_directions:
                return False
            elif self.ship_id < other.ship_id:
                return True
            elif self.ship_id > other.ship_id:
                return False

    def __repr__(self):
        return "Ship id: {} distance: {}".format(self.ship_id, self.distance)


class RetreatPoints():
    """
    USED TO DETERMINE BEST DIRECTION FOR RETREAT

    shipyard > not occupied > least potential ally collisions
    """
    def __init__(self, shipyard, unsafe, potential_collision, direction):
        self.shipyard = shipyard
        self.unsafe = unsafe
        self.potential_collision = potential_collision
        self.direction = direction

    def __gt__(self, other):
        if isinstance(other, RetreatPoints):
            if self.shipyard > other.shipyard:
                return True
            elif self.shipyard < other.shipyard:
                return False
            elif self.unsafe > other.unsafe:
                return True
            elif self.unsafe < other.unsafe:
                return False
            elif self.potential_collision > other.potential_collision:
                return True
            elif self.potential_collision < other.potential_collision:
                return False

    def __lt__(self, other):
        if isinstance(other, RetreatPoints):
            if self.shipyard < other.shipyard:
                return True
            elif self.shipyard > other.shipyard:
                return False
            elif self.unsafe < other.unsafe:
                return True
            elif self.unsafe > other.unsafe:
                return False
            elif self.potential_collision < other.potential_collision:
                return True
            elif self.potential_collision > other.potential_collision:
                return False


