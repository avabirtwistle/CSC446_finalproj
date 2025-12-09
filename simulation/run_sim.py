import csv
from system import EV_Charging_System
from routing_policies import RoutingPolicy

SEEDS = [3, 200, 303, 670, 1000]
POLICIES = [
    RoutingPolicy.CLOSEST_STATION_FIRST,
    RoutingPolicy.SHORTEST_ESTIMATED_WAIT,
]
NUM_DELAYS_REQUIRED = 100000
OUTPUT_FILE = "simulation_results.csv"

def run_replications():

    table = [{"seed": seed} for seed in SEEDS]

    for policy in POLICIES:
        pol_name = policy.name.lower()

        for i, seed in enumerate(SEEDS):
            sim = EV_Charging_System(
                policy,
                num_delays_required=NUM_DELAYS_REQUIRED,
                seed=seed
            )
            sim.main()

            wait_times = sim.wait_times
            avg_wait = sum(wait_times) / len(wait_times) if wait_times else 0

            table[i][pol_name] = avg_wait

    fieldnames = ["seed"] + [p.name.lower() for p in POLICIES]
    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(table)

if __name__ == "__main__":
    run_replications()
