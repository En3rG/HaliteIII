
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
        return "{} Ship id: {} distance: {}".format(self.__class__.__name__, self.ship_id, self.distance)


class SupportShip:
    """
    USED TO DETERMINE SUPPORT SHIPS FOR ATTACKING
    """
    def __init__(self, num_support, ship_id, support_ships, directions):
        self.num_support = num_support
        self.ship_id = ship_id
        self.support_ships = support_ships
        self.directions = directions

    def __gt__(self, other):
        if isinstance(other, SupportShip):
            if self.num_support > other.num_support:
                return True
            elif self.num_support < other.num_support:
                return False
            elif self.ship_id >= other.ship_id:
                return True
            elif self.ship_id < other.ship_id:
                return False

        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, SupportShip):
            if self.num_support < other.num_support:
                return True
            elif self.num_support > other.num_support:
                return False
            elif self.ship_id <= other.ship_id:
                return True
            elif self.ship_id > other.ship_id:
                return False

        return NotImplemented

    def __repr__(self):
        return "{} Ship id: {} num_support: {}".format(self.__class__.__name__, self.ship_id, self.num_support)



class ExploreShip:
    """
    USED TO DETERMINE CLOSEST SHIP FOR EXPLORING
    ALSO USED FOR HEAPQ PURPOSES

    NO LONGER USED, USING EXPLORE2 NOW!!!!
    """
    def __init__(self, dist, id, curr_cell, destination, indices_deque, distances_deque):
        self.distance = dist
        self.ship_id = id
        self.curr_cell = curr_cell
        self.destination = destination
        self.indices_deque = indices_deque      ## NO LONGER USED (TIMING OUT)
        self.distances_deque = distances_deque  ## NO LONGER USED (TIMING OUT)

    def __gt__(self, other):
        if isinstance(other, ExploreShip):
            if self.distance > other.distance:
                return True
            elif self.distance < other.distance:
                return False
            elif self.ship_id >= other.ship_id:
                return True
            elif self.ship_id < other.ship_id:
                return False

        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, ExploreShip):
            if self.distance < other.distance:
                return True
            elif self.distance > other.distance:
                return False
            elif self.ship_id <= other.ship_id:
                return True
            elif self.ship_id > other.ship_id:
                return False

        return NotImplemented

    def __repr__(self):
        return "{} Ship id: {} distance: {}".format(self.__class__.__name__, self.ship_id, self.distance)



class ExploreShip2:
    """
    USED TO DETERMINE CLOSEST SHIP FOR EXPLORING WITH HIGHEST
    HALITE HARVEST PER TURN
    """
    def __init__(self, ratio, id, destination, matrix_ratio):
        self.ratio = -ratio  ## NEED HIGHEST RATIO TO BE FIRST IN HEAP
        self.ship_id = id
        self.destination = destination
        self.matrix_ratio = matrix_ratio

    def __gt__(self, other):
        if isinstance(other, ExploreShip2):
            if self.ratio > other.ratio:
                return True
            elif self.ratio < other.ratio:
                return False
            elif self.ship_id >= other.ship_id:
                return True
            elif self.ship_id < other.ship_id:
                return False

        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, ExploreShip2):
            if self.ratio < other.ratio:
                return True
            elif self.ratio > other.ratio:
                return False
            elif self.ship_id <= other.ship_id:
                return True
            elif self.ship_id > other.ship_id:
                return False

        return NotImplemented

    def __repr__(self):
        return "{} Ship id: {} ratio: {}".format(self.__class__.__name__,
                                                 self.ship_id, self.ratio)



class RetreatPoints():
    """
    USED TO DETERMINE BEST DIRECTION FOR RETREAT

    shipyard > not occupied > least potential ally collisions
    """
    def __init__(self, priority_direction, shipyard, safe, stuck, potential_ally_collision, direction):
        self.priority_direction = priority_direction
        self.shipyard = shipyard
        self.safe = safe
        self.stuck = -stuck
        self.potential_ally_collision = potential_ally_collision
        self.direction = direction

    def __gt__(self, other):
        if isinstance(other, RetreatPoints):
            if self.priority_direction > other.priority_direction:
                return True
            elif self.priority_direction < other.priority_direction:
                return False
            elif self.shipyard > other.shipyard:
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
            if self.priority_direction < other.priority_direction:
                return True
            elif self.priority_direction > other.priority_direction:
                return False
            elif self.shipyard < other.shipyard:
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
        return "{} shipyard: {} priority_direction: {} safe: {} stuck: {} potential_ally_collision: {} direction: {}".format(self.__class__.__name__,
                                                                                           self.shipyard,
                                                                                           self.priority_direction,
                                                                                           self.safe,
                                                                                           self.stuck,
                                                                                           self.potential_ally_collision,
                                                                                           self.direction)


class DepositPoints():
    """
    USED TO DETERMINE BEST DIRECTION FOR RETURNING/DEPOSITING

    COMMENTED OUT ALLY COLLISION, WITH IT IT CAUSES A TRAFFIC JAM AT THE DOCK
    """
    def __init__(self, priority_direction, safe, dock, enemy_occupied, potential_enemy_collision, potential_ally_collision, cost, direction):
        self.priority_direction = priority_direction
        self.safe = safe
        self.dock = dock
        self.enemy_occupied = -enemy_occupied
        self.potential_enemy_collision = potential_enemy_collision
        self.potential_ally_collision = potential_ally_collision
        self.cost = -cost  ## NEGATIVE BECAUSE WE WANT THE LEAST COST
        self.direction = direction

    def __gt__(self, other):
        if isinstance(other, DepositPoints):
            if self.priority_direction > other.priority_direction:
                return True
            elif self.priority_direction < other.priority_direction:
                return False
            elif self.safe > other.safe:
                return True
            elif self.safe < other.safe:
                return False
            elif self.dock > other.dock:
                return True
            elif self.dock < other.dock:
                return False
            elif self.enemy_occupied > other.enemy_occupied:
                return True
            elif self.enemy_occupied < other.enemy_occupied:
                return False
            elif self.potential_enemy_collision > other.potential_enemy_collision:
                return True
            elif self.potential_enemy_collision < other.potential_enemy_collision:
                return False
            # elif self.potential_ally_collision > other.potential_ally_collision:
            #     return True
            # elif self.potential_ally_collision < other.potential_ally_collision:
            #     return False
            elif self.cost > other.cost:
                return True
            elif self.cost < other.cost:
                return False
            else:
                return False  ## OTHER PROPERTY NOT ABOVE IS NEGLECTED

        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, DepositPoints):
            if self.priority_direction < other.priority_direction:
                return True
            elif self.priority_direction > other.priority_direction:
                return False
            elif self.safe < other.safe:
                return True
            elif self.safe > other.safe:
                return False
            elif self.dock < other.dock:
                return True
            elif self.dock > other.dock:
                return False
            elif self.enemy_occupied < other.enemy_occupied:
                return True
            elif self.enemy_occupied > other.enemy_occupied:
                return False
            elif self.potential_enemy_collision < other.potential_enemy_collision:
                return True
            elif self.potential_enemy_collision > other.potential_enemy_collision:
                return False
            # elif self.potential_ally_collision < other.potential_ally_collision:
            #     return True
            # elif self.potential_ally_collision > other.potential_ally_collision:
            #     return False
            elif self.cost < other.cost:
                return True
            elif self.cost > other.cost:
                return False
            else:
                return False  ## OTHER PROPERTY NOT ABOVE IS NEGLECTED

        return NotImplemented

    def __repr__(self):
        return "{} priority_direction: {} safe: {} dock: {} enemy_occupied: {} potential_enemy_collision: {} potential_ally_collision: {} cost: {} direction: {}".format(
                                                                                        self.__class__.__name__,
                                                                                        self.priority_direction,
                                                                                        self.safe,
                                                                                        self.dock,
                                                                                        self.enemy_occupied,
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
    def __init__(self, safe, occupied, enemy_occupied, potential_enemy_collision, harvest, direction):
        self.safe = safe
        self.occupied = occupied
        self.enemy_occupied = -enemy_occupied
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
            elif self.enemy_occupied > other.enemy_occupied:
                return True
            elif self.enemy_occupied < other.enemy_occupied:
                return False
            # elif self.potential_enemy_collision > other.potential_enemy_collision:
            #     return True
            # elif self.potential_enemy_collision < other.potential_enemy_collision:
            #     return False
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
            elif self.enemy_occupied < other.enemy_occupied:
                return True
            elif self.enemy_occupied > other.enemy_occupied:
                return False
            # elif self.potential_enemy_collision < other.potential_enemy_collision:
            #     return True
            # elif self.potential_enemy_collision > other.potential_enemy_collision:
            #     return False
            elif self.harvest < other.harvest:
                return True
            elif self.harvest > other.harvest:
                return False
            else:
                return False  ## OTHER PROPERTY NOT ABOVE IS NEGLECTED

        return NotImplemented

    def __repr__(self):
        return "{} safe: {} occupied: {} enemy_occupied: {} potential_collision: {} harvest: {} direction: {}".format(
                                                                                self.__class__.__name__,
                                                                                self.safe,
                                                                                self.occupied,
                                                                                self.enemy_occupied,
                                                                                self.potential_enemy_collision,
                                                                                self.harvest,
                                                                                self.direction)


class ExplorePoints():
    """
    USED TO DETERMINE BEST DIRECTION FOR EXPLORING
    """
    def __init__(self, priority_direction, safe, occupied, potential_enemy_collision, cost, direction):
        self.priority_direction = priority_direction
        self.safe = safe
        self.occupied = occupied
        self.potential_enemy_collision = potential_enemy_collision
        self.cost = -cost
        self.direction = direction

    def __gt__(self, other):
        if isinstance(other, ExplorePoints):
            if self.priority_direction > other.priority_direction:
                return True
            elif self.priority_direction < other.priority_direction:
                return False
            elif self.safe > other.safe:
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
            if self.priority_direction < other.priority_direction:
                return True
            elif self.priority_direction > other.priority_direction:
                return False
            elif self.safe < other.safe:
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
        return "{} priority_direction: {} safe: {} occupied: {} potential_collision: {} cost: {} direction: {}".format(
            self.__class__.__name__,
            self.priority_direction,
            self.safe,
            self.occupied,
            self.potential_enemy_collision,
            self.cost,
            self.direction)


class CollisionPoints():
    """
    USED TO DETERMINE BEST DIRECTION FOR AVOIDING IMMINENT COLLISION
    """
    def __init__(self, safe, occupied, priority_direction, harvest, direction):
        self.safe = safe
        self.occupied = occupied
        self.priority_direction = priority_direction
        self.harvest = harvest
        self.direction = direction

    def __gt__(self, other):
        if isinstance(other, CollisionPoints):
            if self.safe > other.safe:
                return True
            elif self.safe < other.safe:
                return False
            elif self.occupied > other.occupied:
                return True
            elif self.occupied < other.occupied:
                return False
            elif self.priority_direction > other.priority_direction:
                return True
            elif self.priority_direction < other.priority_direction:
                return False
            elif self.harvest > other.harvest:
                return True
            elif self.harvest < other.harvest:
                return False
            else:
                return False  ## OTHER PROPERTY NOT ABOVE IS NEGLECTED

        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, CollisionPoints):
            if self.safe < other.safe:
                return True
            elif self.safe > other.safe:
                return False
            elif self.occupied < other.occupied:
                return True
            elif self.occupied > other.occupied:
                return False
            elif self.priority_direction < other.priority_direction:
                return True
            elif self.priority_direction > other.priority_direction:
                return False
            elif self.harvest < other.harvest:
                return True
            elif self.harvest > other.harvest:
                return False
            else:
                return False  ## OTHER PROPERTY NOT ABOVE IS NEGLECTED

        return NotImplemented

    def __repr__(self):
        return "{} safe: {} occupied: {} priority_direction: {} harvest: {} direction: {}".format(
            self.__class__.__name__,
            self.safe,
            self.occupied,
            self.priority_direction,
            self.harvest,
            self.direction)


class BuildPoints():
    """
    USED TO DETERMINE BEST DIRECTION FOR BUILDING
    """
    def __init__(self, priority_direction, safe, cost, direction):
        self.priority_direction = priority_direction
        self.safe = safe
        self.cost = -cost
        self.direction = direction

    def __gt__(self, other):
        if isinstance(other, BuildPoints):
            if self.priority_direction > other.priority_direction:
                return True
            elif self.priority_direction < other.priority_direction:
                return False
            elif self.safe > other.safe:
                return True
            elif self.safe < other.safe:
                return False
            elif self.cost > other.cost:
                return True
            elif self.cost < other.cost:
                return False
            else:
                return False  ## OTHER PROPERTY NOT ABOVE IS NEGLECTED

        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, BuildPoints):
            if self.priority_direction < other.priority_direction:
                return True
            elif self.priority_direction > other.priority_direction:
                return False
            elif self.safe < other.safe:
                return True
            elif self.safe > other.safe:
                return False
            elif self.cost < other.cost:
                return True
            elif self.cost > other.cost:
                return False
            else:
                return False  ## OTHER PROPERTY NOT ABOVE IS NEGLECTED

        return NotImplemented

    def __repr__(self):
        return "{} priority_direction: {} safe: {} cost: {} direction: {}".format(
            self.__class__.__name__,
            self.priority_direction,
            self.safe,
            self.cost,
            self.direction)


class AttackPoints():
    """
    USED TO DETERMINE BEST DIRECTION FOR ATTACKING
    """
    def __init__(self, priority_direction, safe, direction):
        self.priority_direction = priority_direction
        self.safe = safe
        self.direction = direction

    def __gt__(self, other):
        if isinstance(other, AttackPoints):
            if self.priority_direction > other.priority_direction:
                return True
            elif self.priority_direction < other.priority_direction:
                return False
            elif self.safe > other.safe:
                return True
            elif self.safe < other.safe:
                return False
            else:
                return False  ## OTHER PROPERTY NOT ABOVE IS NEGLECTED

        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, AttackPoints):
            if self.priority_direction < other.priority_direction:
                return True
            elif self.priority_direction > other.priority_direction:
                return False
            elif self.safe < other.safe:
                return True
            elif self.safe > other.safe:
                return False
            else:
                return False  ## OTHER PROPERTY NOT ABOVE IS NEGLECTED

        return NotImplemented

    def __repr__(self):
        return "{} priority_direction: {} safe: {} direction: {}".format(
            self.__class__.__name__,
            self.priority_direction,
            self.safe,
            self.direction)


class SupportPoints():
    """
    USED TO DETERMINE BEST DIRECTION FOR SUPPORTING
    """
    def __init__(self, priority_direction, safe, direction):
        self.priority_direction = priority_direction
        self.safe = safe
        self.direction = direction

    def __gt__(self, other):
        if isinstance(other, SupportPoints):
            if self.priority_direction > other.priority_direction:
                return True
            elif self.priority_direction < other.priority_direction:
                return False
            elif self.safe > other.safe:
                return True
            elif self.safe < other.safe:
                return False
            else:
                return False  ## OTHER PROPERTY NOT ABOVE IS NEGLECTED

        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, SupportPoints):
            if self.priority_direction < other.priority_direction:
                return True
            elif self.priority_direction > other.priority_direction:
                return False
            elif self.safe < other.safe:
                return True
            elif self.safe > other.safe:
                return False
            else:
                return False  ## OTHER PROPERTY NOT ABOVE IS NEGLECTED

        return NotImplemented

    def __repr__(self):
        return "{} priority_direction: {} safe: {} direction: {}".format(
            self.__class__.__name__,
            self.priority_direction,
            self.safe,
            self.direction)

class StartPoints():
    """
    USED TO DETERMINE BEST DIRECTION FOR START GAME
    """

    def __init__(self, safe, hasShip, harvest, direction, canMove=1):
        self.safe = safe        ## NEED FOR BEST DIRECTION (IGNORING)
        self.hasShip = -hasShip
        self.canMove = canMove
        self.harvest = harvest
        self.direction = direction

    def __gt__(self, other):
        if isinstance(other, StartPoints):
            if self.hasShip > other.hasShip:
                return True
            elif self.hasShip < other.hasShip:
                return False
            elif self.canMove > other.canMove:
                return True
            elif self.canMove < other.canMove:
                return False
            elif self.harvest > other.harvest:
                return True
            elif self.harvest < other.harvest:
                return False
            else:
                return False  ## OTHER PROPERTY NOT ABOVE IS NEGLECTED

        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, StartPoints):
            if self.hasShip < other.hasShip:
                return True
            elif self.hasShip > other.hasShip:
                return False
            elif self.canMove < other.canMove:
                return True
            elif self.canMove > other.canMove:
                return False
            elif self.harvest < other.harvest:
                return True
            elif self.harvest > other.harvest:
                return False
            else:
                return False  ## OTHER PROPERTY NOT ABOVE IS NEGLECTED

        return NotImplemented

    def __repr__(self):
        return "{} hasShip: {} canMove: {} harvest: {} direction: {}".format(
            self.__class__.__name__,
            self.hasShip,
            self.canMove,
            self.harvest,
            self.direction)



## NO LONGER USED
# class DepartPoints():
#     """
#     USED TO DETERMINE BEST DIRECTION FOR DEPARTING
#     """
#     def __init__(self, safe, cost, direction):
#         self.safe = safe
#         self.cost = -cost
#         self.direction = direction
#
#     def __gt__(self, other):
#         if isinstance(other, DepartPoints):
#             if self.safe > other.safe:
#                 return True
#             elif self.safe < other.safe:
#                 return False
#             elif self.cost > other.cost:
#                 return True
#             elif self.cost < other.cost:
#                 return False
#             else:
#                 return False  ## OTHER PROPERTY NOT ABOVE IS NEGLECTED
#
#         return NotImplemented
#
#     def __lt__(self, other):
#         if isinstance(other, DepartPoints):
#             if self.safe < other.safe:
#                 return True
#             elif self.safe > other.safe:
#                 return False
#             elif self.cost < other.cost:
#                 return True
#             elif self.cost > other.cost:
#                 return False
#             else:
#                 return False  ## OTHER PROPERTY NOT ABOVE IS NEGLECTED
#
#         return NotImplemented
#
#     def __repr__(self):
#         return "{} safe: {} cost: {} direction: {}".format(
#             self.__class__.__name__,
#             self.safe,
#             self.cost,
#             self.direction)