# charging_station.py
import numpy as np
from event import EventType

class Charging_Station:
    def __init__(self, station_id, position, time_next_event, sim_time):
        self.station_id = station_id
        self.position = position
        self.time_next_event = time_next_event
        self.sim_time = sim_time           

        self.num_in_queue = 0
        self.fast_charger_status = 0  # 0 idle, 1 busy
        self.slow_charger_status = 0

        # Map departures to event types
        self.depart_fast_event = {
            1: EventType.DEPARTURE_STATION_1_FAST,
            2: EventType.DEPARTURE_STATION_2_FAST,
            3: EventType.DEPARTURE_STATION_3_FAST
        }[station_id]

        self.depart_slow_event = {
            1: EventType.DEPARTURE_STATION_1_SLOW,
            2: EventType.DEPARTURE_STATION_2_SLOW,
            3: EventType.DEPARTURE_STATION_3_SLOW
        }[station_id]

        self.arrival_event = {
            1: EventType.ARRIVAL_STATION_1,
            2: EventType.ARRIVAL_STATION_2,
            3: EventType.ARRIVAL_STATION_3
        }[station_id]

    def arrival(self):
        if self.fast_charger_status and self.slow_charger_status:
            # Both busy → join queue
            self.num_in_queue += 1
            return

        if not self.fast_charger_status:
            self.fast_charger_status = 1
            self.time_next_event[self.depart_fast_event] = self.sim_time() + self.expon(10.0)
        else:
            self.slow_charger_status = 1
            self.time_next_event[self.depart_slow_event] = self.sim_time() + self.expon(20.0)
        
        self.time_next_event[self.arrival_event] = float('inf')

    def departure_fast(self):
        self.fast_charger_status = 0

        if self.num_in_queue > 0:
            # Take next car from queue
            self.num_in_queue -= 1
            self.fast_charger_status = 1
            self.time_next_event[self.depart_fast_event] = self.sim_time() + self.expon(10.0)

    def departure_slow(self):
        self.slow_charger_status = 0

        if self.num_in_queue > 0:
            self.num_in_queue -= 1
            self.slow_charger_status = 1
            self.time_next_event[self.depart_slow_event] = self.sim_time() + self.expon(20.0)

    def expon(self, mean):
        """Generate exponential random variate."""
        return -mean * np.log(np.random.uniform(0, 1))
