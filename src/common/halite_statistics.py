from src.common.values import Matrix_val
import logging


class BuildType():
    SHIP = 1
    DOCK = 2


class Ship_stat():
    def __init__(self, id):
        self.id = id
        self.halite_gained = 0
        self.halite_burned = 0
        self.halite_bonus = 0
        self.halite_dropped = 0


    def __repr__(self):
        return "\nShipID: {} gained: {} bonus: {} burned: {} dropped: {}".format(
             self.id, self.halite_gained, self.halite_bonus, self.halite_burned, self.halite_dropped)


class Halite_stats():
    def __init__(self):
        self.ships_stat = {}   ## EACH SHIP ID WILL HAVE Ship_stat AS ITS VALUE
        self.total_gained = 0
        self.total_burned = 0
        self.total_bonus = 0
        self.total_spent = 0
        self.total_dropped = 0


    def __repr__(self):
        output = "\nHalite stats......"
        for id, record in self.ships_stat.items():
            output += str(record)

        output += "\n\nTotal gained: {} || bonus: {} || spent: {} || burned: {} ||  dropped: {}".format(
                    self.total_gained, self.total_bonus, self.total_spent, self.total_burned, self.total_dropped)

        return output


    def record_data(self, ship, destination, data):
        """
        RECORD GAINED/BURNED HALITE

        :param ship:
        :param destination:
        :param data:
        :return:
        """
        self.ships_stat.setdefault(ship.id, Ship_stat(ship.id))  ## IF DOESNT EXIST YET, CREATE THE RECORD WITH ID

        ## HARVESTING
        if ship.position == destination:
            harvest_val = data.matrix.harvest[ship.position.y][ship.position.x]
            self.ships_stat[ship.id].halite_gained += harvest_val
            self.total_gained += harvest_val

            ## CALCULATE BONUS HALITE
            if data.matrix.influenced[ship.position.y][ship.position.x] > Matrix_val.OCCUPIED:
                bonus_val = harvest_val * 2

                self.ships_stat[ship.id].halite_bonus += bonus_val
                self.total_bonus += bonus_val

        ## MOVING, THUS BURNING HALITE
        else:
            burned_val = data.matrix.cost[ship.position.y][ship.position.x]
            self.ships_stat[ship.id].halite_burned += burned_val
            self.total_burned += burned_val


    def record_spent(self, item):
        """
        RECORD BUILT SHIPS OR DOCKS

        :param item: BUILDTYPE OBJECT (SHIP OR DOCK)
        :return:
        """
        """

        """
        if item == BuildType.SHIP:
            self.total_spent += 1000
        elif item == BuildType.DOCK:
            self.total_spent += 4000


    def record_drop(self, ships_died, prev_data):
        """
        RECORD DROPPED HALITE
        GRAB PREVIOUS HALITE AMOUNT IT HAD (NOT CONSIDERING HALITE IT COULD HAVE HARVESTED BEFORE DYING)

        :param ships_died: SET OF SHIP IDs THAT DIED
        :param prev_data:
        :return:
        """
        for ship_id in ships_died:
            ship = prev_data.me._ships.get(ship_id)
            logging.debug("Ship died id: {} Ship: {}".format(ship_id, ship))
            self.ships_stat[ship.id].halite_dropped = ship.halite_amount ## NOT ACCURATE BECAUSE IF SHIP MOVED, WILL BE LESS

            self.total_dropped += ship.halite_amount