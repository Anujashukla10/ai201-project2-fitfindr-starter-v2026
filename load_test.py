"""
CAPSTONE STRETCH — load observation.
Runs 10 queries back-to-back with no delay between them, to see what
changes under burst load (latency, rate-limit waits, errors).
"""
import time
from agent import run_agent
from utils.data_loader import get_example_wardrobe

QUERIES = [
    "vintage graphic tee under $30",
    "90s track jacket in size M",
    "denim jacket under $50",
    "leather belt",
    "oversized cardigan under $40",
] * 2  # 10 total

wardrobe = get_example_wardrobe()
start = time.monotonic()
for i, q in enumerate(QUERIES, 1):
    t0 = time.monotonic()
    session = run_agent(q, wardrobe)
    dt = time.monotonic() - t0
    status = "error" if session.get("error") else "ok"
    print(f"{i:2d}. {dt:6.2f}s  {status:6s}  {q}")
print(f"\nTotal: {time.monotonic() - start:.2f}s for {len(QUERIES)} runs")