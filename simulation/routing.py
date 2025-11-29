

class Routing:
    def __init__(self, car, routing_policy):
        self.station_arrival_time = None # time car arrives at station, none indicates in queue or driving
        self.queue_entry_time = None # time car enters queue at station, none indicates not in queue
        self.station_routed_to = None # the station meta or station not sure