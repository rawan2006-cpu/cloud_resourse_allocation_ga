# src/baselines/heuristics.py

# first-fit algorithm used for assigning tasks to virtual machines in a cloud environment
# it is simple, efficient and used as a baseline to compare with higher algorithms as genetic algorithms
# it is a greedy approach always picks the first available spot
def first_fit(tasks, vms):
    chrom = [-1] * len(tasks)  # chrom[i] = index of VM assigned to task i
    # Make a copy of VM loads to avoid modifying the original VMs
    vm_cpu_loads = [vm.cpu_load for vm in vms]
    vm_mem_loads = [vm.mem_load for vm in vms]

    for i, t in enumerate(tasks):
        assigned = False
        for j, vm in enumerate(vms):
            if (vm_cpu_loads[j] + t.cpu <= vm.cpu_capacity) and \
               (vm_mem_loads[j] + t.mem <= vm.mem_capacity):
                chrom[i] = j
                vm_cpu_loads[j] += t.cpu
                vm_mem_loads[j] += t.mem
                assigned = True
                break
        if not assigned:
            chrom[i] = -1  # Could not assign
    return chrom

def round_robin(tasks, vms):
    chrom = [-1]*len(tasks)
    for i, t in enumerate(tasks):
        chrom[i] = i % len(vms)
    return chrom
