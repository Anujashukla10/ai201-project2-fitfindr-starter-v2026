"""
The FitFindr planning loop — now with a Capstone extension.

Capstone extension: if a query gives the agent nothing to search on (no
size, no price ceiling, and barely any descriptive keywords), the agent
asks a clarifying question instead of running a search likely to return
noise or nothing.
"""

import re
import time

import config
import trace
import generate
import capstone_log
from tools import suggest_outfit, create_fit_card, _tokenize
from mcp_client import call_tool
from generate import ModelUnavailable


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    return {
        "query": query,
        "parsed": {},
        "search_results": [],
        "selected_item": None,
        "wardrobe": wardrobe,
        "price_comparison": None,
        "dropped_constraint": None,
        "needs_clarification": False,
        "clarifying_question": None,
        "outfit_suggestion": None,
        "fit_card": None,
        "error": None,
    }


def _parse_query(query: str) -> dict:
    max_price = None
    price_match = re.search(r"\$(\d+(?:\.\d{1,2})?)", query)
    if price_match:
        max_price = float(price_match.group(1))

    size = None
    size_match = re.search(r"size\s+([A-Za-z0-9/]+)", query, re.I)
    if size_match:
        size = size_match.group(1)

    description = re.sub(r"\$\d+(?:\.\d{1,2})?", "", query)
    description = re.sub(r"size\s+[A-Za-z0-9/]+", "", description, flags=re.I)
    description = re.sub(r"\s+", " ", description).strip()

    return {"description": description, "size": size, "max_price": max_price}


def _is_too_vague(parsed: dict) -> bool:
    """
    CAPSTONE EXTENSION.

    A query is too vague to search meaningfully if it gives no price
    ceiling, no size, and a description with at most one meaningful
    keyword token (stopwords excluded). "something cute and cheap" has
    zero usable tokens after stripping stopwords; "denim jacket" has two
    and is fine even with nothing else specified.
    """
    if parsed.get("max_price") is not None:
        return False
    if parsed.get("size"):
        return False
    tokens = _tokenize(parsed.get("description", ""))
    return len(tokens) <= 1


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    session = new_session(query, wardrobe)
    iterations = 0
    run_start = time.monotonic()
    calls_before = generate.call_count()
    tokens_before = generate.token_counts()

    try:
        stage_start = time.monotonic()
        iterations += 1
        trace.check_iterations(iterations)
        parsed = _parse_query(query)
        session["parsed"] = parsed
        trace.step("parse_query", inputs={"query": query}, returned=parsed)
        capstone_log.log_event("parse_query", query, parsed, time.monotonic() - stage_start)

        # ── CAPSTONE BRANCH: too vague to search ──
        stage_start = time.monotonic()
        if _is_too_vague(parsed):
            question = (
                "That's pretty open-ended — can you give me a size, a "
                "price ceiling, or a more specific kind of item (e.g. "
                "'denim jacket' instead of 'something cute')?"
            )
            session["needs_clarification"] = True
            session["clarifying_question"] = question
            session["error"] = question
            trace.step(
                "branch",
                note="query too vague — asking a clarifying question instead of searching",
            )
            capstone_log.log_event(
                "vagueness_check", parsed, question, time.monotonic() - stage_start,
                status="needs_clarification",
            )
            return session
        capstone_log.log_event(
            "vagueness_check", parsed, "query specific enough — proceeding",
            time.monotonic() - stage_start, status="ok",
        )

        stage_start = time.monotonic()
        iterations += 1
        trace.check_iterations(iterations)
        results = call_tool("search_listings", parsed)
        session["search_results"] = results
        trace.step("search_listings (via MCP)", inputs=parsed, returned=results)
        capstone_log.log_event("search_listings", parsed, {"count": len(results)}, time.monotonic() - stage_start)

        if not results and parsed.get("size"):
            stage_start = time.monotonic()
            retry_parsed = {**parsed, "size": None}
            trace.step(
                "branch",
                note=f"empty with size={parsed['size']!r} — retrying without size filter",
            )
            results = call_tool("search_listings", retry_parsed)
            session["search_results"] = results
            trace.step(
                "search_listings (via MCP, retry)",
                inputs=retry_parsed,
                returned=results,
            )
            capstone_log.log_event(
                "search_listings_retry", retry_parsed, {"count": len(results)},
                time.monotonic() - stage_start,
            )
            if results:
                session["dropped_constraint"] = (
                    f"size '{parsed['size']}' (no exact match — showing all sizes)"
                )

        if not results:
            session["error"] = (
                "No listings matched, even after loosening the size filter. "
                "Try raising the price ceiling or using different keywords."
            )
            trace.step(
                "branch",
                note="still empty after retry — stopping before suggest_outfit",
            )
            return session

        session["selected_item"] = results[0]

        stage_start = time.monotonic()
        iterations += 1
        trace.check_iterations(iterations)
        if len(results) >= 3:
            comparison = call_tool("compare_price", {
                "item_id": session["selected_item"]["id"],
                "listing_ids": [r["id"] for r in results],
            })
            session["price_comparison"] = comparison
            trace.step(
                "compare_price (via MCP)",
                inputs={"result_count": len(results)},
                returned=comparison,
            )
            capstone_log.log_event(
                "compare_price", {"result_count": len(results)}, comparison,
                time.monotonic() - stage_start,
            )
        else:
            trace.step(
                "branch",
                note=f"only {len(results)} result(s) — skipping compare_price",
            )

        stage_start = time.monotonic()
        iterations += 1
        trace.check_iterations(iterations)
        outfit = suggest_outfit(session["selected_item"], wardrobe)
        session["outfit_suggestion"] = outfit
        trace.step(
            "suggest_outfit",
            inputs=f"item_id={session['selected_item']['id']}, item_title={session['selected_item']['title']}",
            returned=outfit,
        )
        capstone_log.log_event(
            "suggest_outfit", {"item_id": session["selected_item"]["id"]},
            outfit[:200], time.monotonic() - stage_start,
        )

        stage_start = time.monotonic()
        iterations += 1
        trace.check_iterations(iterations)
        fit_card = create_fit_card(outfit, session["selected_item"])
        session["fit_card"] = fit_card
        trace.step("create_fit_card", inputs={"outfit": outfit}, returned=fit_card)
        capstone_log.log_event("create_fit_card", {"outfit_len": len(outfit)}, fit_card, time.monotonic() - stage_start)

    except ModelUnavailable as exc:
        session["error"] = f"Couldn't reach the model: {exc}"
        trace.step("error", note=str(exc))

    finally:
        total_duration = time.monotonic() - run_start
        calls_after = generate.call_count()
        tokens_after = generate.token_counts()
        status = (
            "needs_clarification" if session.get("needs_clarification")
            else "error" if session.get("error")
            else "completed"
        )
        capstone_log.log_event(
            "run",
            {"query": query},
            {
                "status": status,
                "selected_item": (session.get("selected_item") or {}).get("title"),
                "error": session.get("error"),
            },
            total_duration,
            model_calls=calls_after - calls_before,
            prompt_tokens=tokens_after["prompt"] - tokens_before["prompt"],
            output_tokens=tokens_after["output"] - tokens_before["output"],
        )

    return session


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session.get("needs_clarification"):
        print(f"  clarifying question: {session['clarifying_question']}")
        return
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    if session.get("dropped_constraint"):
        print(f"  note:     dropped {session['dropped_constraint']}")
    if session.get("price_comparison"):
        print(f"  price:    {session['price_comparison']}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query that's too vague ===")
    _show(run_agent(
        query="something cute and cheap",
        wardrobe=get_example_wardrobe(),
    ))