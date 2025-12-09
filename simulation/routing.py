from car import MIN_BATTERY_THRESHOLD
from station_meta import Station_Meta
from routing_policies import RoutingPolicy
from event import EventType
from constants import MAX_QUEUE_LENGTH, TIME_FACTOR, BALK_BATTERY_LEVEL

class Routing:
    def __init__(self, car, routing_policy: RoutingPolicy, void_counter: list[int]):
        self.car = car # the car being routed
        self.routing_policy = routing_policy # the routing policy to use, this is an ENUM and chosen in system.py
        self.routed_station = None
        self.void_counter = void_counter # store the void counter for use in routing decisions

        # mapping of policies to functions, function names are defined in ENUM, the car will routing will call the correct function based on the policy chosen
        self._policy_map = {
            RoutingPolicy.CLOSEST_STATION_FIRST: self._closest_station_first,
            RoutingPolicy.SHORTEST_ESTIMATED_WAIT: self._shortest_estimated_wait
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
        while stations: # while there are still stations to check
            closest = min(stations, key=lambda s: s.drive_time_minutes) # get the closest station based on drive time
            # if the queue length at the closest station is acceptable or the car is low on battery choose it
            if (verify := self._verify_station_(closest, closest.soc_after_drive, void_counter=self.void_counter)) != -1: # if we are allowed to route to the station
                # Apply routing decision cleanly
                self._apply_routing_decision(closest, void_counter=self.void_counter)
                return closest
            else:
                stations.remove(closest) # remove and check next closest

        return None # if we reach here no stations were suitable and None were chosen, car balks
    
    def _shortest_estimated_wait(self) -> Station_Meta | None:
        stations: list[Station_Meta] = list(self.car.reachable_stations)
        wait_times = {}

        for station_meta in stations:
            drive_time = station_meta.drive_time_minutes

            # compute estimated queue wait
            wait_time_ahead = self._verify_station_(station_meta,
                                                    station_meta.soc_after_drive,
                                                    void_counter=self.void_counter)

            wait_time_ahead = wait_time_ahead * TIME_FACTOR

            if wait_time_ahead < 0:
                continue

            total_est = wait_time_ahead + drive_time
            wait_times[station_meta] = total_est

        if not wait_times:
            return None

        # pick minimum
        chosen = min(wait_times, key=lambda s: wait_times[s])
        self._apply_routing_decision(chosen, void_counter=self.void_counter)
        return chosen

    def _verify_station_(self, station_meta: Station_Meta, soc_after_drive: float, void_counter: list[int]) -> int:
        """
        Helper for eliminating the stations that have too long of a queue from consideration 
        Returns the queue length >=0 if valid, returns -1 if false
        """
        q_len = station_meta.get_effective_queue_length(void_counter=void_counter) # get the number of cars in the queue and on the way to the station
        if q_len > MAX_QUEUE_LENGTH and soc_after_drive > BALK_BATTERY_LEVEL: # if the queue length is too long and the car has enough battery to consider other stations
            return -1 # if we shouldn't consider this station return -1
        return q_len # if we can consider this stations return the queue length

    def _apply_routing_decision(self, chosen: Station_Meta, void_counter: list[int]) -> None:
        """
        Updates all car fields after selecting a routing destination.
        """
        void_counter[chosen.get_station_id() - 1] += 1 # increment the void counter for the chosen station indicating a car is somewhere in the simultion
        self.car.routed_station = chosen # update routed station with station_meta object
        self.car.routed_arrival_time = self.car.system_arrival_time + chosen.drive_time_minutes
        self.car.soc_after_drive = chosen.soc_after_drive
        self.car.routed_drive_time = chosen.drive_time_minutes 
