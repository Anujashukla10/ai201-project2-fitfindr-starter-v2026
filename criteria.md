# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
<!-- Why 4 of 5 and not 5 of 5? Something about your search, probably —
     "my search is a plain keyword match and some phrasings will miss" is a
     real answer. -->

The search depends on the wording of the query, so some matching queries may still fail to find a result if the keywords do not match the listing data closely enough. After a result is found, the agent continues to suggest_outfit and create_fit_card, but these steps include model calls and can vary because TEMPERATURE is set to 0.9. Because of these possible variations, I think 4 out of 5 is a reasonable target instead of 5 out of 5.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
<!-- Why is 5 of 5 reasonable here when criterion 1 isn't? What's different
     about this path? -->

When search_listings returns no results, the agent has a direct code path that sets an error message and returns the session before reaching suggest_outfit. There is no model call or random choice needed to decide whether to continue, so the same behavior should happen every time. This makes 5 out of 5 a reasonable target.

---

## 3. Something about state

<!-- YOU WRITE THIS ONE.

     How would you know that the item your search found is the same item the
     next tool received? Name something countable or observable.

     This is the criterion people find hardest, because state failure doesn't
     look like state failure — it looks like a tool problem. Something that
     compares session["selected_item"] against what actually reached
     suggest_outfit is the shape you're after. -->

In 5 out of 5 matching query runs, the id of session["selected_item"] should be the same as the id of the item passed to suggest_outfit.

**Why this target:**
The agent sets session["selected_item"] directly from the first search result, and then passes that same item to suggest_outfit. There is no model call or random choice between these steps that could change the item, so I expect this to pass 5 out of 5 times.


---

## 4. Something about the fit card

<!-- YOU WRITE THIS ONE.

     The fit card calls a model, so the same input can produce different words
     each time. That's not a bug — it's the nature of the tool. So what would
     make it acceptable?

     Think about what you'd actually be unhappy to see. A caption that never
     mentions the price? Two different items producing the same opening
     sentence? A card longer than a caption anyone would post? Any of those can
     be turned into a number. -->

In 5 out of 5 runs, the fit card should mention the selected item's price and platform, and it should be 2 to 4 sentences long. The price counts as mentioned if it appears as a dollar formatted value such as $38.00 or $38.

**Why this target:**

The create_fit_card prompt tells the model to include the item's price and platform, so these are specific things the model is being asked to include. The wording can still change because TEMPERATURE is set to 0.9, but I expect the required information to stay in the response and since this is an explicit formatting instruction rather than open-ended content, I expect the model to follow it reliably even at a high temperature.

---

## 5. Your choice

<!-- YOU WRITE THIS ONE TOO.

     Pick something you actually care about getting right. Speed, the empty
     wardrobe path, what happens when the model can't be reached, whether the
     search respects a price ceiling — anything, as long as it names a number
     or an observable outcome. -->

When the wardrobe is empty, the agent should still give a non-empty outfit suggestion in 5 out of 5 runs.

**Why this target:**

The empty wardrobe case is handled by suggest_outfit with a prompt asking for general styling advice instead of using wardrobe items. This means the tool still has something to generate when the wardrobe is empty, so I expect it to return an outfit suggestion in all 5 runs.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
