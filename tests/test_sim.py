# tests/test_sim.py

# Sanity-check the system
#
# Ensure fitness, GA, and baseline work
#
# Detect errors BEFORE demo day

import os
from src.sim.entities import Task, VM, Host
from src.baselines.heuristics import first_fit
from src.ga.ga_core import run_ga
from src.ga.fitness import evaluate_solution


def test_basic_simulation():
    # Create small dummy workload
    tasks = [
        Task(id=0, cpu=100, mem=128, length=1000, arrival=0),
        Task(id=1, cpu=200, mem=256, length=1500, arrival=1),
        Task(id=2, cpu=150, mem=128, length=1200, arrival=2),
    ]

    vms = [VM(id=i, cpu_capacity=500, mem_capacity=1024) for i in range(2)]
    hosts = [Host(id=0, cpu_capacity=2000, mem_capacity=8192)]

    # Baseline
    chrom = first_fit(tasks, vms)
    f_base, info_base = evaluate_solution(chrom, tasks, vms, hosts)

    assert isinstance(f_base, float)
    assert "makespan" in info_base

    # GA
    best, best_f, best_info = run_ga(
        tasks, vms, hosts, pop_size=10, gen=5
    )

    assert best is not None
    assert isinstance(best_f, float)
    assert "energy" in best_info

    print("✔ Basic simulation test passed")


if __name__ == "__main__":
    test_basic_simulation()



