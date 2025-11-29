import numpy as np

from station_meta import Station_Meta
from charging_station import Charging_Station
from typing import Iterable
# Constraints for the min and max distance for the size of the simulation plane can be adjusted based on the desired area
X_MIN = 0.0 
X_MAX = 9.3
Y_MIN = 0.0
Y_MAX = 5.2
SPEED_KM = 40 # average speed in km/h

# Constraints for the maximum and minimum battery levels for generated cars
BATTERY_MIN = 20 # 20%
BATTERY_MAX = 65 # 60%
ENERGY_CONSUMPTION_RATE: float= 0.20# (kWh/km)
BATTERY_CAPACITY: float = 75.0 # (kWh)
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
        """
        Builds the list of reachable stations.

        For each station, compute distance, drive time, and SoC after drive. 
        TODO handle case where no stations are reachable, raise exception? and should track these 

        Returns a list of Station_Meta objects only for stations the car can reach.
        """
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
            # TODO: there must be at least one reachable station, otherwise the car cannot be serviced... need to determine the python equivalent for throwing and catching exceptions..
        return reachable_stations # return list of station_meta objects 
    
    def _get_estimated_soc_after_drive(self, station) -> tuple[float, float] | None:
        """
        Computes the expected SoC (%) after driving from the EV's current position
        to the specified charging station.

        Returns (soc_after_drive, distance_km), or None if the vehicle cannot reach
        the station (SoC would fall below MIN_BATTERY_THRESHOLD).
        """
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
        """
        Compute the Euclidean distance from the cars spawn point to the station specified.

        Returns the distance in kilometers.
        """
        station_position = station.position # (x,y) coordinate of station
        distance_km = np.sqrt((self.position[0] - station_position[0])**2 + (self.position[1] - station_position[1])**2)
        return distance_km
    
if __name__ == "__main__":
    # Stations placed inside the km-plane (0–9.3 km, 0–5.2 km)
    s1 = Charging_Station(station_id=1, position=(1.0, 1.0), sim_time=0.0)   # close
    s2 = Charging_Station(station_id=2, position=(5.0, 3.0), sim_time=0.0)   # medium
    s3 = Charging_Station(station_id=3, position=(9.0, 5.0), sim_time=0.0)   # far
    stations = [s1, s2, s3]

    car = Car(system_arrival_time=0.0, stations=stations)

    print("\n=== CAR INFO ===")
    print(f"Spawn Position: {car.position}")
    print(f"Initial Battery: {car.battery_level_initial:.2f}%")

    print("\n=== STATION STATUS ===")
    for station in stations:
        distance = car._get_euclidian_to_station(station)
        result = car._get_estimated_soc_after_drive(station)

        print(f"\nStation {station.station_id}:")
        print(f"  Distance: {distance:.2f} km")

        if result is None:
            print("  Status: UNREACHABLE (insufficient battery)")
        else:
            soc_after, _ = result
            print(f"  SoC After Drive: {soc_after:.2f}%")
            print("  Status: REACHABLE")

    print("\n=== REACHABLE STATIONS ===")
    if not car.reachable_stations:
        print("  None")
    else:
        for meta in car.reachable_stations:
            print(f"  Station {meta.station.station_id}:")
            print(f"    Distance:   {meta.distance_km:.2f} km")
            print(f"    Drive Time: {meta.drive_time_min:.2f} min")
            print(f"    SoC After:  {meta.soc_after_drive:.2f}%")
