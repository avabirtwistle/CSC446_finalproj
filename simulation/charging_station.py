class Charging_Station:
    def __init__(self, position):
        # follow the algorityhm of assignment 1, prioritizing fast chargers
        self.position = position
        self.num_in_queue = 0
        self.fast_charger_status = 0
        self.slow_charger_status = 0

    def arrival(self):
        pass
        # check if both cargers are busy add to queue
        # or service them and schedule departure

    def departure(self):
        pass
        # check if queue is empty
        # if not empty, service next car in queue
