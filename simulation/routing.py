from car import MIN_BATTERY_THRESHOLD
from station_meta import Station_Meta
from routing_policies import RoutingPolicy
MAX_QUEUE_LENGTH = 5  # maximum acceptable queue length

class Routing:
    def __init__(self, car, routing_policy: RoutingPolicy):
        self.car = car # the car being routed
        self.routing_policy = routing_policy # the routing policy to use, this is an ENUM and chosed in system.py

        # mapping of policies to functions, function names are defined in ENUM, the car will routing will call the correct function based on the policy chosen
        self._policy_map = {
            RoutingPolicy.CLOSEST_STATION_FIRST: self._closest_station_first,
            RoutingPolicy.SHORTEST_ESTIMATED_WAIT: self._shortest_estimated_wait
            # add more policies here as needed
        }

    def route(self) -> Station_Meta | None:
        try:
            # look up the correct function to call base on the policy provided 
            policy_fn = self._policy_map[self.routing_policy]
        except KeyError: # policy not found
            raise ValueError(f"Unknown routing policy: {self.routing_policy}")

        return policy_fn()  # if the policy exists call it

    def _closest_station_first(self) -> Station_Meta | None:
        # get the list of reachable stations for this car
        stations: list[Station_Meta] = list(self.car.reachable_stations)

        while stations: # while there are still stations to check
            closest = min(stations, key=lambda s: s.distance_km)
            arrival_time = self.car.system_arrival_time + closest.drive_time_minutes
            q_len = closest.station.get_queue_length_at_time(arrival_time)

            if q_len <= MAX_QUEUE_LENGTH or self.car.battery_level_initial <= MIN_BATTERY_THRESHOLD:
                # Apply routing decision cleanly
                self._apply_routing_decision(closest)
                return closest

            stations.remove(closest) # remove and check next closest

        return None # if we reach here no stations were suitable and None were chosen, car balks

    def _shortest_estimated_wait(self) -> Station_Meta | None:
        # Placeholder for shortest estimated wait policy
        pass

    def _apply_routing_decision(self, chosen: Station_Meta) -> None:
        """
        Updates all car fields after selecting a routing destination.
        """
        self.car.routed_station = chosen # update routed station with station_meta object
        self.car.routed_drive_time = chosen.drive_time_minutes 
        # car charge time (service)

