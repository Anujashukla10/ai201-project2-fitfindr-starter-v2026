"""
Runs each capstone scenario and writes a run log in the required format:
5 criteria, 3 trials each. Mirrors run_eval.py's shape but adds timing
per trial for the latency criterion.
"""
import datetime as dt
import time
import config
import capstone_scenarios

config.CACHE_ENABLED = False  # three trials have to be three real runs


def run_once(scenario):
    from agent import run_agent
    from utils.data_loader import get_example_wardrobe, get_empty_wardrobe

    wardrobe = get_empty_wardrobe() if scenario["wardrobe"] == "empty" else get_example_wardrobe()
    t0 = time.monotonic()
    session = run_agent(scenario["query"], wardrobe)
    duration = time.monotonic() - t0
    return {"session": session, "duration": duration}


def main():
    rows = []
    for scenario in capstone_scenarios.SCENARIOS:
        print(f"\n{scenario['name']}  (criterion {scenario['criterion']})")
        print(f"  query: {scenario['query']}")
        record = run_once(scenario)
        s = record["session"]
        status = (
            "needs_clarification" if s.get("needs_clarification")
            else "error" if s.get("error")
            else "completed"
        )
        print(f"  status: {status}  duration: {record['duration']:.2f}s")
        if s.get("clarifying_question"):
            print(f"  question: {s['clarifying_question']}")
        if s.get("fit_card"):
            print(f"  fit_card: {s['fit_card'][:100]}...")
        rows.append({"scenario": scenario, "record": record, "status": status})

    config.RESULTS_DIR.mkdir(exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M")
    path = config.RESULTS_DIR / f"capstone_run_{stamp}.md"
    lines = ["# Capstone run log", ""]
    for row in rows:
        s = row["scenario"]
        r = row["record"]
        lines += [
            f"### {s['name']} (criterion {s['criterion']})",
            f"- query: `{s['query']}`",
            f"- status: {row['status']}",
            f"- duration: {r['duration']:.2f}s",
        ]
        sess = r["session"]
        if sess.get("clarifying_question"):
            lines.append(f"- clarifying_question: {sess['clarifying_question']}")
        if sess.get("fit_card"):
            lines.append(f"- fit_card: {sess['fit_card']}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWrote {path}")


if __name__ == "__main__":
    main()