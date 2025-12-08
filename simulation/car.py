import numpy as np

from station_meta import Station_Meta
from typing import Iterable
from charging_station import Charging_Station
from constants import ENERGY_CONSUMPTION_RATE, BATTERY_CAPACITY, MIN_BATTERY_THRESHOLD, BATTERY_MIN, BATTERY_MAX, TARGET_MAX_FINAL_BATTERY, MIN_CHARGE_AMOUNT, X_MIN, X_MAX, Y_MIN, Y_MAX, SPEED_KM

class Car:
    position: tuple[float, float] # (x,y) coordinate
    battery_level_initial: float # initial battery level (%)
    system_arrival_time: float  # time car was spawned in the system
    reachable_stations: list[Station_Meta] # list of reachable station meta objects
    time_charging: float | None # time spent charging (minutes)
    target_charge_level: float # target charge level (%)
    routed_drive_time: float | None # drive time to routed station (minutes)
    routed_arrival_time: float # arrival time at station
    total_time_in_system: float | None # total time in system (minutes)

    def __init__(self, system_arrival_time: float, stations: Iterable[Charging_Station]):
        self.system_arrival_time = system_arrival_time 
        self.position = self._set_position()
        self.battery_level_initial = self._set_battery_level_initial() 
        self.target_charge_level = self._set_target_charge_level() 
        self.reachable_stations = self._set_reachable_stations(stations) 

        # Updated once car is routed
        self.routed_drive_time = None
        self.routed_arrival_time = 0.0
        self.time_charging = None
        self.total_time_in_system = None
        self.time_in_queue = 0.0

    def _set_position(self) -> tuple[float, float]:
        x = np.random.uniform(X_MIN, X_MAX)
        y = np.random.uniform(Y_MIN, Y_MAX)
        return (x, y) # the car spawn position
    
    def _set_target_charge_level(self) -> float:
        """
        Sets a target charge level between defined min and max final battery levels.
        In the real world, this simulates a human decision of how much to charge.
        Since the system is simulating routing for example by using an app, the system has no knowledge
        of the target charge level the user is thinking of when they want to charge.
        Because the system has no knowledge of this target charge level, it cannot use it in routing decisions
        and must rely on other metrics such as distance, estimated wait time, etc.

        Returns the target charge level (%).
        """
        return np.random.uniform(self.battery_level_initial + MIN_CHARGE_AMOUNT, TARGET_MAX_FINAL_BATTERY)

    def get_total_time_in_system(self, sim_time: float) -> float:
        """
        Computes the total time the car has been in the system.
        Returns total time in system (minutes).
        """
        return sim_time - self.system_arrival_time

    def _set_battery_level_initial(self) -> float:
        """
        Sets an initial battery level between defined min and max battery levels.
        Returns the initial battery level (%).
        """
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
            distance_km = self._get_euclidian_to_station(station)
            soc_after_drive = self.get_estimated_soc_after_driving_km(distance_km)

            if soc_after_drive is None:
                continue # car cannot reach this station, check the next station

            # otherwise station is reachable, create station meta object
            drive_time_minutes = distance_km / (SPEED_KM / 60)  # get the drive time in minutes
            station_meta = Station_Meta(
                station, # station object
                distance_km, # eculidian distance from spawn point of car to station
                drive_time_minutes, # drive time from spawn point of car to station
                soc_after_drive # estimated soc after driving to station
            )
            # add to reachable stations list
            reachable_stations.append(station_meta)

        return reachable_stations # return list of station_meta objects 
    
    def get_estimated_soc_after_driving_km(self, distance_km) -> float | None:
        """
        Computes the expected SoC (%) after driving from the EV's current position
        to the specified charging station.

        Returns soc_after_drive, or None if the vehicle cannot reach it the station (SoC would fall below MIN_BATTERY_THRESHOLD).
        """
        # energy used to drive there (one-way)
        energy_used = distance_km * ENERGY_CONSUMPTION_RATE

        # SoC after driving to the station (percent)
        soc_after_drive = self.battery_level_initial - (energy_used / BATTERY_CAPACITY) * 100

        # if the car cannot even physically reach the station
        if soc_after_drive < MIN_BATTERY_THRESHOLD:
            return None   
        return soc_after_drive

    def _get_euclidian_to_station(self, station) -> float:
        """
        Compute the Euclidean distance from the cars spawn point to the station specified.

        Returns the distance in kilometers.
        """
        station_position = station.position # (x,y) coordinate of station
        distance_km = np.sqrt((self.position[0] - station_position[0])**2 + (self.position[1] - station_position[1])**2)
        return distance_km
  