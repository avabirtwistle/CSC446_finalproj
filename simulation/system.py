# ev_charging_system.py
import numpy as np
from event import EventType
from charging_station import Charging_Station
from car import Car

class EV_Charging_System:
    def __init__(self, routing_policy, num_delays_required):
        self.routing_policy = routing_policy
        self.num_delays_required = num_delays_required
        self.num_cars_processed = 0

        self.mean_interarrival_time = 0.3

        self.sim_time = 0.0

        # event list
        self.time_next_event = {e: float('inf') for e in EventType}
        self.time_next_event[EventType.ARRIVAL_SYSTEM] = (
            self.sim_time + self.expon(self.mean_interarrival_time)
        )

        # stations
        self.stations = [
            Charging_Station(1, [48.42806, -123.36959], self.time_next_event, lambda: self.sim_time),
            Charging_Station(2, [48.4573, -123.37509], self.time_next_event, lambda: self.sim_time),
            Charging_Station(3, [48.44504, -123.46754], self.time_next_event, lambda: self.sim_time),
        ]

    def timing(self):
        self.min_time_next_event = float('inf')
        self.next_event_type = None

        for event_type, event_time in self.time_next_event.items():
            if event_time < self.min_time_next_event:
                self.min_time_next_event = event_time
                self.next_event_type = event_type

        if self.next_event_type is None:
            raise Exception("All events are infinite — terminating simulation.")

        # Advance simulation clock
        self.sim_time = self.min_time_next_event
        print(f"Time: {self.sim_time:.3f} | Next Event: {self.next_event_type.name}")
        print("Event List:")
        for event_type, event_time in self.time_next_event.items():
            print(f"  {event_type.name}: {event_time:.3f}")
        print("-" * 40)
        print(f"Advancing simulation clock to {self.sim_time:.3f}")

    def arrival_system(self):
        # schedule next system arrival
        self.time_next_event[EventType.ARRIVAL_SYSTEM] = (
            self.sim_time + self.expon(self.mean_interarrival_time)
        )

        car = Car(self.sim_time)

        # TEMP routing policy pass car into actual one
        station_choice = np.random.randint(0, 3)
        station_event = [
            EventType.ARRIVAL_STATION_1,
            EventType.ARRIVAL_STATION_2,
            EventType.ARRIVAL_STATION_3,
        ][station_choice]

        self.time_next_event[station_event] = (
            self.sim_time + self.expon(2.0)  # change to drive time
        )
    def expon(self, mean):
        return -mean * np.log(np.random.uniform(0, 1))

    def main(self):
        while self.num_cars_processed < self.num_delays_required:
            self.timing()



            match self.next_event_type:
                case EventType.ARRIVAL_SYSTEM:
                    self.arrival_system()
                case EventType.ARRIVAL_STATION_1:
                    self.stations[0].arrival()
                case EventType.ARRIVAL_STATION_2:
                    self.stations[1].arrival()
                case EventType.ARRIVAL_STATION_3:
                    self.stations[2].arrival()
                case EventType.DEPARTURE_STATION_1_FAST:
                    self.stations[0].departure_fast()
                    self.num_cars_processed += 1
                case EventType.DEPARTURE_STATION_1_SLOW:
                    self.stations[0].departure_slow()
                    self.num_cars_processed += 1
                case EventType.DEPARTURE_STATION_2_FAST:
                    self.stations[1].departure_fast()
                    self.num_cars_processed += 1
                case EventType.DEPARTURE_STATION_2_SLOW:
                    self.stations[1].departure_slow()
                    self.num_cars_processed += 1
                case EventType.DEPARTURE_STATION_3_FAST:
                    self.stations[2].departure_fast()
                    self.num_cars_processed += 1
                case EventType.DEPARTURE_STATION_3_SLOW:
                    self.stations[2].departure_slow()
                    self.num_cars_processed += 1

if __name__ == "__main__":
    simulation = EV_Charging_System("shortest_estimated_time", 10000)
    simulation.main()
