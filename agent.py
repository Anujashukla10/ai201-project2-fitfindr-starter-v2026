"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""

import re

import config
import trace
from tools import suggest_outfit, create_fit_card
from mcp_client import call_tool
from generate import ModelUnavailable


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "price_comparison": None,    # STRETCH — what compare_price returned, if it ran
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


# ── query parsing ──────────────────────────────────────────────────────────────

def _parse_query(query: str) -> dict:
    """
    Pull a description, a size, and a max_price out of a plain-language query.

    Regex-based: a $NN or $NN.NN pattern for max_price, a "size X" pattern for
    size, with both stripped out of what's left to form the description.
    """
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


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.

    Args:
        query:    what the user asked for, in plain language
                  (e.g. "vintage graphic tee under $30, size M").
        wardrobe: a wardrobe dict — get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py.

    Returns:
        The session dict. **Check session["error"] first** — if it isn't None,
        the run ended early and the later fields will still be None.

    ─────────────────────────────────────────────────────────────────────────
    TODO — build this, following the branch rule you wrote in Milestone 2.

      1. Start a session with new_session().

      2. Count the times round the loop, and call trace.check_iterations(count)
         on each one before you go again. It raises when the count passes
         MAX_ITERATIONS in config.py — see trace.py.

      3. Parse the query into a description, a size, and a max_price. Regex,
         string splitting, or asking the model are all fine — say which you
         chose in your README. Put the result in session["parsed"].

      4. Call search_listings() with what you parsed.
         Put the results in session["search_results"].

         ⚠️ THIS IS THE BRANCH. If nothing came back:
              - put a message in session["error"] saying what the user could
                change — "No results" is not that message
              - return the session
              - do NOT call suggest_outfit with nothing

      5. Choose an item — the first result is fine. Put it in
         session["selected_item"].

      6. Call suggest_outfit() with the selected item and the wardrobe.
         Put the result in session["outfit_suggestion"].

      7. Call create_fit_card() with the outfit and the item.
         Put the result in session["fit_card"].

      8. Return the session.

    ─────────────────────────────────────────────────────────────────────────
    IN UNIT 4 you come back and add two things:

      • Trace calls. One per step. `trace.step("search_listings", inputs=...,
        returned=...)` — see trace.py. Your README needs the output.

      • A handler for ModelUnavailable, so a bad key produces a message rather
        than a stack trace. The import is already at the top of this file.

    ─────────────────────────────────────────────────────────────────────────
    STRETCH — second branch (this unit, optional, for extra credit):

      After selecting an item, if three or more results came back, call the
      new compare_price() tool and store its verdict in
      session["price_comparison"]. With fewer than three results there isn't
      enough in the category to compare against, so the loop skips that call
      entirely rather than running it on nothing — same shape as the
      empty-search branch, just a different condition.
    """
    session = new_session(query, wardrobe)
    iterations = 0

    iterations += 1
    trace.check_iterations(iterations)
    parsed = _parse_query(query)
    session["parsed"] = parsed
    trace.step("parse_query", inputs={"query": query}, returned=parsed)

    try:
        iterations += 1
        trace.check_iterations(iterations)
        results = call_tool("search_listings", parsed)
        session["search_results"] = results
        trace.step("search_listings (via MCP)", inputs=parsed, returned=results)

        # ⚠️ THIS IS THE BRANCH. If nothing came back:
        #      - put a message in session["error"] saying what the user could
        #        change — "No results" is not that message
        #      - return the session
        #      - do NOT call suggest_outfit with nothing
        if not results:
            session["error"] = (
                "No listings matched. Try raising the price ceiling, "
                "loosening the size, or using different keywords."
            )
            trace.step(
                "branch",
                note="search_results empty — stopping before suggest_outfit",
            )
            return session

        session["selected_item"] = results[0]

        # STRETCH — second branch: only compare prices when there's enough in
        # the category to compare against. Fewer than three results means
        # compare_price would have nothing meaningful to average, so the loop
        # takes the other path instead of calling it on an empty comparison set.
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
        else:
            trace.step(
                "branch",
                note=f"only {len(results)} result(s) — skipping compare_price",
            )

        iterations += 1
        trace.check_iterations(iterations)
        outfit = suggest_outfit(session["selected_item"], wardrobe)
        session["outfit_suggestion"] = outfit
        trace.step(
            "suggest_outfit",
            inputs=f"item_id={session['selected_item']['id']}, item_title={session['selected_item']['title']}",
            returned=outfit,
        )

        iterations += 1
        trace.check_iterations(iterations)
        fit_card = create_fit_card(outfit, session["selected_item"])
        session["fit_card"] = fit_card
        trace.step("create_fit_card", inputs={"outfit": outfit}, returned=fit_card)

    except ModelUnavailable as exc:
        session["error"] = f"Couldn't reach the model: {exc}"
        trace.step("error", note=str(exc))

    return session


# ── running it directly ────────────────────────────────────────────