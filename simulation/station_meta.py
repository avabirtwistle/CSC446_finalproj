from charging_station import Charging_Station

# Metadata about a station for a specific car
# This includes distance, drive time, and estimated SoC after driving there
# Used in routing decisions
# the actual routed station object is not stored here and only in the car object
ESTIMATION_FACTOR = 1.2  # factor to multiply estimated wait times by for estimation
class Station_Meta:
    station: Charging_Station            # the actual station object
    distance_km: float                  # the euclidean distance for the ev to the station
    drive_time_minutes: float               # travel time
    soc_after_drive: float              # SoC (%) after getting there

    def __init__(self, station, distance_km, drive_time_minutes, soc_after_drive):
        self.station = station           # the actual station object this meta refers to
        self.distance_km = distance_km  # the euclidean distance for the ev to the station
        self.drive_time_minutes = drive_time_minutes # the travel time to the station in minutes for the ev
        self.soc_after_drive = soc_after_drive # SoC (%) after the ev gets there

    def get_drive_time_minutes(self) -> float:
        return self.drive_time_minutes # return the drive time in minutes

    def get_station_id(self) -> int:
        return self.station.station_id # return the station id
    
    def get_effective_queue_length(self, void_counter) -> int:
        return len(self.station.queue) + void_counter[self.station.station_id - 1]  # return the current queue length at the station and the current length of void cars for the station