# ev_charging_system.py
import heapq
import numpy as np
from event import EventType
from charging_station import Charging_Station
from car import Car


class EV_Charging_System:
    def __init__(self, routing_policy, num_delays_required):
        self.routing_policy = routing_policy
        self.num_delays_required = num_delays_required
        self.num_cars_processed = 0
        self.total_time_in_system = 0.0
        self.total_wait_time = 0.0

        self.mean_interarrival_time = 0.3
        self.sim_time = 0.0

        # Event list
        self.event_queue = []   # (time, event_type, payload)

        # schedule first system arrival
        first_arrival = self.sim_time + self.expon(self.mean_interarrival_time)
        heapq.heappush(self.event_queue,
                       (first_arrival, EventType.ARRIVAL_SYSTEM, None))

        # stations
        self.stations = [
            Charging_Station(1, [48.42806, -123.36959], lambda: self.sim_time),
            Charging_Station(2, [48.4573,  -123.37509], lambda: self.sim_time),
            Charging_Station(3, [48.44504, -123.46754], lambda: self.sim_time),
        ]

    def timing(self):
        if not self.event_queue:
            raise Exception("Event queue empty — simulation cannot continue.")
        # Addvance sim time, get next event, and the car involved (if car)
        self.sim_time, self.next_event_type, self.event_car = heapq.heappop(self.event_queue)

        print(f"\nTime advanced to {self.sim_time:.3f} | "
          f"Next Event = {self.next_event_type.name} | "
          f"Car = {self.event_car.station_routed_to if self.event_car else 'N/A'}")

    # arrivals to the system 
    def arrival_system(self):
        # schedule next system arrival
        next_arrival = self.sim_time + self.expon(self.mean_interarrival_time)
        heapq.heappush(self.event_queue,
                       (next_arrival, EventType.ARRIVAL_SYSTEM, None))

        # create the car
        car = Car()
        car.system_arrival_time = self.sim_time

        # select a station (TEMP: random)
        station_choice = np.random.randint(1, 4)  # 1,2,3
        station_event = [
            EventType.ARRIVAL_STATION_1,
            EventType.ARRIVAL_STATION_2,
            EventType.ARRIVAL_STATION_3,
        ][station_choice - 1]

        # compute drive time (TEMP: random)
        drive_time = self.expon(0.5)
        car.drive_time = drive_time
        car.station_routed_to = station_choice
        car.station_arrival_time = self.sim_time + drive_time

        # schedule arrival to the station - this is the time it takes the car to drive there
        heapq.heappush(self.event_queue,
                       (car.station_arrival_time, station_event, car))

    def expon(self, mean):
        return -mean * np.log(np.random.uniform())
    
    def record_departure(self, car):
        time_in_system = self.sim_time - car.system_arrival_time
        self.total_time_in_system += time_in_system

        if car.queue_entry_time == 0.0:
            wait_time = car.drive_time

        else:
            time_in_queue = self.sim_time - car.queue_entry_time
            wait_time = car.drive_time + time_in_queue

        self.total_wait_time += wait_time
        self.num_cars_processed += 1

    def print_results(self):
        """Prints the final simulation results."""
        if self.num_cars_processed > 0:
            avg_time_in_system = self.total_time_in_system / self.num_cars_processed
            avg_wait_time = self.total_wait_time / self.num_cars_processed
        else:
            avg_time_in_system = 0.0
            avg_wait_time = 0.0

        print("\n" + "="*50)
        print("Simulation Results")
        print(f"Total Cars Processed: {self.num_cars_processed}")
        print(f"Total Time in System: {self.total_time_in_system:.2f} hrs")
        print(f"Total Wait Time (incl. drive): {self.total_wait_time:.2f} hrs")
        print("-" * 50)
        print(f"Average Time in System: {avg_time_in_system:.2f} hrs")
        print(f"Average Wait Time (incl. drive): {avg_wait_time:.2f} hrs")
        print("="*50)

    def main(self):
        while self.num_cars_processed < self.num_delays_required:
            self.timing() # - to get the next event

            match self.next_event_type:
                # to each event other than system arrival pass the event queue and the car

                case EventType.ARRIVAL_SYSTEM:
                    self.arrival_system()

                case EventType.ARRIVAL_STATION_1:
                    self.stations[0].arrival(self.event_car, self.event_queue)

                case EventType.ARRIVAL_STATION_2:
                    self.stations[1].arrival(self.event_car, self.event_queue)

                case EventType.ARRIVAL_STATION_3:
                    self.stations[2].arrival(self.event_car, self.event_queue)

                case EventType.DEPARTURE_STATION_1_FAST:
                    self.stations[0].departure_fast(self.event_queue)
                    self.record_departure(self.event_car)

                case EventType.DEPARTURE_STATION_1_SLOW:
                    self.stations[0].departure_slow(self.event_queue)
                    self.record_departure(self.event_car)

                case EventType.DEPARTURE_STATION_2_FAST:
                    self.stations[1].departure_fast(self.event_queue)
                    self.record_departure(self.event_car)

                case EventType.DEPARTURE_STATION_2_SLOW:
                    self.stations[1].departure_slow(self.event_queue)
                    self.record_departure(self.event_car)

                case EventType.DEPARTURE_STATION_3_FAST:
                    self.stations[2].departure_fast(self.event_queue)
                    self.record_departure(self.event_car)

                case EventType.DEPARTURE_STATION_3_SLOW:
                    self.stations[2].departure_slow(self.event_queue)
                    self.record_departure(self.event_car)

        self.print_results()

if __name__ == "__main__":
    sim = EV_Charging_System("shortest_estimated_time", 100000)
    sim.main()
