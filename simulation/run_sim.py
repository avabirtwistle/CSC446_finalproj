import csv
from system import EV_Charging_System
from routing_policies import RoutingPolicy


def run_experiments():
    results = []
    num_runs = 2
    seeds = [100 + i for i in range(num_runs)]

    policies = [
        RoutingPolicy.CLOSEST_STATION_FIRST,
        RoutingPolicy.SHORTEST_ESTIMATED_WAIT,
    ]

    for seed in seeds:
        for policy in policies:
            sim = EV_Charging_System(policy, num_delays_required=100, seed=seed)
            sim.main()
            results.append(sim.get_results())

    # Write CSV
    with open("simulation_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print("CSV written: simulation_results.csv")


if __name__ == "__main__":
    run_experiments()
