"""
Capstone improvement — latency trials run in their own process, isolated
from the rate-limit contention that the other 12 scenarios create when
run in the same batch.
"""
import time
import config
from agent import run_agent
from utils.data_loader import get_example_wardrobe

config.CACHE_ENABLED = False

QUERIES = [
    "silk slip dress in midi length under $40",
    "vintage graphic tee under $30",
    "denim jacket under $50",
]

wardrobe = get_example_wardrobe()
for i, q in enumerate(QUERIES, 1):
    t0 = time.monotonic()
    session = run_agent(q, wardrobe)
    dt = time.monotonic() - t0
    status = "error" if session.get("error") else "completed"
    verdict = "PASS" if dt < 8.0 else "FAIL"
    print(f"{i}. {dt:6.2f}s  {verdict}  {status}  {q}")