import csv
import math
import matplotlib.pyplot as plt
from scipy.stats import t

INPUT_FILE = "results.csv"

def load_results():
    seeds = []
    p1 = []
    p2 = []
    with open(INPUT_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            seeds.append(int(row["seed"]))
            p1.append(float(row["closest_station_first"]))
            p2.append(float(row["shortest_estimated_wait"]))
    return seeds, p1, p2

def compute_crn_confidence_interval(p1, p2):
    R = len(p1)
    D = [p1[i] - p2[i] for i in range(R)]

    D_bar = sum(D) / R
    S2_D = sum((d - D_bar)**2 for d in D) / (R - 1)
    se = math.sqrt(S2_D / R)

    # 95% CI
    t_val = t.ppf(1 - 0.025, R - 1)
    H = t_val * se

    return D, D_bar, H

def plot_differences(seeds, D, D_bar, H):
    plt.figure()
    plt.axhline(D_bar, linestyle="--", label=f"Mean diff = {D_bar:.3f}")
    plt.axhline(D_bar + H, linestyle=":", label=f"95% CI = [{D_bar - H:.3f}, {D_bar + H:.3f}]")
    plt.axhline(D_bar - H, linestyle=":")

    plt.scatter(seeds, D)
    plt.plot(seeds, D)

    plt.title("Paired Differences (CRN)")
    plt.xlabel("Seed")
    plt.ylabel("Difference in Avg Wait (Policy1 − Policy2)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    seeds, p1, p2 = load_results()
    D, D_bar, H = compute_crn_confidence_interval(p1, p2)

    print("\nPaired Differences:")
    for s, d in zip(seeds, D):
        print(f"Seed {s}: {d:.4f}")

    print(f"\nMean Difference (D̄) = {D_bar:.4f}")
    print(f"Half-width (H) = {H:.4f}")
    print(f"95% CI = [{D_bar - H:.4f}, {D_bar + H:.4f}]")

    plot_differences(seeds, D, D_bar, H)
