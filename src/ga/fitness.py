from src.sim.cluster import Cluster
from copy import deepcopy

def evaluate_solution(chrom, tasks, vms, hosts, weights=None):
    """
    Evaluates a solution (chromosome) for the cloud resource allocation problem.

    Args:
        chrom: List[int]
            A list where chrom[i] is the index of the VM assigned to task i.
            If chrom[i] == -1, the task is unassigned.
        tasks: List[Task]
            List of Task objects to be scheduled.
        vms: List[VM]
            List of VM objects (used as templates for simulation).
        hosts: List[Host]
            List of Host objects (used as templates for simulation).
        weights: dict (optional)
            Dictionary specifying the importance of each metric in the fitness calculation.
            Example: {"makespan": 0.4, "energy": 0.3, "util": 0.2, "sla": 0.1}

    Returns:
        fitness: float
            The overall fitness score (lower is better).
        metrics: dict
            Dictionary containing detailed metrics for analysis.
    """

    # Default weights if not provided
    if weights is None:
        weights = {"makespan": 0.4, "energy": 0.3, "util": 0.2, "sla": 0.1}

    # Create deep copies of VMs and Hosts to avoid modifying originals
    vms_copy = deepcopy(vms)
    hosts_copy = deepcopy(hosts)

    # Initialize the simulation cluster
    cluster = Cluster(hosts_copy, vms_copy)

    # Assign VMs to hosts (e.g., round-robin)
    for idx, vm in enumerate(vms_copy):
        host_idx = idx % len(hosts_copy)
        cluster.assign_vm_to_host(idx, host_idx)

    # Assign tasks to VMs according to the chromosome
    unassigned_tasks = 0
    for t_idx, vm_idx in enumerate(chrom):
        if vm_idx != -1 and 0 <= vm_idx < len(vms_copy):
            cluster.assign_task_to_vm(tasks[t_idx], vm_idx)
        else:
            # Task is unassigned (e.g., no suitable VM found)
            unassigned_tasks += 1

    # Calculate metrics
    makespan = cluster.makespan()           # Total time to finish all tasks
    energy = cluster.total_energy()         # Total energy consumed by all hosts
    avg_util = sum(h.utilization() for h in hosts_copy) / len(hosts_copy)  # Average host utilization

    # SLA violations: Example criterion - tasks longer than 1000 units
    sla_violations = sum(
        1 for vm in vms_copy for t in getattr(vm, 'tasks', []) if getattr(t, 'length', 0) > 1000
    )
    # Optionally, count unassigned tasks as SLA violations
    sla_violations += unassigned_tasks

    # Fitness calculation (lower is better)
    # You may want to normalize metrics for fair weighting in real experiments
    fitness = (
        weights["makespan"] * makespan +
        weights["energy"] * energy -
        weights["util"] * avg_util +
        weights["sla"] * sla_violations
    )

    # Return both the fitness and detailed metrics for analysis
    metrics = {
        "fitness": fitness,
        "makespan": makespan,
        "energy": energy,
        "avg_utilization": avg_util,
        "sla_violations": sla_violations,
        "unassigned_tasks": unassigned_tasks
    }
    return fitness, metrics
