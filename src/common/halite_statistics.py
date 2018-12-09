from src.common.values import Matrix_val
import logging


class BuildType():
    SHIP = 1
    DOCK = 2


class Ship_stat():
    """
    TRACKS HALITE STATS PER SHIP
    """
    def __init__(self, id):
        self.id = id
        self.halite_amount = 0
        self.halite_gained = 0
        self.halite_burned = 0
        self.halite_bonus = 0
        self.halite_dropped = 0

    def set_halite(self, halite_amount):
        self.halite_amount = halite_amount

    def __repr__(self):
        return "\nShipID: {} halite_amount: {} gained: {} bonus: {} burned: {} dropped: {}".format(
             self.id, self.halite_amount, self.halite_gained, self.halite_bonus, self.halite_burned, self.halite_dropped)


class Halite_stats():
    """
    TRACKS HALITE STATS OF THE ENTIRE GAME
    """
    def __init__(self):
        self.ships_stat = {}        ## EACH SHIP ID WILL HAVE Ship_stat AS ITS VALUE
        self.halite_amount = 0
        self.halite_carried = 0
        self.total_gained = 0
        self.total_burned = 0
        self.total_bonus = 0
        self.total_spent = 0
        self.total_dropped = 0
        self.enemy_stat = {}


    def set_halite(self, game, data):
        self.halite_amount = game.me.halite_amount
        self.halite_carried = data.myDicts.players_halite[game.my_id].halite_carried

        self.enemy_stat = {}
        for id, v in data.myDicts.players_halite.items():
            if id != game.me.id:
                self.enemy_stat[id] = {"halite amount":v.halite_amount, "halite carried":v.halite_carried}


    def __repr__(self):
        output = "\n\nHalite stats......"
        for id, record in self.ships_stat.items():
            output += str(record)

        output += "\n\nHalite: {} || Carrying: {} || Total gained: {} || bonus: {} || spent: {} || burned: {} ||  dropped: {}\n enemy_stat: {}"\
                    .format(self.halite_amount,
                            self.halite_carried,
                            self.total_gained,
                            self.total_bonus,
                            self.total_spent,
                            self.total_burned,
                            self.total_dropped,
                            self.enemy_stat)

        return output


    def record_data(self, ship, destination, data):
        """
        RECORD GAINED/BURNED HALITE

        :param ship:
        :param destination:
        :param data: DATA THAT IS UPDATED
        :return:
        """
        self.ships_stat.setdefault(ship.id, Ship_stat(ship.id))  ## IF DOESNT EXIST YET, CREATE THE RECORD WITH ID
        self.ships_stat[ship.id].set_halite(ship.halite_amount)

        ## HARVESTING
        if ship.position == destination:
            harvest_val = data.myMatrix.halite.harvest[ship.position.y][ship.position.x]
            self.ships_stat[ship.id].halite_gained += harvest_val
            self.total_gained += harvest_val

            ## CALCULATE BONUS HALITE
            if data.myMatrix.locations.influenced[ship.position.y][ship.position.x] > Matrix_val.ONE:
                bonus_val = harvest_val * 2

                self.ships_stat[ship.id].halite_bonus += bonus_val
                self.total_bonus += bonus_val

        ## MOVING, THUS BURNING HALITE
        else:
            burned_val = data.myMatrix.halite.cost[ship.position.y][ship.position.x]
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
            self.ships_stat[ship.id].set_halite(0)

            self.total_dropped += ship.halite_amount
