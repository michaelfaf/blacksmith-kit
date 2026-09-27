---
name: clean-skill
description: Use when a meal plan needs to become a shopping list; triggers on "make my grocery list" or "shopping list from this week's meals".
---
# Grocery List

Mode: one thread, one pass. Reads one pasted meal plan, produces one shopping list. Out of scope: prices, store choice, ordering.

**Time budget: 2 minutes typical, 10 max.** One file plus the pantry note; never a tracker, a script or a new folder to support it.

1. Read the meal plan as pasted into the chat. Produces: a plain list of every ingredient it names.
2. Check the pantry note at `references/pantry.md` now. Produces: the ingredient list minus anything already on hand.
3. Group what is left by grocery aisle and format it as a checklist. Produces: the final shopping list, one item per line.

## Rules
- Never buy more than a week of perishables: they spoil before the next trip (user, 2026-09-20).

No state persists between runs; each list starts fresh from the pasted meal plan.

What the answer to the line below means: the standard, section 7.

Done. Feedback loop: 1, 2, 3, or later? (usual: 1)
