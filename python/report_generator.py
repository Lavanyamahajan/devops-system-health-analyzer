import json
import os
import sys
from datetime import datetime

import psutil
from jinja2 import Environment, FileSystemLoader

from log_analyzer import analyze_log
from utils import load_config, get_status, overall_status, ensure_directory


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)

    config = load_config()
    thresholds = config["thresholds"]

    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent

    metrics = {
        "cpu": {"value": cpu, "status": get_status(
            cpu, thresholds["cpu_warning"], thresholds["cpu_critical"])},
        "memory": {"value": memory, "status": get_status(
            memory, thresholds["memory_warning"], thresholds["memory_critical"])},
        "disk": {"value": disk, "status": get_status(
            disk, thresholds["disk_warning"], thresholds["disk_critical"])},
    }

    app_log = analyze_log(config["log_analyzer"]["application_log"])
    system_log = analyze_log(config["log_analyzer"]["system_log"])

    statuses = [item["status"] for item in metrics.values()]
    statuses.extend([app_log["status"], system_log["status"]])
    status = overall_status(statuses)

    report = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "hostname": os.uname().nodename,
        "status": status,
        "metrics": metrics,
        "application_log": app_log,
        "system_log": system_log,
    }

    output_dir = config["report"]["output_dir"]
    ensure_directory(output_dir)

    with open(os.path.join(output_dir, "report.json"), "w",
              encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("health_report.html.j2")
    with open(os.path.join(output_dir, "report.html"), "w",
              encoding="utf-8") as file:
        file.write(template.render(report=report))

    with open(os.path.join(output_dir, "report.txt"), "w",
              encoding="utf-8") as file:
        file.write(f"System Health Report\nStatus: {status}\n")
        file.write(f"Generated: {report['generated_at']}\n")
        for name, metric in metrics.items():
            file.write(f"{name.upper()}: {metric['value']}% "
                       f"({metric['status']})\n")
        file.write(f"Application log status: {app_log['status']}\n")
        file.write(f"System log status: {system_log['status']}\n")

    print(f"Report generated. Overall status: {status}")
    print(f"Reports saved in: {output_dir}/")


if __name__ == "__main__":
    main()
