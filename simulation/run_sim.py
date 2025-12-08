import csv
from system import EV_Charging_System
from routing_policies import RoutingPolicy


def run_experiments():

    grouped_results = {}
    
    num_runs = 5
    seeds = [100 + i * 2 for i in range(num_runs)] 

    policies = [
        RoutingPolicy.CLOSEST_STATION_FIRST,
        RoutingPolicy.SHORTEST_ESTIMATED_WAIT,
    ]
    

    for seed in seeds:

        grouped_results[seed] = {"Seed": seed} 
        
        for policy in policies:
            
            sim = EV_Charging_System(policy, num_delays_required=10000, seed=seed)
            sim.main()
            
            raw_result = sim.get_results()

            policy_name = raw_result["policy"]
            

            if policy_name == "CLOSEST_STATION_FIRST":
                prefix = "ClosestStation"
            elif policy_name == "SHORTEST_ESTIMATED_WAIT":
                prefix = "ShortestWait"
            else:
                prefix = policy_name

            grouped_results[seed][f"{prefix}_AvgWaitTime_min"] = raw_result["avg_wait_time"]
            grouped_results[seed][f"{prefix}_AvgTotalTime_min"] = raw_result["avg_time_in_system"]
            grouped_results[seed][f"{prefix}_Balking_count"] = raw_result["total_balking"]

    final_results_list = list(grouped_results.values())
    
    headers = [
        "Seed", 
        "ClosestStation_AvgWaitTime_min", 
        "ClosestStation_AvgTotalTime_min",
        "ClosestStation_Balking_count",
        "ShortestWait_AvgWaitTime_min",
        "ShortestWait_AvgTotalTime_min",
        "ShortestWait_Balking_count",
    ]
    
    with open("simulation_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(final_results_list)

    print("\n CSV written: simulation_results_pivoted_descriptive.csv")


if __name__ == "__main__":
    run_experiments()