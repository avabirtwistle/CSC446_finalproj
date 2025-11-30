import heapq
import numpy as np
from event import EventType
from car import Car
from car import BATTERY_CAPACITY

SLOW_CHARGER_POWER_KW = 4.8 # BC Hydro Level 2 ~ 4.8 kW
FAST_CHARGER_POWER_KW = 200   # BC Hydro Fast Charger ~ 200 kW Level 3
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
            car.routed_arrival_time_queue = self.sim_time() # update the car's arrival time at the station queue if it has to wait
            self.queue.append(car)
            return

        # is the fast charger free?
        if self.fast_charger_status == 0:
            self.fast_charger_status = 1

            # compute service time and schedule departure
            service_time = self.compute_charge_time(car, FAST_CHARGER_POWER_KW)            
            depart_time = self.sim_time() + service_time

            #schedule departure event
            heapq.heappush(event_queue,
                (depart_time, self.depart_fast_event, car)) 
            return

        # is the slow charger free?
        if self.slow_charger_status == 0:
            self.slow_charger_status = 1
            self.slow_car = car

            service_time = self.compute_charge_time(car, SLOW_CHARGER_POWER_KW)
            depart_time = self.sim_time() + service_time

            # Schedule thedeparture event
            heapq.heappush(event_queue,
                (depart_time, self.depart_slow_event, car))

            return

    def get_queue_length_at_time(self, query_time: float) -> int:
        """
        Estimates the queue length at this station at the specified future time.

        Args:
            query_time (float): The future time (in hours) to query the queue length for.

        Returns:
            int: Estimated queue length at the specified time.
        """
        # For simplicity, we return the current queue length.
        # In a more complex implementation, we would simulate the queue evolution over time.
        return len(self.queue)

    # the next event was a departure from the fast charger
    def departure_fast(self, event_queue):

        # queue empty?
        if len(self.queue) == 0:
            self.fast_charger_status = 0
            return

        # take next car from queue
        next_car = self.queue.pop(0)
        self.fast_charger_status = 1

        # compute service time and schedule departure
        service_time = self.compute_charge_time(next_car, FAST_CHARGER_POWER_KW)
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

        # compute service time and schedule departure
        service_time = self.compute_charge_time(next_car, SLOW_CHARGER_POWER_KW)
        depart_time = self.sim_time() + service_time

        heapq.heappush(event_queue,
            (depart_time, self.depart_slow_event, next_car))

    def compute_charge_time(self, car: Car, charge_rate_kw: float) -> float:
        """
        Computes the estimated charge time (in hours) for the given car
        based on its target charge level. Affected by the service rate of the charger it gets assigned to.


        Args:
            car (Car): The car to compute charge time for.
            Returns:       
            float: Estimated charge time in minutes
        """
        soc_diff = (car.target_charge_level - car.battery_level_initial) / 100.0 # fraction of battery to charge
        time_in_minutes = ((soc_diff * BATTERY_CAPACITY) / charge_rate_kw) * 60.0 
        car.time_charging = time_in_minutes # update the car's time charging field
        return time_in_minutes # return the service time in minutes

    def expon(self, mean):
        return -mean * np.log(np.random.uniform())
