import heapq
import numpy as np
from event import EventType
from constants import BATTERY_CAPACITY, FAST_CHARGER_POWER_KW, SLOW_CHARGER_POWER_KW, ASSUMED_SOC_FINAL


class Charging_Station:
    def __init__(self, station_id, position, sim_time):

        self.station_id = station_id
        self.position = position
        self.sim_time = sim_time   # lambda returning current sim time

        self.fast_charger_status = 0
        self.slow_charger_status = 0

        self.current_estimated_wait_time = 0.0 # in minutes

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
    def arrival(self, routing, event_queue):
        print("\n=== arrival() ===")
        car = routing.car
        # if both chargers busy - join queue
        if self.fast_charger_status == 1 and self.slow_charger_status == 1:
            print(f"Both chargers busy at station {self.station_id}. Car joining queue.")
            car.routed_arrival_time_queue = self.sim_time() # update the car's arrival time at the station queue if it has to wait
            self.queue.append(car)
            return

        # is the fast charger free?
        if self.fast_charger_status == 0:
            print(f"Fast charger free at station {self.station_id}. Car starting to charge.")
            self.fast_charger_status = 1

            # compute service time and schedule departure
            service_time = self.compute_charge_time(car.target_charge_level, car.battery_level_initial, FAST_CHARGER_POWER_KW)            
            car.time_charging = service_time
            depart_time = self.sim_time() + service_time
            print(f"Car's initial battery level: {car.battery_level_initial:.2f}%, target charge level: {car.target_charge_level:.2f}%. , service time: {service_time:.3f} minutes. ")
            print(f"cheduling departure from fast charger at station {self.station_id} at time {depart_time:.3f}.")
            #schedule departure event
            heapq.heappush(event_queue,
                (depart_time, self.depart_fast_event, car)) 
            return

        # is the slow charger free?
        if self.slow_charger_status == 0:
            print(f"Slow charger free at station {self.station_id}. Car starting to charge.")
            self.slow_charger_status = 1
            self.slow_car = car

            # compute service time and schedule departure
            service_time = self.compute_charge_time(car.target_charge_level, car.battery_level_initial, SLOW_CHARGER_POWER_KW)
            car.time_charging = service_time # set the car's service time
            depart_time = self.sim_time() + service_time # compute departure time
            print(f"Car's initial battery level: {car.battery_level_initial:.2f}%, target charge level: {car.target_charge_level:.2f}%. , service time: {service_time:.3f} minutes. ")
            print(f"cheduling departure from slow charger at station {self.station_id} at time {depart_time:.3f}.")


            # Schedule thedeparture event
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

        # compute service time and schedule departure
        service_time = self.compute_charge_time(next_car.target_charge_level, next_car.battery_level_initial, FAST_CHARGER_POWER_KW)
        next_car.time_charging = service_time  # set the car's service time
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
        service_time = self.compute_charge_time(next_car.target_charge_level, next_car.battery_level_initial, SLOW_CHARGER_POWER_KW)
        next_car.time_charging = service_time  # set the car's service time
        depart_time = self.sim_time() + service_time

        heapq.heappush(event_queue,
            (depart_time, self.depart_slow_event, next_car))

    def compute_charge_time(self, target_charge_level, battery_level_initial, charge_rate_kw: float) -> float:
        """
        Computes the estimated charge time (in hours) for the given car
        based on its target charge level. Affected by the service rate of the charger it gets assigned to.
        Args:
            target_charge_level (float): The target charge level for the car.
            battery_level_initial (float): The initial battery level of the car.
            charge_rate_kw (float): The charging rate of the charger in kW.
            Returns:       
            float: Estimated charge time in minutes
        """
        soc_diff = (target_charge_level - battery_level_initial) / 100.0 # fraction of battery to charge
        time_in_minutes = ((soc_diff * BATTERY_CAPACITY) / charge_rate_kw) * 60.0 
        return time_in_minutes # return the service time in minutes


    def expon(self, mean):
        return -mean * np.log(np.random.uniform())
