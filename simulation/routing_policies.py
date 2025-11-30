from enum import Enum

class RoutingPolicy(str, Enum):
    CLOSEST_STATION_FIRST = "closest_station_first"
    SHORTEST_ESTIMATED_WAIT = "shortest_estimated_wait"
