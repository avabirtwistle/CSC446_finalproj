from car import MIN_BATTERY_THRESHOLD
from station_meta import Station_Meta
from routing_policies import RoutingPolicy
from event import EventType
from constants import MAX_QUEUE_LENGTH, TIME_FACTOR

class Routing:
    def __init__(self, car, routing_policy: RoutingPolicy, void_counter: list[int]):
        self.car = car # the car being routed
        self.routing_policy = routing_policy # the routing policy to use, this is an ENUM and chosed in system.py
        self.routed_station = None
        # store the void counter for use in routing decisions
        self.void_counter = void_counter
        # mapping of policies to functions, function names are defined in ENUM, the car will routing will call the correct function based on the policy chosen
        self._policy_map = {
            RoutingPolicy.CLOSEST_STATION_FIRST: self._closest_station_first,
            RoutingPolicy.SHORTEST_ESTIMATED_WAIT: self._shortest_estimated_wait
            # add more policies here as needed
        }

    def route(self) -> Station_Meta | None:
        """
        Docstring for route which selects the routing policy to use and calls the appropriate function
        
        :param self: Description
        :rtype: Station_Meta | None
        """
        try:
            # look up the correct function to call base on the policy provided 
            policy_fn = self._policy_map[self.routing_policy]
        except KeyError: # policy not found
            raise ValueError(f"Unknown routing policy: {self.routing_policy}")

        return policy_fn()  # if the policy exists call it

    def _closest_station_first(self) -> Station_Meta | None:
        """
        Implements the closest station first routing policy.

        :param self: Description
        :rtype: Station_Meta | None
        """
        # get the list of reachable stations for this car
        stations: list[Station_Meta] = list(self.car.reachable_stations)
        print("\n==================== NEW ROUTING DECISION ====================")
        print(f"Car Info:")
        print(f"  • Position: {self.car.position}")
        print(f"  • Battery: {self.car.battery_level_initial:.2f}%")
        print(f"  • System arrival time: {self.car.system_arrival_time:.2f}")
        print(f"  • Reachable stations: {len(stations)}")        
        while stations: # while there are still stations to check
            closest = min(stations, key=lambda s: s.drive_time_minutes) # get the closest station based on drive time
            q_len = closest.get_effective_queue_length(void_counter=self.void_counter)
            print(f"Case: Station {closest.get_station_id()} | "
                f"drive_time={closest.drive_time_minutes:.2f} min | "
                f"current queue={closest.get_effective_queue_length(void_counter=self.void_counter)}")
            # if the queue length at the closest station is acceptable or the car is low on battery choose it
            if q_len <= MAX_QUEUE_LENGTH or self.car.battery_level_initial <= MIN_BATTERY_THRESHOLD:
                # Apply routing decision cleanly
                self._apply_routing_decision(closest, void_counter=self.void_counter)
                print(f"  Chose station {closest.get_station_id()} for routing.")
                print(f"  Arrival at station queue {self.car.routed_arrival_time_queue} for routing.")
                return closest
            else:
                print(f"  Station {closest.get_station_id()} rejected due to long queue.")
                stations.remove(closest) # remove and check next closest

        return None # if we reach here no stations were suitable and None were chosen, car balks
    def _shortest_estimated_wait(self) -> Station_Meta | None:
        print("\n=== SHORTEST ESTIMATED WAIT () ===")
        print(f"Car battery: {self.car.battery_level_initial:.2f}%")
        print(f"Reachable stations: {len(self.car.reachable_stations)}")

        stations: list[Station_Meta] = list(self.car.reachable_stations)
        wait_times = {}

        for station_meta in stations:
            st_id = station_meta.get_station_id()
            drive_time = station_meta.drive_time_minutes
            print(f"\nChecking station {st_id}:")
            print(f"  • Drive time = {drive_time:.2f} min")

            # compute estimated queue wait
            wait_time_ahead = self._verify_station_(station_meta,
                                                    self.car.battery_level_initial,
                                                    void_counter=self.void_counter)

            if wait_time_ahead == -1:
                print(f"  ✘ Station {st_id} rejected (verify returned -1)")
                continue

            print(f"  • Estimated queue wait = {wait_time_ahead:.2f} min")

            total_est = wait_time_ahead + drive_time
            print(f"  → Total estimated time = {total_est:.2f} min")

            wait_times[station_meta] = total_est

        if not wait_times:
            print("\nNo valid stations. Car will balk.\n")
            return None

        # pick minimum
        chosen = min(wait_times, key=lambda s: wait_times[s])
        chosen_id = chosen.get_station_id()
        chosen_wait = wait_times[chosen]
        soc_after_drive = self.car.get_estimated_soc_after_drive(chosen.station)

        self.car.soc_initial = soc_after_drive[0]
        print(f"  • Estimated SoC after drive = {soc_after_drive[0]:.2f}%")
        print(f"\n=== CHOSEN STATION ===")
        print(f"Station {chosen_id} with total estimated time {chosen_wait:.2f} min.\n")

        self._apply_routing_decision(chosen, void_counter=self.void_counter)
        return chosen

    def _verify_station_(self, station_meta: Station_Meta, battery_level, void_counter: list[int]) -> int:
        """
        Helper for eliminating the stations that have too long of a queue from consideration 
        Returns the queue length >=0 if valid, returns -1 if false
        """
        q_len = station_meta.get_effective_queue_length(void_counter=void_counter) # get the number of cars in the queue and on the way to the station
        if q_len > MAX_QUEUE_LENGTH and battery_level > MIN_BATTERY_THRESHOLD:
            return -1 # if we shouldn't consider this station return -1
        return q_len # if we can consider this stations return the queue length

    def _apply_routing_decision(self, chosen: Station_Meta, void_counter: list[int]) -> None:
        """
        Updates all car fields after selecting a routing destination.
        """
        void_counter[chosen.get_station_id() - 1] += 1 # increment the void counter for the chosen station indicating a car is somewhere in the simultion
        self.car.routed_station = chosen # update routed station with station_meta object
        self.car.routed_arrival_time_queue = self.car.system_arrival_time + chosen.drive_time_minutes  # set arrival time at station including drive time
        
        self.car.routed_drive_time = chosen.drive_time_minutes 
