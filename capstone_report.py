"""
Summarize logs/capstone.jsonl: per-stage latency, per-run token cost, and
error/status counts. Used for What It Costs and the latency breakdown.
"""
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean

LOG_PATH = Path(__file__).parent / "logs" / "capstone.jsonl"


def load_records():
    if not LOG_PATH.exists():
        return []
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main():
    records = load_records()
    if not records:
        print("No log records found yet — run the agent first.")
        return

    by_event = defaultdict(list)
    for r in records:
        by_event[r["event"]].append(r)

    print(f"Total log records: {len(records)}\n")
    print("--- Per-stage latency (measured) ---")
    for event, rows in by_event.items():
        durations = [r["duration_s"] for r in rows]
        print(f"[{event:<20}]  n={len(rows):<3}  "
              f"avg={mean(durations):.3f}s  min={min(durations):.3f}s  max={max(durations):.3f}s")

    run_rows = by_event.get("run", [])
    if run_rows:
        print("\n--- Per-run cost (measured) ---")
        total_prompt = sum(r.get("prompt_tokens", 0) for r in run_rows)
        total_output = sum(r.get("output_tokens", 0) for r in run_rows)
        total_calls = sum(r.get("model_calls", 0) for r in run_rows)
        n = len(run_rows)
        print(f"Across {n} full agent runs:")
        print(f"  avg model calls/run:   {total_calls / n:.2f}")
        print(f"  avg prompt tokens/run: {total_prompt / n:.1f}")
        print(f"  avg output tokens/run: {total_output / n:.1f}")
        print(f"  avg total tokens/run:  {(total_prompt + total_output) / n:.1f}")

        statuses = defaultdict(int)
        for r in run_rows:
            statuses[r["output"].get("status", "?")] += 1
        print(f"\n  status breakdown: {dict(statuses)}")


if __name__ == "__main__":
    main()