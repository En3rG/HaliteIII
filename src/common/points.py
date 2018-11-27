
class FarthestShip:
    """
    USED TO DETERMINE FARTHEST SHIP FOR RETREAT/RETURNING
    ALSO USED FOR HEAPQ PURPOSES

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
            elif self.ship_id >= other.ship_id:
                return True
            elif self.ship_id < other.ship_id:
                return False

        return NotImplemented

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
            elif self.ship_id <= other.ship_id:
                return True
            elif self.ship_id > other.ship_id:
                return False

        return NotImplemented

    def __repr__(self):
        return "Ship id: {} distance: {}".format(self.ship_id, self.distance)


class RetreatPoints():
    """
    USED TO DETERMINE BEST DIRECTION FOR RETREAT

    shipyard > not occupied > least potential ally collisions
    """
    def __init__(self, shipyard, safe, stuck, potential_ally_collision, direction):
        self.shipyard = shipyard
        self.safe = safe
        self.stuck = -stuck
        self.potential_ally_collision = potential_ally_collision
        self.direction = direction

    def __gt__(self, other):
        if isinstance(other, RetreatPoints):
            if self.shipyard > other.shipyard:
                return True
            elif self.shipyard < other.shipyard:
                return False
            elif self.safe > other.safe:
                return True
            elif self.safe < other.safe:
                return False
            elif self.stuck > other.stuck:
                return True
            elif self.stuck < other.stuck:
                return False
            elif self.potential_ally_collision > other.potential_ally_collision:
                return True
            elif self.potential_ally_collision < other.potential_ally_collision:
                return False
            else:
                return False ## OTHER PROPERTY NOT ABOVE IS NEGLECTED

        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, RetreatPoints):
            if self.shipyard < other.shipyard:
                return True
            elif self.shipyard > other.shipyard:
                return False
            elif self.safe < other.safe:
                return True
            elif self.safe > other.safe:
                return False
            elif self.stuck < other.stuck:
                return True
            elif self.stuck > other.stuck:
                return False
            elif self.potential_ally_collision < other.potential_ally_collision:
                return True
            elif self.potential_ally_collision > other.potential_ally_collision:
                return False
            else:
                return False ## OTHER PROPERTY NOT ABOVE IS NEGLECTED

        return NotImplemented

    def __repr__(self):
        return "{} shipyard: {} safe: {} stuck: {} potential_ally_collision: {} direction: {}".format(self.__class__.__name__,
                                                                                           self.shipyard,
                                                                                           self.safe,
                                                                                           self.stuck,
                                                                                           self.potential_ally_collision,
                                                                                           self.direction)



class DepositPoints():
    """
    USED TO DETERMINE BEST DIRECTION FOR RETURNING/DEPOSITING

    not occupied > cost
    """
    def __init__(self, safe, potential_enemy_collision, potential_ally_collision, cost, direction):
        self.safe = safe
        self.potential_enemy_collision = potential_enemy_collision
        self.potential_ally_collision = potential_ally_collision
        self.cost = -cost  ## NEGATIVE BECAUSE WE WANT THE LEAST COST
        self.direction = direction

    def __gt__(self, other):
        if isinstance(other, DepositPoints):
            if self.safe > other.safe:
                return True
            elif self.safe < other.safe:
                return False
            elif self.potential_enemy_collision > other.potential_enemy_collision:
                return True
            elif self.potential_enemy_collision < other.potential_enemy_collision:
                return False
            elif self.potential_ally_collision > other.potential_ally_collision:
                return True
            elif self.potential_ally_collision < other.potential_ally_collision:
                return False
            elif self.cost > other.cost:
                return True
            elif self.cost < other.cost:
                return False
            else:
                return False  ## OTHER PROPERTY NOT ABOVE IS NEGLECTED

        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, DepositPoints):
            if self.safe < other.safe:
                return True
            elif self.safe > other.safe:
                return False
            elif self.potential_enemy_collision < other.potential_enemy_collision:
                return True
            elif self.potential_enemy_collision > other.potential_enemy_collision:
                return False
            elif self.potential_ally_collision < other.potential_ally_collision:
                return True
            elif self.potential_ally_collision > other.potential_ally_collision:
                return False
            elif self.cost < other.cost:
                return True
            elif self.cost > other.cost:
                return False
            else:
                return False  ## OTHER PROPERTY NOT ABOVE IS NEGLECTED

        return NotImplemented

    def __repr__(self):
        return "{} safe: {} potential_enemy_collision: {} potential_ally_collision: {} cost: {} direction: {}".format(self.__class__.__name__,
                                                                                           self.safe,
                                                                                           self.potential_enemy_collision,
                                                                                           self.potential_ally_collision,
                                                                                           self.cost,
                                                                                           self.direction)



class HarvestPoints():
    """
    USED TO DETERMINE BEST DIRECTION FOR HARVESTING

    not occupied > least potential enemy collisions > harvest
    HARVEST SHOULD CONSISTS OF: BONUS + HARVEST - COST

    """
    def __init__(self, safe, occupied, potential_enemy_collision, harvest, direction):
        self.safe = safe
        self.occupied = occupied
        self.potential_enemy_collision = potential_enemy_collision
        self.harvest = harvest
        self.direction = direction

    def __gt__(self, other):
        if isinstance(other, HarvestPoints):
            if self.safe > other.safe:
                return True
            elif self.safe < other.safe:
                return False
            elif self.occupied > other.occupied:
                return True
            elif self.occupied < other.occupied:
                return False
            elif self.potential_enemy_collision > other.potential_enemy_collision:
                return True
            elif self.potential_enemy_collision < other.potential_enemy_collision:
                return False
            elif self.harvest > other.harvest:
                return True
            elif self.harvest < other.harvest:
                return False
            else:
                return False  ## OTHER PROPERTY NOT ABOVE IS NEGLECTED

        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, HarvestPoints):
            if self.safe < other.safe:
                return True
            elif self.safe > other.safe:
                return False
            elif self.occupied < other.occupied:
                return True
            elif self.occupied > other.occupied:
                return False
            elif self.potential_enemy_collision < other.potential_enemy_collision:
                return True
            elif self.potential_enemy_collision > other.potential_enemy_collision:
                return False
            elif self.harvest < other.harvest:
                return True
            elif self.harvest > other.harvest:
                return False
            else:
                return False  ## OTHER PROPERTY NOT ABOVE IS NEGLECTED

        return NotImplemented

    def __repr__(self):
        return "{} safe: {} occupied: {} potential_collision: {} harvest: {} direction: {}".format(self.__class__.__name__,
                                                                                                   self.safe,
                                                                                                   self.occupied,
                                                                                                   self.potential_enemy_collision,
                                                                                                   self.harvest,
                                                                                                   self.direction)


class ExplorePoints():
    """
    USED TO DETERMINE BEST DIRECTION FOR EXPLORING
    """
    def __init__(self, safe, occupied, potential_enemy_collision, cost, direction):
        self.safe = safe
        self.occupied = occupied
        self.potential_enemy_collision = potential_enemy_collision
        self.cost = -cost
        self.direction = direction

    def __gt__(self, other):
        if isinstance(other, ExplorePoints):
            if self.safe > other.safe:
                return True
            elif self.safe < other.safe:
                return False
            elif self.occupied > other.occupied:
                return True
            elif self.occupied < other.occupied:
                return False
            elif self.potential_enemy_collision > other.potential_enemy_collision:
                return True
            elif self.potential_enemy_collision < other.potential_enemy_collision:
                return False
            elif self.cost > other.cost:
                return True
            elif self.cost < other.cost:
                return False
            else:
                return False  ## OTHER PROPERTY NOT ABOVE IS NEGLECTED

        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, ExplorePoints):
            if self.safe < other.safe:
                return True
            elif self.safe > other.safe:
                return False
            elif self.occupied < other.occupied:
                return True
            elif self.occupied > other.occupied:
                return False
            elif self.potential_enemy_collision < other.potential_enemy_collision:
                return True
            elif self.potential_enemy_collision > other.potential_enemy_collision:
                return False
            elif self.cost < other.cost:
                return True
            elif self.cost > other.cost:
                return False
            else:
                return False  ## OTHER PROPERTY NOT ABOVE IS NEGLECTED

        return NotImplemented

    def __repr__(self):
        return "{} safe: {} occupied: {} potential_collision: {} cost: {} direction: {}".format(
            self.__class__.__name__,
            self.safe,
            self.occupied,
            self.potential_enemy_collision,
            self.cost,
            self.direction)


class DepartPoints():
    """
    USED TO DETERMINE BEST DIRECTION FOR DEPARTING
    """
    def __init__(self, safe, cost, direction):
        self.safe = safe
        self.cost = -cost
        self.direction = direction

    def __gt__(self, other):
        if isinstance(other, DepartPoints):
            if self.safe > other.safe:
                return True
            elif self.safe < other.safe:
                return False
            if self.cost > other.cost:
                return True
            elif self.cost < other.cost:
                return False
            else:
                return False  ## OTHER PROPERTY NOT ABOVE IS NEGLECTED

        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, DepartPoints):
            if self.safe < other.safe:
                return True
            elif self.safe > other.safe:
                return False
            if self.cost < other.cost:
                return True
            elif self.cost > other.cost:
                return False
            else:
                return False  ## OTHER PROPERTY NOT ABOVE IS NEGLECTED

        return NotImplemented

    def __repr__(self):
        return "{} safe: {} cost: {} direction: {}".format(
            self.__class__.__name__,
            self.safe,
            self.cost,
            self.direction)