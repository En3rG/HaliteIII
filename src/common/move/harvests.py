from hlt.positionals import Direction, Position
import logging
from src.common.points import HarvestPoints
from src.common.values import MyConstants, MoveMode, Matrix_val


class Harvests():
    def check_harvestNow(self, ship_id, moveNow=True, avoid_enemy=True, avoid_potential_enemy=True):
        """
        CHECK IF SHIP WILL HARVEST NOW, IF SO, MOVE IT
        """
        harvesting = False
        ship = self.data.game.me._ships.get(ship_id)

        # direction = self.get_highest_harvest_move(ship)
        direction = self.best_direction(ship, MyConstants.DIRECTIONS, mode=MoveMode.HARVEST, avoid_enemy=avoid_enemy, avoid_potential_enemy=avoid_potential_enemy)
        if self.isHarvestingNow(direction, ship):
            harvesting = True
            if moveNow: self.move_mark_unsafe(ship, direction)

        return harvesting, direction


    def isHarvestingNow(self, direction, ship):
        """
        CHECK IF SHIP IS HARVESTING NOW
        """
        ## USING PERCENTILE
        if direction == Direction.Still and \
                (self.data.myMatrix.halite.harvest_with_bonus[ship.position.y][ship.position.x] >= self.data.myVars.harvest_percentile or self.isBlocked(ship)):
            return True


    def check_harvestLater(self, ship_id, directions, kicked=False, moveNow=True, avoid_enemy=True, avoid_potential_enemy=True):
        """
        CHECK IF WILL HARVEST LATER, IF SO, MOVE IT
        """
        harvesting = False
        ship = self.data.game.me._ships.get(ship_id)

        # direction = self.get_highest_harvest_move(ship)
        direction = self.best_direction(ship, directions, mode=MoveMode.HARVEST, avoid_enemy=avoid_enemy, avoid_potential_enemy=avoid_potential_enemy)
        if self.isHarvestingLater(ship, direction):
            harvesting = True
            if moveNow: self.move_mark_unsafe(ship, direction)

        elif kicked:  ## IF NOT A GOOD HARVEST AND KICKED, ADD TO TEMP TO BE MOVED LATER FOR EXPLORE
            self.ships_kicked_temp.add(ship_id)

        return harvesting, direction


    def isHarvestingLater(self, ship, direction):
        """
        CHECKS IF THE DESTINATION HAVE A POTENTIAL HARVEST ABOVE THE THRESHOLD

        :param ship:
        :param direction:
        :return: TRUE/FALSE
        """
        destination = self.get_destination(ship, direction)

        ## USING PERCENTILE
        return (self.data.myMatrix.halite.harvest_with_bonus[destination.y][destination.x] >= self.data.myVars.harvest_percentile
                and self.data.myMatrix.locations.occupied[destination.y][destination.x] > Matrix_val.OCCUPIED)


    def isBlocked(self, ship):
        """
        IF ALL 4 DIRECTIONS ARE NOT SAFE

        :return:
        """
        unsafe_num = 0
        for direction in MyConstants.DIRECTIONS:
            destination = self.get_destination(ship, direction)
            if self.data.myMatrix.locations.safe[destination.y][destination.x] == -1: unsafe_num += 1

        return unsafe_num == 4


    def get_move_points_harvest(self, ship, directions, avoid_enemy, avoid_potential_enemy):
        """
        GET POINTS FOR HARVESTING

        :param ship:
        :param directions: DIRECTIONS TO CONSIDER
        :return:
        """
        points = []
        leave_cost, harvest_stay = self.get_harvest(ship, Direction.Still)
        self.set_harvestPoints(ship, Direction.Still, harvest_stay, points, avoid_enemy, avoid_potential_enemy)

        for direction in directions:
            cost, harvest = self.get_harvest(ship, direction, leave_cost, harvest_stay)
            self.set_harvestPoints(ship, direction, harvest, points, avoid_enemy, avoid_potential_enemy)

        logging.debug(points)

        return points

    def get_harvest(self, ship, direction, leave_cost=None, harvest_stay=None):
        """
        HARVEST SHOULD CONSISTS OF: BONUS + HARVEST - COST

        :return: COST AND HARVEST AMOUNT
        """
        destination = self.get_destination(ship, direction)
        harvest_with_bonus = self.data.myMatrix.halite.harvest_with_bonus[destination.y][destination.x]
        cost = self.data.myMatrix.halite.cost[destination.y][destination.x]

        if direction != Direction.Still:
            twoTurn_harvest = harvest_stay + harvest_stay * 0.75  ## SECOND HARVEST IS 0.75 OF FIRST HARVEST
            harvest_with_bonus = harvest_with_bonus - leave_cost - twoTurn_harvest

        return cost, harvest_with_bonus


    def set_harvestPoints(self, ship, direction, harvest, points, avoid_enemy, avoid_potential_enemy):
        """
        GATHER POINTS WITH DIRECTION PROVIDED

        :param direction:
        :param harvest:
        :return:
        """
        destination = self.get_destination(ship, direction)
        safe = self.data.myMatrix.locations.safe[destination.y][destination.x]
        potential_enemy_collision = self.data.myMatrix.locations.potential_enemy_collisions[destination.y][destination.x]
        occupied = 0 if self.data.myMatrix.locations.occupied[destination.y][destination.x] >= -1 else -1
        enemy_occupied = self.data.myMatrix.locations.enemyShips[destination.y][destination.x]

        c = HarvestPoints(safe, occupied, enemy_occupied, potential_enemy_collision, harvest, direction, self.data,
                          avoid_enemy, avoid_potential_enemy)
        points.append(c)