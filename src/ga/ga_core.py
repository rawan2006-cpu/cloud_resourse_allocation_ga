# src/ga/ga_core.py
import random
from copy import deepcopy
from typing import List, Tuple, Optional
import numpy as np

# Import the fitness evaluator (should return either float or (float, dict))
from src.ga.fitness import evaluate_solution

# -------------------------
# Helper GA functions
# -------------------------
def init_population(pop_size: int, num_tasks: int, num_vms: int, seed: Optional[int]=None) -> List[List[int]]:
    if seed is not None:
        random.seed(seed)
    return [[random.randrange(num_vms) for _ in range(num_tasks)] for _ in range(pop_size)]

def tournament_select(pop: List[List[int]], fitnesses: List[float], k: int = 3) -> List[int]:
    idxs = random.sample(range(len(pop)), k)
    best_idx = min(idxs, key=lambda i: fitnesses[i])
    return deepcopy(pop[best_idx])

def single_point_crossover(a: List[int], b: List[int]) -> Tuple[List[int], List[int]]:
    if len(a) != len(b):
        raise ValueError("Chromosome lengths differ")
    pt = random.randint(1, len(a)-1)
    return a[:pt] + b[pt:], b[:pt] + a[pt:]

def mutate(chrom: List[int], num_vms: int, pm: float) -> List[int]:
    # mutate in place (but caller should pass a copy if needed)
    for i in range(len(chrom)):
        if random.random() < pm:
            chrom[i] = random.randrange(num_vms)
    return chrom

def repair(chrom: List[int], tasks, vms) -> List[int]:
    """
    Simple capacity-aware repair:
    - compute CPU & mem loads per VM
    - for overloaded VMs move largest tasks to the first VM that fits
    This is a basic greedy repair; adapt to your capacity model.
    """
    num_vms = len(vms)
    # compute loads
    loads_cpu = [0.0] * num_vms
    loads_mem = [0.0] * num_vms
    for t_idx, vm_idx in enumerate(chrom):
        if 0 <= vm_idx < num_vms:
            loads_cpu[vm_idx] += tasks[t_idx].cpu
            loads_mem[vm_idx] += tasks[t_idx].mem

    changed = True
    while changed:
        changed = False
        for vm_i in range(num_vms):
            if loads_cpu[vm_i] > vms[vm_i].cpu_capacity or loads_mem[vm_i] > vms[vm_i].mem_capacity:
                # tasks assigned to vm_i
                assigned = [i for i, g in enumerate(chrom) if g == vm_i]
                # sort tasks by cpu descending (move largest first)
                assigned.sort(key=lambda i: tasks[i].cpu, reverse=True)
                moved = False
                for t_idx in assigned:
                    for target in range(num_vms):
                        if target == vm_i:
                            continue
                        if loads_cpu[target] + tasks[t_idx].cpu <= vms[target].cpu_capacity and \
                           loads_mem[target] + tasks[t_idx].mem <= vms[target].mem_capacity:
                            # move task
                            chrom[t_idx] = target
                            loads_cpu[vm_i] -= tasks[t_idx].cpu
                            loads_mem[vm_i] -= tasks[t_idx].mem
                            loads_cpu[target] += tasks[t_idx].cpu
                            loads_mem[target] += tasks[t_idx].mem
                            changed = True
                            moved = True
                            break
                    if moved:
                        break
                # if we couldn't move any task from this VM, leave as-is and rely on penalty in fitness
    return chrom

# -------------------------
# Main GA runner
# -------------------------
def run_ga(tasks, vms, hosts, pop_size: int =50, gen: int = 100,
           pc: float = 0.8, pm: float = 0.05, seed: Optional[int]=None,
           elitism_frac: float = 0.05):
    """
    Run a simple generational GA.
    Returns: (best_chromosome, best_fitness, best_info_dict_or_None)
    """
    num_tasks = len(tasks)
    num_vms = len(vms)
    pop = init_population(pop_size, num_tasks, num_vms, seed)
    best = None
    best_f = float('inf')
    best_info = None

    for g in range(gen):
        fitnesses = []
        infos = []
        # Evaluate population
        for chrom in pop:
            res = evaluate_solution(chrom, tasks, vms, hosts)
            if isinstance(res, (tuple, list)):
                f_val, info = res[0], res[1]
            else:
                f_val, info = res, None
            fitnesses.append(f_val)
            infos.append(info)
            if f_val < best_f:
                best_f = f_val
                best = deepcopy(chrom)
                best_info = info

        # Build new population with elitism
        new_pop = []
        elite_count = max(1, int(elitism_frac * pop_size))
        sorted_idx = np.argsort(fitnesses)  # ascending (minimization)
        for idx in sorted_idx[:elite_count]:
            new_pop.append(deepcopy(pop[idx]))

        # Generate offspring until population full
        while len(new_pop) < pop_size:
            p1 = tournament_select(pop, fitnesses)
            p2 = tournament_select(pop, fitnesses)
            if random.random() < pc:
                c1, c2 = single_point_crossover(p1, p2)
            else:
                c1, c2 = deepcopy(p1), deepcopy(p2)
            # mutate
            c1 = mutate(c1, num_vms, pm)
            c2 = mutate(c2, num_vms, pm)
            # repair to enforce capacities (best-effort)
            c1 = repair(c1, tasks, vms)
            c2 = repair(c2, tasks, vms)
            new_pop.append(c1)
            if len(new_pop) < pop_size:
                new_pop.append(c2)

        pop = new_pop

        # logging
        gen_best = min(fitnesses) if fitnesses else float('inf')
        print(f"Generation {g+1}/{gen} - gen_best_fitness = {gen_best:.6f}  global_best = {best_f:.6f}")

    return best, best_f, best_info
