# A worked example: door 2 on one skill

This walks one small skill through door 2 (checking an existing skill against the standard): what
the check finds, what the report looks like, what the guard does, and what "fixed" looks like.
Every command and output block below is real, copied from an actual run of the files in this kit.

## The skill before (`example/dirty-skill/SKILL.md`)

```
---
name: dirty-skill
description: Turns a meal plan into a shopping list.
---
# Grocery List

1. Read the meal plan from wherever it was pasted, pull out every ingredient, check the pantry inventory in `references/pantry.md`, group the remaining items by grocery aisle, and format the final list as a checklist.
2. Never buy more than a week of perishables. Note a substitute for anything out of season.

## Notes
- Never buy more than a week of perishables: it just goes bad in the fridge before the next trip.

Done. Feedback loop: 1, 2 or later? (usual: 2)
```

## Running the check

```
$ python3 skill/scripts/check.py example/dirty-skill
PASS  1 name: name 'dirty-skill' is bare kebab-case (path target: name not compared)  [SKILL.md:2]
FAIL  2 description: no trigger phrases: say when it fires ("Use when …") (plain)
PASS  3 size: SKILL.md is 13 lines
FAIL  4 paths: 1 missing of 1 checked: SKILL.md:7 `references/pantry.md`  [SKILL.md:7]
FAIL  5 close line: near-miss: expected `Done. Feedback loop: 1, 2, 3, or later? (usual: N)`, found `Done. Feedback loop: 1, 2 or later? (usual: 2)`  [SKILL.md:13]
PASS  6 placeholders: no [NEEDS CLARIFICATION in the folder
PASS  7 feedback-loop files: runs.md / lessons.md not pre-created
SKIP  8 discovery: path target: no discovery check
SKIP  9 registry: path target: a copy is not registered by design
FAIL dirty-skill: 3 failures
```

## What Blacksmith would report

**Needs you.**
- Situation: the description never says when the skill fires. Recommendation: rewrite it, e.g.
  "Use when a meal plan needs to become a shopping list." Why: wording is a judgment call.
- Situation: step 1 is one paragraph doing five things, with no line saying what each produces.
  Recommendation: split it into numbered steps, each with a "produces" line. Why: reshaping the
  spine changes what the skill does, not just its shape.
- Situation: "never buy more than a week of perishables" appears twice, with no source for either
  copy. Recommendation: keep one copy, in a rules block, with who set it or what it cost. Why:
  which copy to keep is a judgment call.

- Situation: step 1 reads `references/pantry.md`, which does not exist, and no other file is its
  replacement. Recommendation: create the pantry note. Why: a dead path with no verified
  replacement is never fixed unasked.

**Mechanical** (runs without a ruling, behind the guard):
- The close line is a near-miss: replaced with the exact line, as the last line.

## The guard, run for real (on a temporary copy)

The dirty skill was copied into a temporary skills home as `demo-skill`, beside an installed
`blacksmith` folder. `<temp>` stands for that temporary folder.

```
$ python3 blacksmith/scripts/check.py --snapshot demo-skill
snapshot: <temp>/skills/blacksmith/history/snapshots/demo-skill-20260927-103133
restore command: python3 "<temp>/skills/blacksmith/scripts/check.py" --restore demo-skill 20260927-103133
```

A line was appended to the copy's `SKILL.md` to stand in for a bad edit, then the restore ran:

```
$ python3 blacksmith/scripts/check.py --restore demo-skill 20260927-103133
restored <temp>/skills/demo-skill from <temp>/skills/blacksmith/history/snapshots/demo-skill-20260927-103133
```

A file-by-file comparison with the original found no difference.

## The skill after (`example/clean-skill/SKILL.md`)

```
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
```

The dead path became a real file; the doubled rule became one rule with a source; the step
paragraph became three steps, each naming what it produces; a mode line, a time budget and a "no state" line
were added (no flag is set, so this is a leaf and its usual depth is 1); and the close line is now the exact line, last.

## Running the check again

```
$ python3 skill/scripts/check.py example/clean-skill
PASS  1 name: name 'clean-skill' is bare kebab-case (path target: name not compared)  [SKILL.md:2]
PASS  2 description: 131 chars (plain)
PASS  3 size: SKILL.md is 22 lines
PASS  4 paths: 1 path-shaped tokens resolve (no workspace root set: only skill-relative and absolute paths checked)
PASS  5 close line: exact, last line  [SKILL.md:22]
PASS  6 placeholders: no [NEEDS CLARIFICATION in the folder
PASS  7 feedback-loop files: runs.md / lessons.md not pre-created
SKIP  8 discovery: path target: no discovery check
SKIP  9 registry: path target: a copy is not registered by design
PASS clean-skill
```

Checks 8 and 9 stay SKIP here because this run passed a folder path, not a bare name: door 2 on
a skill already in your skills home passes the bare name, and those two turn into PASS or FAIL.
