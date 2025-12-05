## Car
| Attribute | Type | Description |
|----------|------|-------------|
| `position` | `(float, float)` | Random (x, y) spawn location. |
| `battery_level_initial` | `float` | Initial SoC (%) when the car enters the system. |
| `system_arrival_time` | `float` | Simulation time at which the car was spawned. |
| `reachable_stations` | `list[Station_Meta]` | Stations the car can physically reach. |
| `target_charge_level` | `float` | Car's chosen final battery %; the system does not know this value. |
| `time_charging` | `float \| None` | Time the car spent charging. |
| `routed_drive_time` | `float \| None` | Drive time to the station selected by the routing algorithm. |
| `routed_arrival_time_queue` | `float` | Time the car arrives at the chosen station’s queue. |
| `total_time_in_system` | `float \| None` | Total time from system entry to completion of charging. |

###  _set_position(self)
The purpose of this function is to randomly generate the x and y coordinates of the car within the simulation plane.
The x coordinate in the car is generated between X_MIN and X_MAX, defined in Constants.py. The y coordinate is similarly generated between Y_MIN and Y_MAX.
If the car's x,y coordinates is generated at exactly the station's same x,y coordinates, this is assumed to be that the car is already at the station and the drive time is 0.
In other words, it is permissable for the coordinates of the station and the car to be the same. 

### _set_battery_level_initial
This generates the car's initial SOC defined between a minimum and maximum battery level.

### _set_target_charge_level(self)
In order to model the real world scenario where people are not always charging to the same value, the target charge level
for the car to charge to is also randomly generated between 20% and 80%. These parameters are defined in Constants.py as MIN_CHARGE_AMOUNT and TARGET_MAX_FINAL_BATTERY. In order to generate a target charge that is not
bellow the initial soc of the car, the following formula was used: $$\text{target charge level} = Uniform(SOC_{initial}+\delta_min, SOC_{max})$$, where $\delta_{min}$ is the minimum amount that the car must charge before leaving the station.

### get_total_time_in_system(self, sim_time: float)
This is used for the system metrics after a car has been serviced. The equation used is $sim \_ time - system\_arrival\_time = \Delta_{time\_in\_system}$

### get_estimated_soc_after_driving_km(self, distance_km)
This is a helper function that is used in _set_reachable_stations(self, stations: Iterable[Charging_Station]) to determine how much battery is drained by driving a certain distance. This is used to set the soc_after_drive in the Station_Meta object. This is used to calculate what the service rate is for the car once it is at the charging station.
It also helps filter out the stations which are "unreachable" by the car because they car will be bellow the maximum threshold for the battery after driving. This is done by returning "None" if the minimum battery threshold is violated and the '_set_reachable_stations' function checks this condition.
1. Calculate energy consumed:  
   `energy_used = distance_km * ENERGY_CONSUMPTION_RATE`
2. Convert energy to a percentage of the battery capacity.
3. Subtract that value from the initial state-of-charge.
4. If the resulting SoC is below `MIN_BATTERY_THRESHOLD`, return `None` (station unreachable).
5. Otherwise, return the estimated SoC (%).

### _get_euclidian_to_station(self, station)
This is the second helper function that is used in '_set_reachable_stations'. It's purpose is to get the euclidean distance from the cars spawn point to the station specified in the function parameters.
$$d = \sqrt{(x_{\mathrm{car}} - x_{\mathrm{station}})^2 + (y_{\mathrm{car}} - y_{\mathrm{station}})^2}$$



### _set_reachable_stations(self, stations: Iterable[Charging_Station])
This function helps collect the meta data for the relationship between a car and a charging station and filter out any stations that all routing policies should not consider because they are unfeasible for the car to reach.
This includes the distance to that charging station, the drive time to the charging station and the soc the car will have after completing the drive.
This function loops through all of the stations in the system. For each station it:
- gets the euclidean distance between the cars initial spawn point and the station
- Calculates the soc after driving to that distance
- It checks the returned value from get_estimated_soc_driving_km which returns "None" if the vehicle cannot reach the station
-   If "None" is returned, this station is not added to the reachable station list and the next station in the system is considered

