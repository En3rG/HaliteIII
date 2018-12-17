from src.common.move.moves import Moves
from src.common.move.harvests import Harvests
from src.common.print import print_heading
from src.common.classes import OrderedSet
from src.common.values import MyConstants


"""
TO DO!!!!!!!!


ADD COLLISION PREVENTION


IF BEST IS TO STAY AND HARVEST IS 0, MUST DO SOMETHING ELSE


"""

class Harvest(Moves, Harvests):
    """
    HARVEST RIGHT NOW OR NEXT TURN
    """
    def __init__(self, data, prev_data):
        Moves.__init__(self, data, prev_data)

        self.ships_kicked_temp = OrderedSet()
        self.move_ships()


    def move_ships(self):
        print_heading("Moving harvesting (now) ships......")
        ## MOVE SHIPS (THAT WILL HARVEST NOW)
        for ship_id in (self.data.mySets.ships_all & self.data.mySets.ships_to_move):
            self.check_harvestNow(ship_id)

        print_heading("Moving harvesting (later) ships......")
        ## MOVE SHIPS (THAT WILL HARVEST NEXT TURN)
        # ships = (self.data.mySets.ships_all & self.data.mySets.ships_to_move) ## SAVING SINCE ships_to_move WILL BE UPDATED DURING ITERATION
        # for ship_id in ships:
        #     ## MOVE KICKED SHIPS FIRST (IF ANY)
        #     while self.data.mySets.ships_kicked:
        #         ship_kicked = self.data.mySets.ships_kicked.pop()
        #         self.check_harvestLater(ship_kicked, MyConstants.DIRECTIONS, kicked=True)
        #
        #     ## DOUBLE CHECK SHIP IS STILL IN SHIPS TO MOVE
        #     if ship_id in self.data.mySets.ships_to_move:
        #         self.check_harvestLater(ship_id, MyConstants.DIRECTIONS)
        #
        # ## MERGE TEMP BACK TO SHIPS KICKED
        # ## UNION WITH ships_to_move IN CASE SHIP MOVED
        # self.data.mySets.ships_kicked.update(self.ships_kicked_temp & self.data.mySets.ships_to_move)












