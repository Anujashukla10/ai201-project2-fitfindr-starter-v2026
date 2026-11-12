"""
Structured logging for the Capstone instrumentation requirement.

Every stage of an agent run, and every full run, writes one JSON record
to logs/capstone.jsonl: a timestamp, what came in, what came out, and how
long it took. This is what What It Costs and the latency breakdown are
computed from — not estimated, measured.
"""
import json
import time
from pathlib import Path

LOG_PATH = Path(__file__).parent / "logs" / "capstone.jsonl"


def log_event(event: str, input_data, output_data, duration_s: float, **extra) -> None:
    LOG_PATH.parent.mkdir(exist_ok=True)
    record = {
        "timestamp": time.time(),
        "event": event,
        "input": input_data,
        "output": output_data,
        "duration_s": round(duration_s, 4),
    }
    record.update(extra)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, default=str) + "\n")