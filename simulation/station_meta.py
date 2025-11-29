#station mapping.py 

from charging_station import Charging_Station


class Station_Meta:
    station: Charging_Station            # the actual station object
    distance_km: float                  # the euclidean distance for the ev to the station
    drive_time_min: float               # travel time
    soc_after_drive: float              # SoC (%) after getting there

    def __init__(self, station, distance_km, drive_time_min, soc_after_drive):
        self.station = station
        self.distance_km = distance_km
        self.drive_time_min = drive_time_min
        self.soc_after_drive = soc_after_drive