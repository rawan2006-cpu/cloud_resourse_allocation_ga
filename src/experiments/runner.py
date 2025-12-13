# src/experiments/runner.py
# src/experiments/runner.py

import os
import csv
import json
from datetime import datetime
import matplotlib.pyplot as plt

# ===============================
# Project paths (ABSOLUTE)
# ===============================
THIS_DIR = os.path.dirname(__file__)                 # src/experiments
PROJECT_ROOT = os.path.abspath(os.path.join(THIS_DIR, "..", ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")
PLOTS_DIR = os.path.join(RESULTS_DIR, "plots")

os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(PLOTS_DIR, exist_ok=True)

print("PROJECT_ROOT:", PROJECT_ROOT)
print("DATA_DIR:", DATA_DIR)
print("RESULTS_DIR:", RESULTS_DIR)
print("PLOTS_DIR:", PLOTS_DIR)

# ===============================
# Project imports
# ===============================
from src.sim.entities import Task, VM, Host
from src.baselines.heuristics import first_fit
from src.ga.ga_core import run_ga
from src.ga.fitness import evaluate_solution


# ===============================
# Load workload
# ===============================
def load_tasks_from_csv(path):
    tasks = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            tasks.append(
                Task(
                    id=i,
                    cpu=float(row.get("cpu", 100)),
                    mem=float(row.get("mem", 128)),
                    length=float(row.get("length", 1000)),
                    arrival=float(row.get("arrival", 0)),
                )
            )
    return tasks


# ===============================
# Plotting utilities
# ===============================
def save_bar_plot(values, labels, title, ylabel, filename):
    plt.figure()
    plt.bar(labels, values)
    plt.ylabel(ylabel)
    plt.title(title)
    path = os.path.join(PLOTS_DIR, filename)
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved plot:", path)


# ===============================
# Main experiment
# ===============================
def example_run():

    # -------- Load tasks --------
    csv_path = os.path.join(DATA_DIR, "sample_google_trace.csv")
    print("\nLoading workload from:", csv_path)
    tasks = load_tasks_from_csv(csv_path)
    print("Number of tasks:", len(tasks))

    # -------- Infrastructure --------
    vms = [VM(id=i, cpu_capacity=1000, mem_capacity=2048) for i in range(10)]
    hosts = [Host(id=i, cpu_capacity=10000, mem_capacity=32768) for i in range(3)]

    # ===============================
    # Baseline: First-Fit
    # ===============================
    baseline_chrom = first_fit(tasks, vms)
    baseline_fitness, baseline_info = evaluate_solution(
        baseline_chrom, tasks, vms, hosts
    )

    print("\n--- BASELINE RESULTS ---")
    print("Fitness:", baseline_fitness)
    print("Metrics:", baseline_info)

    # ===============================
    # Genetic Algorithm
    # ===============================
    print("\n--- RUNNING GENETIC ALGORITHM ---")
    best_chrom, best_fitness, best_info = run_ga(
        tasks,
        vms,
        hosts,
        pop_size=30,
        gen=50,
        pc=0.8,
        pm=0.05,
        seed=42,
    )

    print("\n--- GA RESULTS ---")
    print("Best fitness:", best_fitness)
    print("Metrics:", best_info)

    # ===============================
    # Save CSV + JSON
    # ===============================
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    csv_file = os.path.join(RESULTS_DIR, "runs_summary.csv")
    write_header = not os.path.exists(csv_file)

    with open(csv_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "timestamp",
                "baseline_fitness",
                "ga_best_fitness",
                "baseline_makespan",
                "ga_makespan",
                "baseline_energy",
                "ga_energy",
                "baseline_sla_violations",
                "ga_sla_violations",
            ],
        )
        if write_header:
            writer.writeheader()

        writer.writerow(
            {
                "timestamp": timestamp,
                "baseline_fitness": baseline_fitness,
                "ga_best_fitness": best_fitness,
                "baseline_makespan": baseline_info["makespan"],
                "ga_makespan": best_info["makespan"],
                "baseline_energy": baseline_info["energy"],
                "ga_energy": best_info["energy"],
                "baseline_sla_violations": baseline_info["sla_violations"],
                "ga_sla_violations": best_info["sla_violations"],
            }
        )

    json_file = os.path.join(RESULTS_DIR, f"run_{timestamp}.json")
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "baseline": baseline_info,
                "ga": best_info,
                "baseline_fitness": baseline_fitness,
                "ga_best_fitness": best_fitness,
            },
            f,
            indent=2,
        )

    print("\nSaved results:")
    print(" -", csv_file)
    print(" -", json_file)

    # ===============================
    # Generate & save plots
    # ===============================
    save_bar_plot(
        [baseline_fitness, best_fitness],
        ["Baseline", "GA"],
        "Fitness Comparison",
        "Fitness (lower is better)",
        "fitness_comparison.png",
    )

    save_bar_plot(
        [baseline_info["energy"], best_info["energy"]],
        ["Baseline", "GA"],
        "Energy Consumption",
        "Energy",
        "energy_comparison.png",
    )

    save_bar_plot(
        [baseline_info["makespan"], best_info["makespan"]],
        ["Baseline", "GA"],
        "Makespan Comparison",
        "Time",
        "makespan_comparison.png",
    )

    save_bar_plot(
        [baseline_info["sla_violations"], best_info["sla_violations"]],
        ["Baseline", "GA"],
        "SLA Violations",
        "Count",
        "sla_violations.png",
    )


# ===============================
# Entry point
# ===============================
if __name__ == "__main__":
    example_run()
