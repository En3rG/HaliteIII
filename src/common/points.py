
class FarthestShip:
    """
    USED TO DETERMINE FARTHEST SHIP FOR RETREAT/RETURNING
    ALSO USED FOR HEAPQ PURPOSES

    distance > num_directions > ship_id
    """
    def __init__(self, dist, num_directions, id, directions, dock_position):
        self.distance = dist
        self.num_directions = num_directions
        self.ship_id = id
        self.directions = directions
        self.dock_position = dock_position

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




class BuildShip:
    """
    USED TO DETERMINE CLOSEST SHIP FOR BUILDING WITH HIGHEST HALITE
    """
    def __init__(self, cargo, id):
        self.cargo = -cargo
        self.ship_id = id

    def __gt__(self, other):
        if isinstance(other, BuildShip):
            if self.cargo >= other.cargo:
                return True
            elif self.cargo < other.cargo:
                return False
            elif self.ship_id >= other.ship_id:
                return True
            elif self.ship_id < other.ship_id:
                return False

        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, BuildShip):
            if self.cargo <= other.cargo:
                return True
            elif self.cargo > other.cargo:
                return False
            elif self.ship_id <= other.ship_id:
                return True
            elif self.ship_id > other.ship_id:
                return False

        return NotImplemented

    def __repr__(self):
        return "{} Ship id: {} cargo: {}".format(self.__class__.__name__,
                                                           self.ship_id,
                                                           self.cargo)


class ExploreShip:
    """
    USED TO DETERMINE CLOSEST SHIP FOR EXPLORING WITH HIGHEST
    HALITE HARVEST PER TURN
    """
    def __init__(self, ratio, cargo, id, destination, matrix_ratio):
        self.ratio = -ratio  ## NEED HIGHEST RATIO TO BE FIRST IN HEAP
        self.cargo = cargo
        self.ship_id = id
        self.destination = destination
        self.matrix_ratio = matrix_ratio

    def __gt__(self, other):
        if isinstance(other, ExploreShip):
            if self.ratio > other.ratio:
                return True
            elif self.ratio < other.ratio:
                return False
            elif self.cargo >= other.cargo:
                return True
            elif self.cargo < other.cargo:
                return False
            elif self.ship_id >= other.ship_id:
                return True
            elif self.ship_id < other.ship_id:
                return False

        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, ExploreShip):
            if self.ratio < other.ratio:
                return True
            elif self.ratio > other.ratio:
                return False
            elif self.cargo <= other.cargo:
                return True
            elif self.cargo > other.cargo:
                return False
            elif self.ship_id <= other.ship_id:
                return True
            elif self.ship_id > other.ship_id:
                return False

        return NotImplemented

    def __repr__(self):
        return "{} Ship id: {} ratio: {} cargo: {}".format(self.__class__.__name__,
                                                           self.ship_id,
                                                           self.ratio,
                                                           self.cargo)


class KamikazeShip:
    """
    USED TO DETERMINE CLOSEST SHIP WITH LOWEST CARGO TO KAMIKAZE HARVEST (POTENTIALLY)
    """
    def __init__(self, cargo, id, support_ships, explore_destination):
        self.cargo = cargo
        self.ship_id = id
        self.explore_destination = explore_destination
        self.support_ships = support_ships

    def __gt__(self, other):
        if isinstance(other, KamikazeShip):
            if self.cargo >= other.cargo:
                return True
            elif self.cargo < other.cargo:
                return False
            elif self.ship_id >= other.ship_id:
                return True
            elif self.ship_id < other.ship_id:
                return False

        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, KamikazeShip):
            if self.cargo <= other.cargo:
                return True
            elif self.cargo > other.cargo:
                return False
            elif self.ship_id <= other.ship_id:
                return True
            elif self.ship_id > other.ship_id:
                return False

        return NotImplemented

    def __repr__(self):
        return "{} Ship id: {} cargo: {} support_ships {}".format(self.__class__.__name__,
                                                           self.ship_id,
                                                           self.cargo,
                                                           self.support_ships)



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
                return False

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
                return False

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

    COMMENTED OUT ALLY COLLISION, WITH IT IT CAUSES A TRAFFIC JAM AT THE DOCK
    """
    def __init__(self, safe, dock, enemy_occupied, potential_enemy_collision, potential_ally_collision,
                 cost, direction, avoid_enemy, avoid_potential_enemy):
        self.safe = safe
        self.dock = dock
        self.enemy_occupied = -enemy_occupied
        self.potential_enemy_collision = potential_enemy_collision
        self.potential_ally_collision = potential_ally_collision
        self.cost = -cost                                                                                               ## NEGATIVE BECAUSE WE WANT THE LEAST COST
        self.direction = direction
        self.avoid_enemy = avoid_enemy
        self.avoid_potential_enemy = avoid_potential_enemy

    def __gt__(self, other):
        if isinstance(other, DepositPoints):
            if self.safe > other.safe:
                return True
            elif self.safe < other.safe:
                return False
            elif self.dock > other.dock:
                return True
            elif self.dock < other.dock:
                return False
            elif self.enemy_occupied > other.enemy_occupied and self.avoid_enemy:
                return True
            elif self.enemy_occupied < other.enemy_occupied and self.avoid_enemy:
                return False
            elif self.potential_enemy_collision > other.potential_enemy_collision and self.avoid_potential_enemy:
                return True
            elif self.potential_enemy_collision < other.potential_enemy_collision and self.avoid_potential_enemy:
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
                return False

        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, DepositPoints):
            if self.safe < other.safe:
                return True
            elif self.safe > other.safe:
                return False
            elif self.dock < other.dock:
                return True
            elif self.dock > other.dock:
                return False
            elif self.enemy_occupied < other.enemy_occupied and self.avoid_enemy:
                return True
            elif self.enemy_occupied > other.enemy_occupied and self.avoid_enemy:
                return False
            elif self.potential_enemy_collision < other.potential_enemy_collision and self.avoid_potential_enemy:
                return True
            elif self.potential_enemy_collision > other.potential_enemy_collision and self.avoid_potential_enemy:
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
                return False

        return NotImplemented

    def __repr__(self):
        return "{} safe: {} dock: {} enemy_occupied: {} potential_enemy_collision: {} potential_ally_collision: {} " \
               "cost: {} direction: {} avoid_enemy {} avoid_potential_enemy {}".format(
                                                                                        self.__class__.__name__,
                                                                                        self.safe,
                                                                                        self.dock,
                                                                                        self.enemy_occupied,
                                                                                        self.potential_enemy_collision,
                                                                                        self.potential_ally_collision,
                                                                                        self.cost,
                                                                                        self.direction,
                                                                                        self.avoid_enemy,
                                                                                        self.avoid_potential_enemy)


class HarvestPoints():
    """
    USED TO DETERMINE BEST DIRECTION FOR HARVESTING

    not occupied > least potential enemy collisions > harvest
    HARVEST SHOULD CONSISTS OF: BONUS + HARVEST - COST

    """
    def __init__(self, safe, occupied, enemy_occupied, potential_enemy_collision, harvest, direction, data,
                 avoid_enemy, avoid_potential_enemy):
        self.safe = safe
        self.occupied = occupied
        self.enemy_occupied = -enemy_occupied
        self.potential_enemy_collision = potential_enemy_collision
        self.harvest = harvest
        self.direction = direction
        self.data = data
        self.avoid_enemy = avoid_enemy
        self.avoid_potential_enemy = avoid_potential_enemy

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
            elif self.enemy_occupied > other.enemy_occupied and self.avoid_enemy:
                return True
            elif self.enemy_occupied < other.enemy_occupied  and self.avoid_enemy:
                return False
            elif self.potential_enemy_collision > other.potential_enemy_collision and self.avoid_potential_enemy:
                return True
            elif self.potential_enemy_collision < other.potential_enemy_collision and self.avoid_potential_enemy:
                return False
            elif self.harvest > other.harvest:
                return True
            elif self.harvest < other.harvest:
                return False
            else:
                return False

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
            elif self.enemy_occupied < other.enemy_occupied and self.avoid_enemy:
                return True
            elif self.enemy_occupied > other.enemy_occupied and self.avoid_enemy:
                return False
            elif self.potential_enemy_collision < other.potential_enemy_collision and self.avoid_potential_enemy:
                return True
            elif self.potential_enemy_collision > other.potential_enemy_collision and self.avoid_potential_enemy:
                return False
            elif self.harvest < other.harvest:
                return True
            elif self.harvest > other.harvest:
                return False
            else:
                return False

        return NotImplemented

    def __repr__(self):
        return "{} safe: {} occupied: {} enemy_occupied: {} potential_collision: {} harvest: {} direction: {} " \
               "avoid_enemy {} avoid_potential_enemy {}".format(
                                                                                self.__class__.__name__,
                                                                                self.safe,
                                                                                self.occupied,
                                                                                self.enemy_occupied,
                                                                                self.potential_enemy_collision,
                                                                                self.harvest,
                                                                                self.direction,
                                                                                self.avoid_enemy,
                                                                                self.avoid_potential_enemy)


class ExplorePoints():
    """
    USED TO DETERMINE BEST DIRECTION FOR EXPLORING
    """
    def __init__(self, safe, occupied, enemy_occupied, potential_enemy_collision, cost, direction, data,
                 avoid_enemy, avoid_potential_enemy):
        self.safe = safe
        self.occupied = occupied
        self.enemy_occupied = -enemy_occupied
        self.potential_enemy_collision = potential_enemy_collision
        self.cost = -cost
        self.direction = direction
        self.data = data
        self.avoid_enemy = avoid_enemy
        self.avoid_potential_enemy = avoid_potential_enemy


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
            elif self.enemy_occupied > other.enemy_occupied and self.avoid_enemy:
                return True
            elif self.enemy_occupied < other.enemy_occupied and self.avoid_enemy:
                return False
            elif self.potential_enemy_collision > other.potential_enemy_collision and self.avoid_potential_enemy:
                return True
            elif self.potential_enemy_collision < other.potential_enemy_collision and self.avoid_potential_enemy:
                return False
            elif self.cost > other.cost:
                return True
            elif self.cost < other.cost:
                return False
            else:
                return False

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
            elif self.enemy_occupied < other.enemy_occupied and self.avoid_enemy:
                return True
            elif self.enemy_occupied > other.enemy_occupied and self.avoid_enemy:
                return False
            elif self.potential_enemy_collision < other.potential_enemy_collision and self.avoid_potential_enemy:
                return True
            elif self.potential_enemy_collision > other.potential_enemy_collision and self.avoid_potential_enemy:
                return False
            elif self.cost < other.cost:
                return True
            elif self.cost > other.cost:
                return False
            else:
                return False

        return NotImplemented

    def __repr__(self):
        return "{} safe: {} occupied: {} enemy_occupied: {} potential_collision: {} cost: {} direction: {} " \
               "avoid_enemy {} avoid_potential_enemy {}".format(
            self.__class__.__name__,
            self.safe,
            self.occupied,
            self.enemy_occupied,
            self.potential_enemy_collision,
            self.cost,
            self.direction,
            self.avoid_enemy,
            self.avoid_potential_enemy)


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
                return False

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
                return False

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
    def __init__(self, safe, enemy_occupied, potential_enemy_collision, cost, direction,
                 avoid_enemy, avoid_potential_enemy):
        self.safe = safe
        self.enemy_occupied = -enemy_occupied
        self.potential_enemy_collision = potential_enemy_collision
        self.cost = -cost
        self.direction = direction
        self.avoid_enemy = avoid_enemy
        self.avoid_potential_enemy = avoid_potential_enemy

    def __gt__(self, other):
        if isinstance(other, BuildPoints):
            if self.safe > other.safe:
                return True
            elif self.safe < other.safe:
                return False
            elif self.enemy_occupied > other.enemy_occupied and self.avoid_enemy:
                return True
            elif self.enemy_occupied < other.enemy_occupied and self.avoid_enemy:
                return False
            elif self.potential_enemy_collision > other.potential_enemy_collision and self.avoid_potential_enemy:
                return True
            elif self.potential_enemy_collision < other.potential_enemy_collision and self.avoid_potential_enemy:
                return False
            elif self.cost > other.cost:
                return True
            elif self.cost < other.cost:
                return False
            else:
                return False

        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, BuildPoints):
            if self.safe < other.safe:
                return True
            elif self.safe > other.safe:
                return False
            elif self.enemy_occupied < other.enemy_occupied and self.avoid_enemy:
                return True
            elif self.enemy_occupied > other.enemy_occupied and self.avoid_enemy:
                return False
            elif self.potential_enemy_collision < other.potential_enemy_collision and self.avoid_potential_enemy:
                return True
            elif self.potential_enemy_collision > other.potential_enemy_collision and self.avoid_potential_enemy:
                return False
            elif self.cost < other.cost:
                return True
            elif self.cost > other.cost:
                return False
            else:
                return False

        return NotImplemented

    def __repr__(self):
        return "{} safe: {} cost: {} direction: {} avoid_enemy {} avoid_potential_enemy {}".format(
            self.__class__.__name__,
            self.safe,
            self.cost,
            self.direction,
            self.avoid_enemy,
            self.avoid_potential_enemy)


class AttackPoints():
    """
    USED TO DETERMINE BEST DIRECTION FOR ATTACKING
    """
    def __init__(self, safe, direction):
        self.safe = safe
        self.direction = direction

    def __gt__(self, other):
        if isinstance(other, AttackPoints):
            if self.safe > other.safe:
                return True
            elif self.safe < other.safe:
                return False
            else:
                return False

        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, AttackPoints):
            if self.safe < other.safe:
                return True
            elif self.safe > other.safe:
                return False
            else:
                return False

        return NotImplemented

    def __repr__(self):
        return "{} safe: {} direction: {}".format(
            self.__class__.__name__,
            self.safe,
            self.direction)


class SupportPoints():
    """
    USED TO DETERMINE BEST DIRECTION FOR SUPPORTING
    """
    def __init__(self, safe, direction):
        self.safe = safe
        self.direction = direction

    def __gt__(self, other):
        if isinstance(other, SupportPoints):
            if self.safe > other.safe:
                return True
            elif self.safe < other.safe:
                return False
            else:
                return False

        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, SupportPoints):
            if self.safe < other.safe:
                return True
            elif self.safe > other.safe:
                return False
            else:
                return False

        return NotImplemented

    def __repr__(self):
        return "{} safe: {} direction: {}".format(
            self.__class__.__name__,
            self.safe,
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