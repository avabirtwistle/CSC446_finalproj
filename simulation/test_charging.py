# test_charging_station_manual.py

import heapq
from charging_station import Charging_Station
from event import EventType
from constants import FAST_CHARGER_POWER_KW, SLOW_CHARGER_POWER_KW, ASSUMED_SOC_FINAL

# ---- Dummy classes to stand in for your real ones ----

class DummyCar:
    def __init__(self, battery_level_initial=30.0, target_charge_level=80.0):
        self.battery_level_initial = battery_level_initial
        self.target_charge_level = target_charge_level
        self.time_charging = 0.0

    # if your compute_estimated_wait_time still uses get_soc_initial()
    def get_soc_initial(self):
        return self.battery_level_initial

class DummyRouting:
    def __init__(self, car, station):
        self.car = car
        self._chosen_station = station

    def get_chosen_station_(self):
        return self._chosen_station

# fake station meta object, just needs station_id
class DummyStationMeta:
    def __init__(self, station_id):
        self.station_id = station_id

# ---- Fake sim_time ----
current_time = 0.0
def sim_time():
    return current_time

# ---- Set up a simple scenario ----
def main():
    global current_time

    # Create station 1 at position 0.0
    station = Charging_Station(
        station_id=1,
        position=0.0,
        sim_time=sim_time
    )

    # Event queue: list of (time, event_type, routing)
    event_queue = []

    # Create two cars that will arrive in the future
    car1 = DummyCar(battery_level_initial=40.0, target_charge_level=80.0)
    car2 = DummyCar(battery_level_initial=50.0, target_charge_level=80.0)
    car3 = DummyCar(battery_level_initial=60.0, target_charge_level=80.0)
    
    station_meta = DummyStationMeta(station_id=1)

    # Car1 arrives at t=5, Car2 arrives at t=10
    heapq.heappush(event_queue, (5.0, EventType.ARRIVAL_STATION_1, DummyRouting(car1, station_meta)))
    heapq.heappush(event_queue, (10.0, EventType.ARRIVAL_STATION_1, DummyRouting(car2, station_meta)))
    heapq.heappush(event_queue, (15.0, EventType.ARRIVAL_STATION_1, DummyRouting(car3, station_meta)))

    # Choose a query time where the new car would arrive
    query_time = 12.0

    # Set the "current" sim time (what Charging_Station.sim_time() will see)
    current_time = 0.0

    wait = station.compute_estimated_wait_time(
        event_queue=list(event_queue),  # pass a copy just in case
        query_time=query_time,
        station_id=1
    )

    print(f"Estimated wait time at station 1 for a car arriving at t={query_time}: {wait:.2f} minutes")

if __name__ == "__main__":
    main()
