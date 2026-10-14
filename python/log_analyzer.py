import re
from collections import Counter
from pathlib import Path
from datetime import datetime


LOG_PATTERN = re.compile(
    r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) "
    r"(INFO|WARNING|ERROR|CRITICAL) (.*)$"
)


def analyze_log(path):
    result = {
        "total": 0,
        "levels": {"INFO": 0, "WARNING": 0, "ERROR": 0, "CRITICAL": 0},
        "malformed": 0,
        "top_error": None,
        "first_timestamp": None,
        "last_timestamp": None,
        "status": "OK",
    }
    errors = Counter()
    timestamps = []

    if not Path(path).is_file():
        result["status"] = "CRITICAL"
        result["error"] = f"Log file not found: {path}"
        return result

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.rstrip("\n")
            match = LOG_PATTERN.match(line)

            if not match:
                result["malformed"] += 1
                continue

            timestamp, level, message = match.groups()
            result["total"] += 1
            result["levels"][level] += 1
            timestamps.append(timestamp)

            if level in ("ERROR", "CRITICAL"):
                errors[message] += 1

    if timestamps:
        result["first_timestamp"] = min(timestamps)
        result["last_timestamp"] = max(timestamps)

    if errors:
        result["top_error"] = errors.most_common(1)[0][0]

    if result["levels"]["CRITICAL"]:
        result["status"] = "CRITICAL"
    elif result["levels"]["ERROR"] or result["levels"]["WARNING"]:
        result["status"] = "WARNING"

    return result
