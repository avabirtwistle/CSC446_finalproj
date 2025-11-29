import numpy as np

from simulation.station_meta import Station_Meta
from simulation.charging_station import Charging_Station
from typing import Iterable
# Constraints for the min and max coordinates can be adjusted based on the desired area
X_MIN = 48.42242
X_MAX = 48.46956
Y_MIN = -123.48509
Y_MAX = -123.35944
SPEED_KM = 40 # average speed in km/h

# Constraints for the maximum and minimum battery levels for generated cars
BATTERY_MIN = 20 # 20%
BATTERY_MAX = 65 # 60%
ENERGY_CONSUMPTION_RATE: float= 0.0# (kWh/km)
BATTERY_CAPACITY: float = 0.0 # (kWh)
MIN_BATTERY_THRESHOLD = 5 # minimum battery level to consider driving to a station (%)

class Car:
    position: tuple[float, float]
    battery_level_initial: float
    system_arrival_time: float
    reachable_stations: list[Station_Meta]

    def __init__(self, system_arrival_time: float, stations: Iterable[Charging_Station]):
        self.system_arrival_time = system_arrival_time # time car was spawned in the system
        self.position = self._set_position() # the car spawn position 
        self.battery_level_initial = self._set_battery_level_initial() 
        self.reachable_stations = self._set_reachable_stations(stations) # list of station meta objects

    def _set_position(self) -> tuple[float, float]:
        x = np.random.uniform(X_MIN, X_MAX)
        y = np.random.uniform(Y_MIN, Y_MAX)
        return (x, y) # the car spawn position
    
    def _set_battery_level_initial(self) -> float:
        return np.random.uniform(BATTERY_MIN, BATTERY_MAX) # initial battery level (%)
    
    def _set_reachable_stations(self, stations: Iterable[Charging_Station]) -> list[Station_Meta]:
        reachable_stations = [] # list of station meta objects

        for station in stations:
            # get the estimate soc after drive
            result = self._get_estimated_soc_after_drive(station)
            if result is None:
                continue # car cannot reach this station, check the next station

            # otherwise the car can reach the station so make a station_meta object
            soc_after_drive, distance_km = result 
            drive_time_minutes = distance_km / (SPEED_KM / 60)  # get the drive time in minutes
            station_meta = Station_Meta(
                station, # station object
                distance_km, # eculidian distance from spawn point of car to station
                drive_time_minutes, # drive time from spawn point of car to station
                soc_after_drive # estimated soc after driving to station, could also add estimated charge time fast and slow
            )
            # add to reachable stations list
            reachable_stations.append(station_meta)
        return reachable_stations # return list of station_meta objects
    
    def _get_estimated_soc_after_drive(self, station) -> tuple[float, float] | None:
        distance_km = self._get_euclidian_to_station(station)

        # energy used to drive there (one-way)
        energy_used = distance_km * ENERGY_CONSUMPTION_RATE

        # SoC after driving to the station (percent)
        soc_after_drive = self.battery_level_initial - (energy_used / BATTERY_CAPACITY) * 100

        # if the car cannot even physically reach the station
        if soc_after_drive < MIN_BATTERY_THRESHOLD:
            return None   

        return (soc_after_drive, distance_km)

    def _get_euclidian_to_station(self, station) -> float:
        station_position = station.position # (x,y) coordinate of station
        distance_km = np.sqrt((self.position[0] - station_position[0])**2 + (self.position[1] - station_position[1])**2)
        return distance_km

if __name__ == "__main__":
    car = Car()
    print("Position:", car.position)
    print("Battery:", car.battery_level)