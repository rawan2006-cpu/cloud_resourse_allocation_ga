# src/sim/entities.py
from dataclasses import dataclass, field
import math

@dataclass
class Task:
    id: int
    cpu: float  # MIPS needed
    mem: float  # MB
    length: float  # seconds or million instructions
    arrival: float

@dataclass
class VM:
    id: int
    cpu_capacity: float
    mem_capacity: float
    tasks: list = field(default_factory=list)

    @property
    def cpu_load(self):
        return sum(t.cpu for t in self.tasks)

    @property
    def mem_load(self):
        return sum(t.mem for t in self.tasks)

@dataclass
class Host:
    id: int
    cpu_capacity: float
    mem_capacity: float
    idle_power: float = 100.0
    max_power: float = 250.0
    vms: list = field(default_factory=list)

    def utilization(self):
        used = sum(vm.cpu_load for vm in self.vms)
        return min(1.0, used / self.cpu_capacity)

    def power(self):
        u = self.utilization()
        # linear model: P = idle + (max-idle)*u
        return self.idle_power + (self.max_power - self.idle_power) * u
