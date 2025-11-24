## Shortest Estimated Time
The Shortest Estimated Time routing policy selects a charging location by minimizing the total expected time for the vehicle. This total time includes both the travel time from the vehicle’s current position and the expected waiting time in each station’s queue.
### Algorithm Description
1. **Compute Battery Consumption to Reach All Stations**
   - For each charging station, calculate how much battery would be used to reach it from the vehicles (x,y) coordinates
2. **Discard Unreachable Stations**
   - Any location requiring more battery than the vehicle currently has is removed
3. **Retrieve Expected Wait Time**
   - For each feasible location, obtain the predicted waiting time from its queue (based on the number of vehicles already there and their charging status)
4. **Compute Travel Time and Total Estimated Time**
   - For each location compute travel time from the vehicle’s current position
   - Add travel time and expected waiting time to get a total estimated time
5. **Sort by Shortest Total Time**
   - Create an ordered list of charging locations in ascending order of total estimated time.
6. **Iterative Selection Loop**
   - Remove the location at the head of the list (minimum total time)
   - If the queue at that location exceeds its maximum allowable length, check if battery exceeds minimum battery threshold for balking: 
       1. If yes, it moves to the next best station.
       2. If no, the vehicle balks (leaves the system).
   - If the queue length is acceptable, the vehicle joins the queue.
7. **Termination**
 - The process ends once the vehicle joins a queue or all possible stations are exhausted.

## Shortest Distance
The Shortest Distance routing policy selects a charging location by choosing the station that is geographically closest to the vehicle’s current (x,y) position, after removing any stations the vehicle cannot reach with its remaining battery.

### Algorithm Description
1. **Compute Battery Consumption to Reach All Stations**
   - For each charging station, calculate how much battery would be used to reach it from the vehicle’s \((x,y)\) coordinates.

2. **Discard Unreachable Stations**
   - Any station requiring more battery than the vehicle currently has is removed.

3. **Compute Distances**
   - For each remaining feasible station, compute the geometric distance between the vehicle’s position and the station’s coordinates.

4. **Sort by Shortest Distance**
   - Create an ordered list of feasible stations from smallest distance to largest distance.

5. **Iterative Selection Loop**
   - Remove the station at the head of the list (minimum distance).
   - If the queue at that station exceeds its maximum allowable length, check if the battery exceeds the minimum battery threshold for balking:
     1. If yes, move to the next closest station.
     2. If no, the vehicle balks (leaves the system).
   - If the queue length is acceptable, the vehicle joins the queue.

6. **Termination**
   - The process ends once the vehicle joins a queue or all possible stations are exhausted.
<p align="center">
<img src="https://github.com/avabirtwistle/CSC446_finalproj/blob/main/diagram.png" width="700">
</p>

