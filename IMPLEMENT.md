# IMPLEMENT: install walkthrough for Blacksmith

> This file is your script. `STATUS.md` is your memory: tick it as you go, not at the end, so a dead session resumes from it alone. A human can follow this file by hand instead of you; nothing here requires you specifically.

## What you are installing

Two things: a written standard for what an AI skill folder should contain, and a skill (`blacksmith`) that applies it. The skill has two doors. Door 1 takes an approved plan for a brand-new skill and drafts the folder from it. Door 2 takes a skill you already have, diffs it against the standard, and reports the gaps in two buckets: things that need your judgment, and things that are purely mechanical and get fixed behind a safety snapshot. Neither door decides what a skill *does*; that is yours. The standard only decides what shape the folder has, so a reader with no memory of your setup can still use it correctly.

## Phase 0: environment scan

Say this, in your own words, before reading anything: "To install this well I want to look at how your skills are set up and read your standing-instructions file, if you have one. Nothing gets changed yet. OK to look?" Wait for yes.

Once you have it, fill in this table (also copy it into `STATUS.md`):

| Check | What you're finding out |
|---|---|
| Platform and capabilities | Can you read and write files? Run a shell? Is Python 3.9 or later on the machine? Can you spin up a sub-agent with no memory of this chat? |
| Operating system | macOS, Linux or Windows: Windows changes the link recipe below |
| How the platform discovers skills | Does it auto-load a directory of skill folders? Read a rules file that points at them? Nothing automatic at all? |
| The directory it reads | The actual path, if there is one |
| Where the user's work lives | A folder, a vault, a repo: this is the **workspace** (defined below) |
| The standing-instructions file | Its path, and whether the platform actually reads it at the start of every session, or whether it is just a file the user opens by habit |
| Skills that already exist | How many, and their names |
| An existing skills index | A README, table, or list of the user's skills, if one exists |
| An installed build protocol | Something like Rome, or a homemade process, that hands over an approved plan the user signed off on |
| Git | Do the user's skills sit inside a git repo? |

No shell and no file access at all (chat-only)? Skip straight to asking the user each row in plain language, and keep this table as a note you paste back into future sessions.

## Phase 1: decisions

Three terms used above, defined once:

**Skills home**: the folder your AI actually reads skills from, whatever the platform calls it.
```
~/tools/ai-skills/            <- skills home
  blacksmith/
  weekly-review/
```

**Workspace**: the folder, vault, or repo where the user's own notes and projects live; not the same folder as the skills home unless the platform forces it.
```
~/Documents/MyNotes/          <- workspace
  Projects/
  Journal/
```

**Standing-instructions file**: the file your AI reads at the start of every session, before the user says anything.
```
CLAUDE.md, AGENTS.md, or a rules file     <- read automatically
a chat app's project instructions field   <- pasted by the user
```

Present these six, one at a time, in plain language. Record every answer in `STATUS.md`'s decisions table the moment it's made.

### DP-1: Where do skills live, and how does your AI find them?

**Options:**
- **A. In the platform's auto-loaded skills directory**, one folder per skill. *Trade-off:* simplest, but the skill's files live apart from everything else you keep.
- **B. In the workspace, linked into the platform's skills directory**: a symlink on macOS and Linux, a directory junction on Windows. *Trade-off:* the skill sits beside the notes it reads, and one backup covers both, but you now maintain a link.
- **C. In the workspace, referenced from the standing-instructions file**, with no auto-discovery. *Trade-off:* works anywhere, but nothing finds the skill on its own: the instructions file has to name it every time.

**Recommendation:** the platform auto-discovers skills and you keep no searched-and-backed-up workspace → A. It auto-discovers and you do have a workspace you search and back up → B (skills sit beside the notes they read; the cost is a link to maintain). No auto-discovery at all → C, in the folder where the user's skills already sit; only when they have none, at `<workspace>/_tools/skills/`. "Whatever you recommend": A if the scan found a skills directory, otherwise C.

**Downstream:** `blacksmith.json`'s `skills_home` value; whether `standard.md` § 8 keeps or drops its link recipe; check 8 (discovery). Record your choice in `STATUS.md`.

### DP-2: What hands Blacksmith a new skill to shape?

**Options:**
- **A. Your build protocol** (Rome, or your own): its build step hands the plan straight to Blacksmith. *Trade-off:* nothing extra to fill in, but only works once that protocol is actually installed.
- **B. The plan card**, `templates/plan-card.md`, filled and approved by the user. *Trade-off:* one page to fill by hand each time, with no protocol required.

**Recommendation:** the scan found an installed build protocol with a plan the user approves → A. Otherwise → B. A user on B who installs a protocol later switches over just by adding the one wiring line from Phase 2 step 8. "Whatever you recommend": follow the scan.

**Downstream:** Phase 2's wiring step (A adds one line to the protocol's build step; under B nothing is installed: the plan card already rides inside the skill at `templates/plan-card.md`). `skill/SKILL.md` is written to accept either card with no edit needed.

### DP-3: How much feedback loop do skills get?

**Options:**
- **A. The full loop**: a close line on every top-level skill, depth chosen per skill (usually 1 for a small skill, 3 for a skill with certain flags set, otherwise 2). *Trade-off:* most useful over time, needs the user to actually answer the close line.
- **B. A flat loop**: every skill at depth 1, one row logged each run. *Trade-off:* lighter, less insight into repeated mistakes.
- **C. No loop**: no close line at all; a run just ends by naming what it produced. *Trade-off:* simplest, but skills never improve from their own runs.

**Recommendation:** anyone who will run their skills more than a handful of times → A (skills improve from real runs, not from theory written up front). A user who says outright they won't read a log of runs → B. C only if the user asks for it by name. "Whatever you recommend": A. If the user has said neither, ask this, word for word: "After a skill runs, will you answer a one-line question about how it went?" Yes → A. No → B.

**Downstream:** `blacksmith.json`'s `close_line` value; check 5 (skipped entirely under C); `standard.md` §§ 1.5 and 7; the last line of every skill's own `SKILL.md` (removed under C).

### DP-4: Who does the cold read?

Two more terms, defined here:

**Cold read**: someone or something with zero memory of this conversation follows a skill using only its own files, to see if a stranger could actually use it.
```
Fresh session. Given only: the SKILL.md path, one prompt.
It must find and use the skill unaided.
If it can't, that's the test doing its job.
```

**Fixture**: a short file naming only the paths a cold read needs, never the content itself.
```
SKILL.md: <skills home>/blacksmith/SKILL.md
Prompt:   "bring my weekly-review skill up to standard"
```

**Options:**
- **A. A fresh sub-agent with zero context.** *Trade-off:* best test, needs a platform that supports sub-agents.
- **B. A second model or tool called from the shell.** *Trade-off:* still automated, needs something else callable on the machine.
- **C. The user opens a new chat and pastes the fixture.** *Trade-off:* works anywhere, but takes a manual step every time.

**Recommendation:** the platform has sub-agents → A. No sub-agents but a second tool on the machine → B. Otherwise → C. "Whatever you recommend": follow the scan, in that order.

**Downstream:** one sentence in `skill/SKILL.md`'s "The check" section, swapped for B or C.

### DP-5: How does the mechanical check run?

**Options:**
- **A. `python3 scripts/check.py`**: Python 3.9 or later, standard library only. *Trade-off:* fast and repeatable, needs Python.
- **B. By hand**, from `references/check-by-hand.md`: the same ten checks as a checklist. *Trade-off:* works with nothing installed, slower, and the snapshot becomes a folder copy you make yourself.

**Recommendation:** a shell and Python 3.9+ are present, or the user has a shell they can paste into → A. Otherwise → B. "Whatever you recommend": follow the scan.

**Downstream:** none beyond what's already written: `skill/SKILL.md` already names both forms at door 1 step 7 and door 2 steps 2, 6 and 7.

### DP-6: Where is the list of your skills kept?

**Options:**
- **A. An index you already have**: a README or table of skills. *Trade-off:* nothing new to maintain, only works if it already exists.
- **B. `templates/skills-index.md`**, installed fresh. *Trade-off:* one more file, worth it once you have several skills.
- **C. None**: the folder listing is the list. *Trade-off:* simplest, stops making sense once you have several skills.

**Recommendation:** the scan found an index → A. No index and five or more skills → B. Fewer than five → C, revisit once you hit five. "Whatever you recommend": follow the scan.

**Downstream:** `blacksmith.json`'s `registry` value (a path under A and B, `null` under C); check 9 (skipped under C); `skill/SKILL.md` door 1 step 5.

## Phase 2: install

1. Copy `skill/` to the DP-1 location, renamed `blacksmith/`.

2. Edit `scripts/blacksmith.json`. Shipped default:
   ```json
   {
     "skills_home": null,
     "workspace_root": null,
     "close_line": "Done. Feedback loop: 1, 2, 3, or later? (usual: N)",
     "registry": null
   }
   ```
   Set `skills_home` and `workspace_root` for DP-1:
   - **A:** `"skills_home": "<path to the auto-loaded skills directory>"`, `"workspace_root": null`
   - **B:** `"skills_home": "<path to the auto-loaded skills directory>"`, `"workspace_root": "<path to the workspace>"` (the real files live in the workspace; the link inside the skills directory is what your AI actually opens)
   - **C:** `"skills_home": "<the folder the user's skills already sit in, or <workspace>/_tools/skills when there is none>"`, `"workspace_root": "<path to the workspace>"`

   Set `close_line` for DP-3:
   - **A and B:** leave the shipped line exactly as it is. The literal `N` stays in the file; each skill's own draft resolves it to 1, 2 or 3 when that skill is written.
   - **C:** `"close_line": null`

   Set `registry` for DP-6:
   - **A:** `"registry": "<path to the existing index>"`
   - **B:** `"registry": "<the path step 5 copies skills-index.md to>"`
   - **C:** `"registry": null` (leave as shipped)

3. Confirm the two templates arrived with the skill: `<blacksmith install path>/templates/fixture.md` and `<blacksmith install path>/templates/plan-card.md`. Nothing to copy; they ship inside `skill/`.

4. Named edits, each one find this sentence, replace with that sentence. Make only the edits your decisions call for, and list each one made in `STATUS.md`. When no branch below matches your decisions, no edit is made: write "none" and move on.
   - **DP-1, option A or C** (nothing is linked). In `references/standard.md` § 8, find the bullet that begins "The link recipe, in this order" and replace the whole bullet with: "No link is needed in this install: the skill folders already sit where the AI reads them (install record)."
   - **DP-3, option B** (every skill at depth 1). In `references/standard.md` § 1.5, find "N is 1 for a leaf, 3 when F1 or F5 is set, otherwise 2, and the user may change it." and replace it with "N is 1 for every skill in this install, and the user may change it." In `SKILL.md` door 1 step 4, find "N is 1 for a leaf, 3 when F1 or F5 is set, otherwise 2; the user changes it later." and replace it with "N is 1; the user changes it later." In the last line of `SKILL.md`, change `(usual: 3)` to `(usual: 1)`.
   - **DP-3, option C** (no loop). In `SKILL.md`, delete everything from the heading "## Close line" to the end of the file, and in door 2 step 8 replace "what is still open, then the close line below." with "and what is still open." In `references/standard.md` § 1.5, replace the bullet that begins "Checkable form:" with: "Checkable form: the last section names what was produced, by path. This install runs no feedback loop, so no close line is printed (install record)."
   - **DP-4, option B** (a second tool does the cold read). In `SKILL.md` section "The check", find "a fresh agent with zero context follows SKILL.md from the fixture's paths on one real prompt, and the transcript is the evidence." and replace it with "a second tool, called read-only from the shell, follows SKILL.md from the fixture's paths on one real prompt, and its transcript is the evidence." Then delete the sentence two sentences later that begins "No sub-agents:"; the new sentence already says it.
   - **DP-4, option C** (the user does the cold read). Same sentence, replaced with "the user opens a new chat and pastes the fixture, that chat follows SKILL.md on one real prompt, and the transcript the user pastes back is the evidence." Then delete the sentence that begins "No sub-agents:", as under option B.
   - **No sub-agents at all** (the scan said so, whatever DP-4 chose). In `SKILL.md`, find "Mode: **orchestrator**. Drafts by a sub-agent at high effort with the brief on disk; cold reads by a fresh agent with zero context;" and replace it with "Mode: **one thread**. You draft from the brief on disk, then re-read your own draft as a stranger would; the cold read runs as the check section says;"

5. Under DP-6 option B: copy `templates/skills-index.md` into the workspace, and add one row for `blacksmith` itself (the row already in the shipped template; replace its path with the real install path). Under DP-6 option A: ask the user before touching their index, then add the same row there in their format.

6. Run the self-test, then the check on blacksmith itself:
   ```
   python3 scripts/check.py --selftest
   python3 scripts/check.py blacksmith
   ```
   Run them from inside the installed `blacksmith` folder. On Windows the command may be `python` or `py -3` instead of `python3`. Both must print PASS; the second one reads the registry you set in step 2, so it fails until step 5's row is in. Under DP-5 option B, walk `references/check-by-hand.md` against the newly installed `blacksmith` folder instead, and confirm each of the ten checks by hand.

7. Wire the standing-instructions file. Add this line, adapted to name the actual install path:

   > Building or fixing a skill folder → the `blacksmith` skill at `<blacksmith install path>/SKILL.md`: shapes a new skill from an approved plan, or checks an existing one against the standard and fixes what's mechanical behind a snapshot.

   If the platform does not actually auto-read that file (a chat app with only a project-level instructions field, for instance), the line goes there instead, and you tell the user plainly: on this platform, every new chat has to name the file itself for the wiring to fire.

8. Under DP-2 option A only: add one line to the build protocol's own build step, naming `blacksmith` as the tool it hands a locked plan to for skill-shaped work.

9. Record every path written or edited so far: the install path, `blacksmith.json`'s final contents, the templates copied, the standing-instructions edit, the build-protocol edit if any: in `STATUS.md`'s install-paths table.

**If DP-1 is option B (linked into the skills directory):**

macOS and Linux:
```
ls -l "<skills home>"                                  # confirm the directory first
ln -sfn "<workspace>/blacksmith" "<skills home>/blacksmith"
ls -lL "<skills home>/blacksmith"                       # confirm the link resolves
```

Windows (Command Prompt, run as the same user who owns both folders):
```
mklink /J "<skills home>\blacksmith" "<workspace>\blacksmith"
dir "<skills home>\blacksmith"
```

## Phase 3: first live run

Order this so the user sees a real result before anything optional. Ask which of their own skills to run door 2 on first: the one the user says misbehaves, or else the smallest one that fails the check (run the check on each to find out). A skill that already passes teaches nothing on a first run. No skills yet at all? Run door 1 instead, on the plan card, against one small real thing the user already does every week (not a made-up example).

**Door 2, on a real skill:**
1. Snapshot the skill folder: `python3 scripts/check.py --snapshot [name]` from inside the `blacksmith` folder, or a folder copy by hand under DP-5 B. Show the user the restore command it prints.
2. Run the mechanical check on it; note the result.
3. Diff it against the standard; write the two-bucket report: Needs you, then Mechanical.
4. The user rules on the Needs-you items; the Mechanical items apply regardless.
5. Apply what's approved, behind the snapshot from step 1.
6. Re-run the check; paste the result.
7. Show the restore command again, so the user knows undoing this is one line.

**Door 1, on the plan card:**
Fill the card together on one small, real, weekly thing, the plan and the build's paper folder included. Draft the folder from it. Home it per DP-1. Run the check. Then run the cold read per DP-4 and close, as door 1 step 8 says for a plan card.

**Verification tests.** Each one only counts if you also state the input that would make it fail:
- (a) The check passes on the newly installed `blacksmith` skill, and fails when pointed at the kit's `example/dirty-skill`: if it passes on the dirty example too, the check isn't actually checking anything.
- (b) In a fresh session, the user says something like "bring my [skill] up to standard" without naming `blacksmith` at all, and it fires anyway: if it doesn't fire, the wiring line from Phase 2 step 7 didn't take. You cannot open a fresh session for the user on any tier: hand them the sentence to say, mark this test `[~]` (deferred) in `STATUS.md`, and tick it when they report back that it fired.
- (c) The cold read from DP-4 runs on the skill just touched, using the fixture, and a reader with no memory of this session can actually follow it: if the reader gets stuck or guesses, that step of the skill needs a rewrite, not a stronger prompt. Door 2 does not write a fixture on its own, so write one first: copy `templates/fixture.md` from the installed `blacksmith` folder to the build's paper folder (default: `builds/[skill name]/tests/` in the workspace), fill every field with paths and one real prompt, and run the check with `--fixture` to confirm it passes check 10. Passing check 10 only shows the fixture is well formed; the cold read itself is the test.

On any install where you cannot start a fresh reader yourself (no sub-agents, whatever else you have), tests (b) and (c) are the user's to run, and you never stand in for the fresh reader: you wrote the edits, so your read cannot fail. Mark both `[~]` in `STATUS.md`, say so, and tick them when the user reports back. On a chat-only install with no shell, test (a) is theirs too, from `references/check-by-hand.md`. For test (c), hand the user this to paste into a second, fresh chat:

> I'm testing a skill called blacksmith. Here's its file: [paste the skill's `SKILL.md`]. Here's the fixture: [paste the filled `templates/fixture.md`]. Follow it and tell me what you'd do, using only what's here.

## Phase 4: wrap

Walk the user through what's installed and where, reading straight from `STATUS.md`'s tables. Before offering to delete the kit, copy the scan table and the decisions table into `<blacksmith install path>/references/install-record.md`: this is the only record of which options were chosen, and it has to survive the kit's own deletion.

Leave the user with one habit, not a list: after any skill finishes a run, answer its close line. That single habit is what makes the feedback loop real instead of theoretical.

## If things go wrong

- **A capability the scan expected isn't actually there:** take the next option down in that decision point's list; every DP names its fallback, so there's always a next option.
- **The user's existing naming clashes with the kit's:** keep the user's own names and map the *jobs* onto them; never force a rename just to match this file.
- **The same step fails twice in a row:** stop, don't try a third variation. Write it in `STATUS.md`'s Blockers section, take the fallback named for that step if one exists, and tell the user plainly what didn't work.
