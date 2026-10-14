import os
import yaml


def load_config(path="config/config.yaml"):
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def ensure_directory(path):
    os.makedirs(path, exist_ok=True)


def get_status(value, warning, critical):
    if value >= critical:
        return "CRITICAL"
    if value >= warning:
        return "WARNING"
    return "OK"


def overall_status(statuses):
    if "CRITICAL" in statuses:
        return "CRITICAL"
    if "WARNING" in statuses:
        return "WARNING"
    return "OK"
