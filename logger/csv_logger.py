import argparse
import csv
import json
import time
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = PROJECT_ROOT / "test-data" / "telemetry_history.json"
DEFAULT_LOG_DIR = PROJECT_ROOT / "test-data" / "logs"
TELEMETRY_FIELDS = [
    "timestamp",
    "speed",
    "batteryVoltage",
    "batteryPercent",
    "current",
    "power",
    "motorTemp",
    "controllerTemp",
    "status",
]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Save telemetry JSON samples to a CSV log file."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help="Telemetry JSON file to read.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="CSV file to append. Defaults to test-data/logs/telemetry_<time>.csv.",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Polling interval in seconds.",
    )
    parser.add_argument(
        "--max-records",
        type=int,
        help="Stop after writing this many records. Useful for local checks.",
    )
    return parser.parse_args()


def build_output_path():
    run_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return DEFAULT_LOG_DIR / f"telemetry_{run_id}.csv"


def read_telemetry(source):
    with open(source, "r", encoding="utf-8") as file:
        data = json.load(file)

    records = data if isinstance(data, list) else [data]
    cleaned_records = []

    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Telemetry record must be a JSON object")

        missing_fields = [field for field in TELEMETRY_FIELDS if field not in record]
        if missing_fields:
            raise ValueError(
                f"Telemetry data is missing fields: {', '.join(missing_fields)}"
            )

        cleaned_records.append({field: record[field] for field in TELEMETRY_FIELDS})

    return cleaned_records


def append_record(output, record):
    output.parent.mkdir(parents=True, exist_ok=True)
    write_header = not output.exists() or output.stat().st_size == 0

    with open(output, "a", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=TELEMETRY_FIELDS)
        if write_header:
            writer.writeheader()
        writer.writerow(record)


def run_logger(source, output, interval, max_records):
    logged_timestamps = set()
    records_written = 0

    print(f"Logging telemetry from {source}")
    print(f"Writing CSV log to {output}")

    while True:
        try:
            record = read_telemetry(source)
        except FileNotFoundError:
            print(f"Waiting for telemetry file: {source}", flush=True)
        except (json.JSONDecodeError, ValueError) as error:
            print(f"Skipping invalid telemetry data: {error}", flush=True)
        else:
            for record in read_telemetry(source):
                timestamp = record["timestamp"]
                if timestamp in logged_timestamps:
                    continue

                append_record(output, record)
                logged_timestamps.add(timestamp)
                records_written += 1
                print(
                    f"logged {timestamp} speed={record['speed']} "
                    f"battery={record['batteryPercent']} status={record['status']}",
                    flush=True,
                )

                if max_records and records_written >= max_records:
                    return records_written

        time.sleep(interval)


def main():
    args = parse_args()
    source = args.source.resolve()
    output = (args.output or build_output_path()).resolve()
    return run_logger(source, output, args.interval, args.max_records)


if __name__ == "__main__":
    main()
