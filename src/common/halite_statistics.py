
class Record():
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
        self.records = {}
        self.total_gained = 0
        self.total_burned = 0
        self.total_bonus = 0

    def __repr__(self):
        output = "\nHalite stats......"
        for id, record in self.records.items():
            output += str(record)

        output += "\n\nTotal gained: {} burned: {} bonsu: {}".format(self.total_gained, self.total_burned, self.total_bonus)

        return output


    def record_data(self, ship, destination, data):
        """
        RECORD GAINED/BURNED HALITE

        :param ship:
        :param destination:
        :return:
        """
        self.records.setdefault(ship.id, Record(ship.id))  ## IF DOESNT EXIST YET, CREATE THE RECORD WITH ID

        if ship.position == destination:  ## HARVESTING
            harvest_val = data.matrix.harvest[ship.position.y][ship.position.x]
            self.records[ship.id].halite_gained += harvest_val
            self.total_gained += harvest_val

        else: ## MOVING, THUS BURNING HALITE
            burned_val = data.matrix.cost[ship.position.y][ship.position.x]
            self.records[ship.id].halite_burned += burned_val
            self.total_burned += burned_val
