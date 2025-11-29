import heapq
import numpy as np
from event import EventType

class Charging_Station:
    def __init__(self, station_id, position, sim_time):

        self.station_id = station_id
        self.position = position
        self.sim_time = sim_time   # lambda returning current sim time

        self.fast_charger_status = 0
        self.slow_charger_status = 0

        self.queue = []   # Store Cars

        self.mean_fast_service = 0.5
        self.mean_slow_service = 1.0

        # event type mapping
        self.arrival_event = {
            1: EventType.ARRIVAL_STATION_1,
            2: EventType.ARRIVAL_STATION_2,
            3: EventType.ARRIVAL_STATION_3
        }[station_id]

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

    # car is passed in from system ( so lowest time in event queue)
    def arrival(self, car, event_queue):

        # if both chargers busy - join queue
        if self.fast_charger_status == 1 and self.slow_charger_status == 1:
            car.queue_entry_time = self.sim_time()
            self.queue.append(car)
            return

        # is teh fast charger free?
        if self.fast_charger_status == 0:
            self.fast_charger_status = 1

            service_time = self.expon(self.mean_fast_service)
            depart_time = self.sim_time() + service_time

            #schedule departure event
            heapq.heappush(event_queue,
                (depart_time, self.depart_fast_event, car))

            return

        # is the slow charger free?
        if self.slow_charger_status == 0:
            self.slow_charger_status = 1
            self.slow_car = car

            service_time = self.expon(self.mean_slow_service)
            depart_time = self.sim_time() + service_time

            heapq.heappush(event_queue,
                (depart_time, self.depart_slow_event, car))

            return


    # the next event was a departure from the fast charger
    def departure_fast(self, event_queue):

        # queue empty?
        if len(self.queue) == 0:
            self.fast_charger_status = 0
            return

        # take next car from queue
        next_car = self.queue.pop(0)
        self.fast_charger_status = 1

        service_time = self.expon(self.mean_fast_service)
        depart_time = self.sim_time() + service_time

        heapq.heappush(event_queue,
            (depart_time, self.depart_fast_event, next_car))


    # slow charger
    def departure_slow(self, event_queue):

        if len(self.queue) == 0:
            self.slow_charger_status = 0
            return

        next_car = self.queue.pop(0)
        self.slow_charger_status = 1

        service_time = self.expon(self.mean_slow_service)
        depart_time = self.sim_time() + service_time

        heapq.heappush(event_queue,
            (depart_time, self.depart_slow_event, next_car))


    def expon(self, mean):
        return -mean * np.log(np.random.uniform())
