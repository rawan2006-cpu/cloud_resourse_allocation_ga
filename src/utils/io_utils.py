# src/utils/io_utils.py

import os
import csv
import json


def ensure_dir(path):
    """Create directory if it does not exist."""
    os.makedirs(path, exist_ok=True)


def load_tasks_from_csv(path, TaskClass):
    """
    Load tasks from CSV file.
    CSV must contain: cpu, mem, length, arrival
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"CSV file not found: {path}")

    tasks = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            tasks.append(
                TaskClass(
                    id=i,
                    cpu=float(row.get("cpu", 100)),
                    mem=float(row.get("mem", 128)),
                    length=float(row.get("length", 1000)),
                    arrival=float(row.get("arrival", 0)),
                )
            )
    return tasks


def save_json(path, data):
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def append_csv(path, fieldnames, row):
    ensure_dir(os.path.dirname(path))
    write_header = not os.path.exists(path)

    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow(row)
