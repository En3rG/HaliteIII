
class Build():
    SHIP = 1
    DOCK = 2

class Ship_stat():
    def __init__(self, id):
        self.id = id
        self.halite_gained = 0
        self.halite_burned = 0
        self.halite_bonus = 0

    def __repr__(self):
        return "\nShipID: {} gained: {} burned: {} bonus: {}".format(
             self.id, self.halite_gained, self.halite_burned, self.halite_bonus)

class Halite_stats():
    def __init__(self):
        self.ships_stat = {}
        self.total_gained = 0
        self.total_burned = 0
        self.total_bonus = 0
        self.total_spent = 0
        self.total_dropped = 0

    def __repr__(self):
        output = "\nHalite stats......"
        for id, record in self.ships_stat.items():
            output += str(record)

        output += "\n\nTotal gained: {} || spent: {} || burned: {} ||  bonus: {} dropped: {}".format(
                    self.total_gained, self.total_spent, self.total_burned, self.total_bonus, self.total_dropped)

        return output


    def record_data(self, ship, destination, data):
        """
        RECORD GAINED/BURNED HALITE

        :param ship:
        :param destination:
        :return:
        """
        self.ships_stat.setdefault(ship.id, Ship_stat(ship.id))  ## IF DOESNT EXIST YET, CREATE THE RECORD WITH ID

        if ship.position == destination:  ## HARVESTING
            harvest_val = data.matrix.harvest[ship.position.y][ship.position.x]
            self.ships_stat[ship.id].halite_gained += harvest_val
            self.total_gained += harvest_val

        else: ## MOVING, THUS BURNING HALITE
            burned_val = data.matrix.cost[ship.position.y][ship.position.x]
            self.ships_stat[ship.id].halite_burned += burned_val
            self.total_burned += burned_val

    def record_spent(self, item):
        """
        RECORD BUILT SHIPS OR DOCKS

        :param item: BUILD OBJECT (SHIP OR DOCK)
        :return:
        """
        """

        """
        if item == Build.SHIP:
            self.total_spent += 1000
        elif item == Build.DOCK:
            self.total_spent += 4000
