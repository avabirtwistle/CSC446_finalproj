import heapq
import numpy as np
from routing_policies import RoutingPolicy
from event import EventType
from charging_station import Charging_Station
from car import Car
from routing import Routing

class EV_Charging_System:
    def __init__(self, routing_policy, num_delays_required, seed):
        self.routing_policy = routing_policy # The routing policy being used
        self.num_delays_required = num_delays_required
        self.num_cars_processed = 0 
        self.total_time_in_system = 0.0
        self.total_wait_time = 0.0
        self.total_wait_time_queue = 0.0
        self.total_balking = 0
        self.seed = seed
        np.random.seed(seed)

        self.mean_interarrival_time = 10.0
        self.sim_time = 0.0
        self.void_counter = [0, 0, 0]  # List to track cars on the way to each station

        # Event list
        self.event_queue = []   # (time, event_type, payload)

        # Schedule first system arrival
        first_arrival = self.sim_time + self.expon(self.mean_interarrival_time)
        heapq.heappush(self.event_queue,
                       (first_arrival, EventType.ARRIVAL_SYSTEM, None)) # Push event without routing

        # Stations
        self.stations = [
            Charging_Station(1, [2.0, 3.0], lambda: self.sim_time),   # Downtown / central
            Charging_Station(2, [7.5, 4.0], lambda: self.sim_time),   # Uptown / NE side
            Charging_Station(3, [3.0, 0.8], lambda: self.sim_time),   # West / highway area
        ]

    def timing(self):
        print("\n=== TIMING() ===")

        if not self.event_queue:
            raise Exception("Event queue empty — simulation cannot continue.")

        # Pop next min time event
        self.sim_time, self.next_event_type, self.routing = heapq.heappop(self.event_queue)

        # determine if there's a car
        if self.routing and hasattr(self.routing, "car"):
            self.event_car = self.routing.car
        else:
            self.event_car = None

        car_info = (
            f"Car at station {self.event_car.routed_station.station.station_id}"
            if self.event_car else
            "No car"
        )

        print(f"Time: {self.sim_time:.3f} | "
            f"Event: {self.next_event_type.name} | "
            f"{car_info}")

    def arrival_system(self):
        print("\n=== arrival_system() ===")
        # Schedule next system arrival
        next_arrival = self.sim_time + self.expon(self.mean_interarrival_time)
        heapq.heappush(self.event_queue,
                    (next_arrival, EventType.ARRIVAL_SYSTEM, None))

        # Create the car and routing object
        car = Car(system_arrival_time=self.sim_time, stations=self.stations)
        routing = Routing(car, self.routing_policy, void_counter=self.void_counter)

        # Actually perform routing and set routed_station
        chosen_station = routing.route()
        routing.routed_station = chosen_station  # (if not set inside route()) follow up 

        if routing.routed_station is None:
            print("No station available for routing (car balks).")
            self.total_balking += 1
            return

        print(f"Car {car.battery_level_initial} routed to station {routing.routed_station.station.station_id}")
        station_choice_id = routing.routed_station.station.station_id

        # Select the correct arrival event type based on the id we retrieved from station choice
        station_event = [
            EventType.ARRIVAL_STATION_1, 
            EventType.ARRIVAL_STATION_2,
            EventType.ARRIVAL_STATION_3,
        ][station_choice_id - 1]

        # Schedule arrival to the station - this is the time it takes the car to drive there
        heapq.heappush(self.event_queue, (car.routed_arrival_time, station_event, routing))

    def expon(self, mean): # generate exponential random variable
        """
        Generate an exponential random variable with the given mean.
        
        :param mean: The mean of the exponential distribution.
        :return: A random variable drawn from the exponential distribution.
        """
        return -mean * np.log(np.random.uniform())
    
    def record_departure(self, car):
        """
        Records the departure of a car from the system, updating statistics.
            
        :param car: The car that is departing.        
        """
        # retrieve the total time in system for this car and add to total
        self.total_time_in_system += car.get_total_time_in_system(self.sim_time)

        # retrieve the wait time (drive + queue) for this car and add to total
        self.total_wait_time_queue += car.time_in_queue
        self.total_wait_time += (car.time_in_queue + car.routed_drive_time) # total wait time includes drive time
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
        print(f"Total Time in System: {self.total_time_in_system:.2f} minutes")
        print(f"Total Wait Time (incl. drive): {self.total_wait_time:.2f} minutes")
        print("-" * 50)
        print(f"Average Time in System: {avg_time_in_system:.2f} minutes")
        print(f"Average Wait Time (incl. drive): {avg_wait_time:.2f} minutes")
        print("="*50)

    def get_results(self):
        if self.num_cars_processed > 0:
            avg_time_in_system = self.total_time_in_system / self.num_cars_processed 
            avg_wait_time = self.total_wait_time / self.num_cars_processed
        else: 
            avg_time_in_system = 0.0
            avg_wait_time = 0.0 

        return {"policy": self.routing_policy.name,
                "seed": self.seed,
                "cars_processed": self.num_cars_processed,
                "avg_time_in_system": avg_time_in_system,
                "avg_wait_time": avg_wait_time,
                "total_balking": self.total_balking,
                }

    def main(self):
        while self.num_cars_processed < self.num_delays_required:
            self.timing() # - to get the next event

            match self.next_event_type:
                # to each event other than system arrival pass the event queue and the car

                case EventType.ARRIVAL_SYSTEM:
                    self.arrival_system()

                case EventType.ARRIVAL_STATION_1:
                    self.stations[0].arrival(self.routing, self.event_queue)

                case EventType.ARRIVAL_STATION_2:
                    self.stations[1].arrival(self.routing, self.event_queue)

                case EventType.ARRIVAL_STATION_3:
                    self.stations[2].arrival(self.routing, self.event_queue)

                case EventType.DEPARTURE_STATION_1_FAST:
                    self.stations[0].departure_fast(self.event_queue)
                    self.record_departure(self.routing)

                case EventType.DEPARTURE_STATION_1_SLOW:
                    self.stations[0].departure_slow(self.event_queue)
                    self.record_departure(self.routing)

                case EventType.DEPARTURE_STATION_2_FAST:
                    self.stations[1].departure_fast(self.event_queue)
                    self.record_departure(self.routing)

                case EventType.DEPARTURE_STATION_2_SLOW:
                    self.stations[1].departure_slow(self.event_queue)
                    self.record_departure(self.routing)

                case EventType.DEPARTURE_STATION_3_FAST:
                    self.stations[2].departure_fast(self.event_queue)
                    self.record_departure(self.routing)

                case EventType.DEPARTURE_STATION_3_SLOW:
                    self.stations[2].departure_slow(self.event_queue)
                    self.record_departure(self.routing)

        self.print_results()

if __name__ == "__main__":
    # CLOSEST_STATION_FIRST = "closest_station_first"
    # SHORTEST_ESTIMATED_WAIT
    sim = EV_Charging_System(RoutingPolicy.SHORTEST_ESTIMATED_WAIT, 1000, 10)
    sim.main()
