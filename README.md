# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->



---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->


### `search_listings`

- **What it does:** Searches the 40 listings for items matching keywords in the description, an optional size, and an optional max price, returning the best matches first.
- **Inputs:** `description` (str), `size` (str or None), `max_price` (float or None)
- **Returns:** A list of listing dicts, best match first (keyword-overlap score), each with: `id, title, description, category, style_tags, size, condition, price, colors, brand, platform`. Capped at `config.SEARCH_RESULT_LIMIT`.
- **When it has nothing:** Returns `[]` — an empty list, never `None`, never raises.

### `suggest_outfit`

- **What it does:** Given a thrifted item and the user's wardrobe, asks the model for outfit combinations using pieces the user already owns.
- **Inputs:** `new_item` (dict, a listing), `wardrobe` (dict with an `items` key)
- **Returns:** A non-empty string of outfit suggestions.
- **When it has nothing:** If `wardrobe["items"]` is empty, returns general styling advice instead of outfit combinations — never an empty string, never raises.

### `create_fit_card`

- **What it does:** Writes a 2-4 sentence social-caption-style blurb for the item and outfit.
- **Inputs:** `outfit` (str), `new_item` (dict, a listing)
- **Returns:** A short caption string mentioning the item, price, and platform once each.
- **When it has nothing:** If `outfit` is empty/whitespace, returns a descriptive fallback message instead of raising or returning `""`.

### `search_listings`

- **What it does:**
- **Inputs:** <!-- name and type each: `max_price` (float), not "a price" -->
- **Returns:**
- **When it has nothing:**

### `suggest_outfit`

- **What it does:**
- **Inputs:**
- **Returns:**
- **When it has nothing:**

### `create_fit_card`

- **What it does:**
- **Inputs:**
- **Returns:**
- **When it has nothing:**

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, put a message in `session["error"]` naming what the user could change, and stop. Otherwise, take the first result as `session["selected_item"]` and continue to `suggest_outfit`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regex — a `$NN` or `$NN.NN` pattern for `max_price`, a `size <token>` pattern for `size`, with both substrings stripped out of the remainder to form `description`.

**What moves through the session:** `parsed` → `search_results` → `selected_item` → `outfit_suggestion` → `fit_card`, each read back out of `session` before being passed to the next tool.

**Branch rule:**

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** <!-- regex, string splitting, or asking the model — say which -->

**What moves through the session:** <!-- which fields, in what order -->

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'

Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

Outfit:   Here are two specific outfit combinations using the new Y2K Butterfly Baby Tee and pieces from your existing wardrobe:

Outfit 1: Streetwear Contrast
- Top: Y2K Butterfly Baby Tee
- Bottoms: Baggy straight-leg jeans (dark wash)
- Footwear: Chunky white sneakers
- Outerwear: Black cropped zip hoodie
- Accessories: Black crossbody bag

Outfit 2: Sweet & Grunge
- Top: Y2K Butterfly Baby Tee
- Bottoms: Wide-leg khaki trousers
- Footwear: Black combat boots
- Outerwear: Vintage black denim jacket
- Accessories: Brown leather belt

Fit card: Just scored the ultimate Y2K butterfly baby tee on Depop for only
$18! Obsessed with how easy it is to style—already planning to wear it with
baggy denim and sneakers, or grunge it up with some combat boots. Secondhand
wins forever. 🦋✨
```

**The empty-search branch, for comparison**

```
$ python app.py ask 'designer ballgown size XXS under $5'

No listings matched. Try raising the price ceiling, loosening the size, or
using different keywords.
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('vintage graphic tee', max_price=30))"

Returned 10 results, best matches first — e.g. lst_002 "Y2K Baby Tee —
Butterfly Print" ($18.00), lst_006 "Graphic Tee — 2003 Tour Bootleg Style"
($24.00), lst_033 "Vintage Band Tee — Faded Grey" ($19.00). All results
are $30 or under, matching the price ceiling.
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"

Here are two specific outfit ideas using the vintage Levi's 501 jeans and pieces from your existing wardrobe:

Outfit 1: Effortless Minimal Streetwear
- Vintage Levi's 501 Jeans (Medium Wash)
- White ribbed tank top
- Brown leather belt
- Chunky white sneakers
- Black crossbody bag
- Optional layering: Oversized grey crewneck sweatshirt

Outfit 2: Grunge-Infused Denim on Denim
- Vintage Levi's 501 Jeans (Medium Wash)
- Black cropped zip hoodie
- Vintage black denim jacket (layered over the hoodie)
- Black combat boots
- Black crossbody bag
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"

Nothing beats the fit of broken-in denim. Snagged these vintage Levi's 501s
on Depop for just $38, and I'm officially obsessed. Can't wait to style
them with my favorite white sneakers for the ultimate effortless weekend fit.
```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:*
- *What came back:*
- *What I changed:*

**Moment 2**

- *What I asked for:*
- *What came back:*
- *What I changed:*

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
