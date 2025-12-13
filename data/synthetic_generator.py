import csv
import random

def generate_synthetic_trace(filename, num_tasks=100, seed=42):
    random.seed(seed)
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['id', 'arrival', 'cpu', 'mem', 'length'])
        arrival = 0.0
        for i in range(1, num_tasks + 1):
            arrival += random.expovariate(1/10)  # average inter-arrival time = 10s
            cpu = random.choice([500, 750, 1000, 1200, 1500])
            mem = random.choice([512, 1024, 2048, 4096])
            length = random.randint(60, 600)  # 1 to 10 minutes
            writer.writerow([i, round(arrival, 2), cpu, mem, length])

if __name__ == "__main__":
    generate_synthetic_trace('sample_google_trace.csv', num_tasks=100)