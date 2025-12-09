import csv
from system import EV_Charging_System
from routing_policies import RoutingPolicy

# ---------- CONFIG ----------
SEEDS = [3, 200, 303, 670, 1000]
POLICIES = [
    RoutingPolicy.CLOSEST_STATION_FIRST,
    RoutingPolicy.SHORTEST_ESTIMATED_WAIT,
]
NUM_DELAYS_REQUIRED = 1000
OUTPUT_FILE = "results.csv"
# ----------------------------

def run_experiments():
    # initialize table: list of dict rows
    table = [{"seed": seed} for seed in SEEDS]

    for policy in POLICIES:
        pol_name = policy.name.lower()  # for column heading

        for i, seed in enumerate(SEEDS):
            print(f"\n=== Running policy={policy.name}, seed={seed} ===")

            sim = EV_Charging_System(
                policy,
                num_delays_required=NUM_DELAYS_REQUIRED,
                seed=seed
            )
            sim.main()

            wait_times = sim.wait_trace
            avg_wait = sum(wait_times) / len(wait_times) if wait_times else 0

            # store result in correct row/column
            table[i][pol_name] = avg_wait

            print(f"{policy.name} avg wait = {avg_wait:.3f} minutes")

    # write output CSV
    fieldnames = ["seed"] + [p.name.lower() for p in POLICIES]
    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(table)

    print(f"\n📁 Results saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    run_experiments()
