# src/sim/cluster.py
from .entities import Host, VM, Task
import copy

class Cluster:
    def __init__(self, hosts: list, vms: list):
        self.hosts = hosts
        self.vms = vms

    def reset(self):
        for vm in self.vms:
            vm.tasks = []
        for h in self.hosts:
            h.vms = []

    def assign_vm_to_host(self, vm_id, host_id):
        vm = self.vms[vm_id]
        host = self.hosts[host_id]
        host.vms.append(vm)

    def assign_task_to_vm(self, task, vm_id):
        vm = self.vms[vm_id]
        vm.tasks.append(task)

    def total_energy(self):
        return sum(h.power() for h in self.hosts)

    def makespan(self):
        # naive: max sum of lengths per VM
        max_time = 0.0
        for vm in self.vms:
            s = sum(t.length for t in vm.tasks)
            max_time = max(max_time, s)
        return max_time
