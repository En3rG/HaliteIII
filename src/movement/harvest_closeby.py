from hlt.positionals import Direction, Position
import logging
from src.common.moves import Moves
from src.common.values import MyConstants, MoveMode, Matrix_val
from src.common.print import print_heading
from src.common.points import HarvestPoints
from src.common.classes import OrderedSet


"""
TO DO!!!!!!!!


ADD COLLISION PREVENTION


IF BEST IS TO STAY AND HARVEST IS 0, MUST DO SOMETHING ELSE


"""

class Harvest(Moves):
    """
    HARVEST RIGHT NOW OR NEXT TURN
    """
    def __init__(self, data, prev_data):
        super().__init__(data, prev_data)

        self.ships_kicked_temp = OrderedSet()
        self.move_ships()


    def move_ships(self):
        print_heading("Moving harvesting (now) ships......")
        ## MOVE SHIPS (THAT WILL HARVEST NOW)
        for ship_id in (self.data.mySets.ships_all & self.data.mySets.ships_to_move):
            self.check_harvestNow(ship_id)


        print_heading("Moving harvesting (later) ships......")
        ## COMMENTING OUT BECAUSE WE WANT TO EXPLORE INSTEAD
        ## COMMENTING THIS OUT CAUSED A BIG DROP IN RATING
        ## MOVE SHIPS (THAT WILL HARVEST NEXT TURN)
        ships = (self.data.mySets.ships_all & self.data.mySets.ships_to_move) ## SAVING SINCE ships_to_move WILL BE UPDATED DURING ITERATION
        for ship_id in ships:
            ## MOVE KICKED SHIPS FIRST (IF ANY)
            while self.data.mySets.ships_kicked:
                ship_kicked = self.data.mySets.ships_kicked.pop()
                self.check_harvestLater(ship_kicked, kicked=True)

            ## DOUBLE CHECK SHIP IS STILL IN SHIPS TO MOVE
            if ship_id in self.data.mySets.ships_to_move:
                self.check_harvestLater(ship_id)

        ## MERGE TEMP BACK TO SHIPS KICKED
        ## UNION WITH ships_to_move IN CASE SHIP MOVED
        self.data.mySets.ships_kicked.update(self.ships_kicked_temp & self.data.mySets.ships_to_move)


    def check_harvestNow(self, ship_id):
        """
        CHECK IF SHIP WILL HARVEST NOW, IF SO, MOVE IT
        """
        ship = self.data.game.me._ships.get(ship_id)

        # direction = self.get_highest_harvest_move(ship)
        direction = self.best_direction(ship, mode=MoveMode.HARVEST)
        if self.isHarvestingNow(direction, ship):
            self.move_mark_unsafe(ship, direction)


    def isHarvestingNow(self, direction, ship):
        """
        CHECK IF SHIP IS HARVESTING NOW
        """
        ## USING DONT HARVEST BELOW
        # if direction == Direction.Still and \
        #         (self.data.myMatrix.halite.harvest[ship.position.y][ship.position.x] > MyConstants.DONT_HARVEST_BELOW or self.isBlocked(ship)):
        #     return True

        ## USING PERCENTAGE BASED ON AVERAGE HALITE
        # if direction == Direction.Still and \
        #         (self.data.myMatrix.halite.harvest[ship.position.y][ship.position.x] > (MyConstants.DONT_HARVEST_PERCENT * self.data.myVars.average_halite) or self.isBlocked(ship)):
        #     return True

        ## USING PERCENTILE
        if direction == Direction.Still and \
                (self.data.myMatrix.halite.harvest_with_bonus[ship.position.y][ship.position.x] >= self.data.myVars.harvest_percentile or self.isBlocked(ship)):
            return True


    def check_harvestLater(self, ship_id, kicked=False):
        """
        CHECK IF WILL HARVEST LATER, IF SO, MOVE IT
        """
        ship = self.data.game.me._ships.get(ship_id)

        # direction = self.get_highest_harvest_move(ship)
        direction = self.best_direction(ship, mode=MoveMode.HARVEST)
        if self.isHarvestingLater(ship, direction):
            self.move_mark_unsafe(ship, direction)

        elif kicked: ## IF NOT A GOOD HARVEST AND KICKED, ADD TO TEMP TO BE MOVED LATER FOR EXPLORE
            self.ships_kicked_temp.add(ship_id)


    def isHarvestingLater(self, ship, direction):
        """
        CHECKS IF THE DESTINATION HAVE A POTENTIAL HARVEST ABOVE THE THRESHOLD

        :param ship:
        :param direction:
        :return: TRUE/FALSE
        """
        destination = self.get_destination(ship, direction)

        ## USING DONT HARVEST BELOW
        # return (self.data.myMatrix.halite.harvest[destination.y][destination.x] > MyConstants.DONT_HARVEST_BELOW
        #         and self.data.myMatrix.locations.occupied[destination.y][destination.x] > Matrix_val.OCCUPIED)

        ## USING PERCENTAGE BASED ON AVERAGE HALITE
        # return (self.data.myMatrix.halite.harvest[destination.y][destination.x] > (MyConstants.DONT_HARVEST_PERCENT * self.data.myVars.average_halite)
        #         and self.data.myMatrix.locations.occupied[destination.y][destination.x] > Matrix_val.OCCUPIED)

        ## USING PERCENTILE
        return (self.data.myMatrix.halite.harvest_with_bonus[destination.y][destination.x] >= self.data.myVars.harvest_percentile
                and self.data.myMatrix.locations.occupied[destination.y][destination.x] > Matrix_val.OCCUPIED)


    def get_move_points_harvest(self, ship):
        """
        GET POINTS FOR HARVESTING

        :param ship:
        :param directions: DIRECTIONS TO CONSIDER
        :return:
        """
        points = []
        leave_cost, harvest_stay = self.get_harvest(ship, Direction.Still)
        self.set_points(ship, Direction.Still, harvest_stay, points)

        for direction in MyConstants.DIRECTIONS:
            cost, harvest = self.get_harvest(ship, direction, leave_cost, harvest_stay)
            self.set_points(ship, direction, harvest, points)

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


    def set_points(self, ship, direction, harvest, points):
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

        c = HarvestPoints(safe, occupied, enemy_occupied, potential_enemy_collision, harvest, direction)
        points.append(c)


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












