# ev_charging_system.py
import heapq
import numpy as np
from event import EventType
from charging_station import Charging_Station
from car import Car
from routing import Routing

class EV_Charging_System:
    def __init__(self, routing_policy, num_delays_required):
        self.routing_policy = routing_policy # the routing policy being used
        self.num_delays_required = num_delays_required
        self.num_cars_processed = 0 
        self.total_time_in_system = 0.0
        self.total_wait_time = 0.0
        self.total_wait_time_queue = 0.0

        self.mean_interarrival_time = 0.3
        self.sim_time = 0.0

        # Event list
        self.event_queue = []   # (time, event_type, payload)

        # schedule first system arrival
        first_arrival = self.sim_time + self.expon(self.mean_interarrival_time)
        heapq.heappush(self.event_queue,
                       (first_arrival, EventType.ARRIVAL_SYSTEM, None)) # push event with no car yet

        # stations
        # TODO find the actual kilometer locations this is what chatgpt suggested based on the coordinates
        self.stations = [
            Charging_Station(1, [2.0, 3.0], lambda: self.sim_time),   # downtown / central
            Charging_Station(2, [7.5, 4.0], lambda: self.sim_time),   # uptown / NE side
            Charging_Station(3, [3.0, 0.8], lambda: self.sim_time),   # west / highway area
        ]


    def timing(self):
        if not self.event_queue:
            raise Exception("Event queue empty — simulation cannot continue.")
        # Addvance sim time, get next event, and the car involved (if car)
        self.sim_time, self.next_event_type, self.event_car = heapq.heappop(self.event_queue)

    #print the time advancement and next event and car metadata
        print(f"\nTime advanced to {self.sim_time:.3f} | "
          f"Next Event = {self.next_event_type.name} | "
          f"Car = {self.event_car.station_routed_to if self.event_car else 'N/A'}")

    # arrivals to the system  
    def arrival_system(self):
        # schedule next system arrival
        next_arrival = self.sim_time + self.expon(self.mean_interarrival_time)
        heapq.heappush(self.event_queue,
                       (next_arrival, EventType.ARRIVAL_SYSTEM, None))

        # create the car and route it
        car = Car(system_arrival_time=self.sim_time, stations=self.stations)
        routing = Routing(car, self.routing_policy) # create routing object for the car, this decides where the car will go
        station_choice_id = routing.get_chosen_station_().station_id # get the station id of the chosen station

        # select the correct arrival event type based on the id we retrieved from station choice
        station_event = [
            EventType.ARRIVAL_STATION_1,
            EventType.ARRIVAL_STATION_2,
            EventType.ARRIVAL_STATION_3,
        ][station_choice_id - 1]

        # schedule arrival to the station - this is the time it takes the car to drive there
        heapq.heappush(self.event_queue, (car.routed_arrival_time_queue, station_event, routing))

    def expon(self, mean):
        return -mean * np.log(np.random.uniform())
    
    def record_departure(self, car):
        # retrieve the total time in system for this car and add to total
        self.total_time_in_system += car.get_total_time_in_system(self.sim_time)

        # retrieve the wait time (drive + queue) for this car and add to total
        self.wait_time_queue += car.get_wait_time(self.sim_time) 
        self.total_wait_time += car.get_wait_time(self.sim_time) + car.routed_drive_time # total wait time includes drive time
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
