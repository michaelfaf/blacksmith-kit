---
name: blacksmith
description: Applies the skill standard to a skill folder, shaping a new skill from an approved plan or bringing one that already exists up to the standard. Use when the user says "blacksmith", "apply the standard to [skill]", "retrofit [skill]", "bring [skill] up to standard", "check [skill] against the standard", "structure this as a skill", or when the build protocol reaches its build step and what ships is a skill. Not for building, researching, or changing what a skill does: those stay with the build protocol and the feedback loop.
---

# Blacksmith

Blacksmith is where a skill gets its shape. Door 1: your build protocol hands over a run card, or the user hands you a filled plan card, and Blacksmith turns the locked goal and plan into a skill folder that passes the check. Door 2: an existing skill is diffed against the standard, the user rules on anything judgment-shaped, and the mechanical fixes land behind a snapshot. It never builds, researches, or changes what a skill does.

Mode: **orchestrator**. Drafts by a sub-agent at high effort with the brief on disk; cold reads by a fresh agent with zero context; drafts and cold reads on the most capable model you have, high effort.

The standard lives at `references/standard.md`: the five things every skill has, the six flags, rule form, frontmatter, the folder table, what the feedback loop needs, registration. This file points at it and does not restate it.

State: **history/snapshots/** inside this folder, one folder per snapshot, is Blacksmith's own state slot (standard § 5). A snapshot holds the whole skill folder except that skill's own top-level history folder and its git and cache folders, and a restore leaves those alone.

**Which door.** A card in hand → door 1. A skill that already exists, named → door 2. Neither → door 1 step 0, which stops.

## Door 1: from a card

0. **The card is the call.** A card is either your build protocol's run card (the tier with the one-line test that picked it, every file the run will create or touch by path, the file and section the checks read) or a filled `templates/plan-card.md` with the user's approval line on it. No card → say "fill the plan card first, or build it through your build protocol" and stop. Produces: the card read back in one line, or the stop.
1. **Read what the card settled** from the files it names: the locked goal, the done list, the plan, the test set. Re-ask nothing. Produces: nothing new; the plan is the spec.
2. **Read `references/standard.md` now**, the whole file, every run. Produces: nothing; it is the ruler the next steps measure with.
3. **Answer the six flags** yes or no from the plan (standard § 2) and print the six answers in one line; no flag set means the leaf rule applies. A yes adds that flag's block; a sub-item the standard marks conditional is written only when its condition holds, never as an empty slot. Produces: the flag line, which decides which blocks SKILL.md carries.
4. **Draft the folder.** One sub-agent, high effort, its brief on disk in the build's own prompts folder, paths in the brief, never pasted contents. It writes SKILL.md per standard §§ 1, 3, 4 plus the flag blocks from step 3, and the references the plan names as pointers to outside sources, never copies. Description: one clause of what, then the user's trigger phrases in their words, never the steps, then the parity check that every phrase the user gave is in it. The close line's `(usual: N)`: N is 1 for a leaf, 3 when F1 or F5 is set, otherwise 2; the user changes it later. Produces: SKILL.md and the named references.
5. **Home it.** Create the folder in the skills home (the folder the AI reads skills from). Then, only when skills are kept in the workspace and linked into the folder the platform reads, the link, its own ask (the recipe in standard § 8), and any edit to a standing-instructions file, also its own ask. The registry row (when `registry` is set in `scripts/blacksmith.json`) is do-and-report: write it and say so. If the skill replaces an existing prompt or document, its body becomes one pointer line, `Retired YYYY-MM-DD → now the [name] skill.`, and the file stays. Produces: the folder in place, the link's verify output, the registry row.
6. **Write the fixture** using `templates/fixture.md`, to the build's own tests folder: paths only, the SKILL.md path, one real prompt from the test set, the references and scripts paths, the outside files the skill reads. Never a reference's contents; an inlined reference makes the cold read unable to fail. Produces: the fixture file.
7. **Run the check:** `python3 scripts/check.py <name>` (or the folder path plus `--fixture <the fixture>` while the folder has no link yet, a scratch copy, checks 8 and 9 then skip), or by hand from `references/check-by-hand.md`. A path the card says this build creates must exist before the check; create it at step 5. Fix until PASS. The same line failing twice → stop, name the residual defect, ship it named. Produces: the check's PASS line, or the named defect.
8. **Hand back, or close.** Called by a build protocol: hand back the file list by path, the use-case lines ("use X when Z", in the user's terms) and the fixture path; the protocol runs the cold read at its own check step and prints its own close line, and Blacksmith prints none. From a plan card, with no protocol: run the cold read yourself as the check section says, then close as door 2 step 8 does. Produces: the hand-back message, or the cold-read transcript and the close.

## Door 2: a skill that already exists

0. **Name the target** in one line ("Blacksmith on **[name]**, door 2."). Read the whole folder first, SKILL.md and every file under references/ and scripts/, never edit from memory or from the description alone. Produces: the target line and the file list read.
1. **Read `references/standard.md` now**, the whole file, every run. Produces: nothing; it is the ruler.
2. **Run the check** (door 1 step 7's command, either form) on the target: the bare name for a live skill; the folder path for a copy, checks 8 and 9 then skip, so run the bare name too, read-only, for the link and registry answers. Produces: both outputs, kept for the report.
3. **Diff the folder** against the five things (standard § 1), the six flags (§ 2) and the leaf rule. Ask by name: does this skill carry its own self-improvement loop, retro block, or lessons file outside the feedback loop's shape? If yes, that is a Needs-you item, never applied. Produces: the list of deltas, each tagged Needs-you or Mechanical. Also list every file the skill names in plain text: the check only sees a path written in backticks or as a link, so a plain-text path is a Needs-you item (write it in backticks, then it is checked).
4. **One report, two buckets, in this order.** Needs you first, each item as Situation · Recommendation · Why: every judgment call, every competing loop, every rule with no known source, any consolidation of two rules into one, any step-order or pointer change. Then Mechanical, exactly: close line added or made exact · a dead path replaced by a verified one · the registry row written · the "none yet" line written into an existing empty lessons file · a placeholder marker flagged, reported, never resolved. Everything else is Needs you. The close line is added as the last line of SKILL.md; a copy of it mid-file becomes a pointer to the last line. A dead path is one the check FAILs on, replaced by the verified full path; a dead path with no replacement is Needs you. Produces: the report, in chat.
5. **The user rules**, one message, numbered items, they reply with the numbers. Mechanical items run without a ruling; their reply is the ask for the rest. Produces: the ruled list.
6. **Apply behind the guard:** `python3 scripts/check.py --snapshot <name>` (copies the folder to `history/snapshots/<name>-<YYYYMMDD-HHMMSS>/` inside the blacksmith folder and prints the restore command), or by hand, a folder copy to `history/snapshots/<name>-<date>/` inside the blacksmith folder. Keep the printed stamp. Apply the Mechanical set plus what the user approved, as deltas to one identified line each (on an old skill that can add up to most of the file; the report already listed every change), then re-run the plain check and paste the PASS line and the restore command (`python3 scripts/check.py --restore <name> <stamp>`). On FAIL: run the restore command, say so, and the item goes back to Needs you. A registry row, when one is owed, is written last, after the re-check passes, so a restore never has to undo it. Produces: the PASS line, the restore command, and the applied deltas by file and line.
7. **Re-run the check** on the target; paste the result. A second FAIL on the same line → name the residual defect and ship it named. Produces: the re-check output.
8. **Close:** what changed by file and line, what is still open, then the close line below.

## The check

The mechanical half is the ten checks: 1 name, 2 description, 3 size, 4 paths, 5 close line, 6 placeholders, 7 feedback-loop files, 8 discovery, 9 registry, 10 fixture, run by `scripts/check.py <name>` or by hand from `references/check-by-hand.md`. The second half is the cold read: a fresh agent with zero context follows SKILL.md from the fixture's paths on one real prompt, and the transcript is the evidence. Your build protocol runs it at its own check step for door 1; door 2 runs it only on a proposed step-order or pointer change, on a copy, never the live skill, and writes the fixture first from `templates/fixture.md`, in the build's own tests folder. No sub-agents: a second tool called from the shell does the cold read, or the user opens a new chat and pastes the fixture. A check that fails twice on the same line is a named defect, not a third round of guessing.

## Hard rules

- Builds nothing without a card; say "fill the plan card first, or build it through your build protocol" and stop (cost: building without a locked card re-opened decisions the plan had already settled).
- Never re-asks what the card settled; goal, done list, plan, test set are read, not re-opened (cost: re-asking a settled question got a different answer than the locked plan, and the build drifted from it).
- Never edits a skill without reading the whole folder first; never edits from memory (cost: an edit made from memory or from the description alone missed what the folder actually said).
- Nothing judgment-shaped is applied without the user's ruling; the Mechanical set is the whole list of what runs unasked (cost: a judgment call applied without asking had to be reversed after the fact, costing more than the ask would have).
- Never creates **references/runs.md** or **references/lessons.md**; those are the feedback loop's to create on its first run (standard § 7).
- Drafts and cold reads on the most capable model you have, high effort (cost: a draft or cold read run on a weaker model missed defects a stronger model caught immediately).
- Every path full and resolvable in every file it writes; never a path one folder short (standard § 7).
- Called from a build protocol, Blacksmith prints no close line; run on its own (door 2, or door 1 from a plan card) it does (standard § 7).
- Never deletes what a skill replaces; one pointer line in the old file, the file stays (standard § 8).
- A link, a hook, or a standing-instructions file: each its own ask, every time; the registry row is the one do-and-report exception (standard § 8).
- Door 2 edits go behind the snapshot; no PASS line pasted, nothing was applied (standard § 7).
- Never changes what a skill does; behavior belongs to the build protocol and the feedback loop (cost: a skill-shaping tool that also changed behavior blurred building and improving into one unreviewable step).

## Close line

The line above this one points at `references/standard.md` § 7. Door 1 called by a build protocol ends at step 8 by handing back and prints no close line.

Done. Feedback loop: 1, 2, 3, or later? (usual: 3)
