# The skill standard

## 0. What this is
- Read by your AI every time a skill is built, or an existing skill is checked against it; the user reads it rarely, so it is written for a cold AI reader, not for the user's eyes.
- Why it exists: a skill organized this way is one the AI understands cold, and one the feedback loop can improve run over run; standardizing has no value beyond that.
- A house opinion derived from one operator's fleet of 33 skills, not an industry standard; no outside standard exists to borrow, and the most-installed "skill template" found in the wild is six blank lines (census).
- Provenance tags used below: `(census)` a finding from the originator's 33-skill fleet · `(cost: ...)` a specific failure that set the rule, stated generically · `(Anthropic docs)` the platform's own skills documentation, https://code.claude.com/docs/en/skills.md · `(superpowers writing-skills)` the public superpowers plugin's writing-skills skill · `(standard § N)` this file, another section.

## 1. The five things every skill has
Present wherever a skill reads well cold, absent wherever it fights the agent; every cold-read failure in the census maps to one of these five (census).

**1.1 A scope or mode line before step 1**: what a run is, which mode this is (orchestrator with helper agents, thought partner on one thread, or a sub-skill another skill calls), and what is out of scope (census).
- Checkable form: one line between the title and the first numbered step that starts "Mode:", "Scope", or names the run types; a text search on the lines above step 1 finds it, or it is missing (census).
- Example: "Mode: **orchestrator**. This chat plans, holds the gates and verifies files; sub-agents do research, writing and checks. Model and effort per your model-routing file."
- Missing → the skill starts at step 1 with no scope stated, and it is also the skill most likely to carry a broken step spine and a rule that contradicts its own reference file (census).

**1.2 A numbered spine** where every step names what it reads and what it produces (census).
- Checkable form: each step carries a "read `<full path>`" at the step that needs it, never every file up front, and a "produces" line; a cold reader can point at both in every step (census; Anthropic docs).
- Example: "Read references/process.md **now**" at the step that needs it, not before.
- Missing → a paragraph carrying several obligations, executed only in part by an agent that skims it (census).

**1.3 One rules block, one rule per line, each carrying who set it or what it cost** (census).
- Checkable form: one heading (`## Hard rules` or `## Standing rules`), one rule per line, each line ending in a provenance tag; a rule with no source is a defect the check flags (census; § 3 below).
- Example: "**Never click Send, Confirm, or Pay.** Ever." followed by "Pay only from the pre-funded balance, never a slow rail: a late payment is the failure this rule exists to prevent (cost: a payment landed late because a slow rail was used)."
- Missing → the rule gets restated in more than one place and the copies drift apart; one skill in the census carried 219 lines with no attribution at all, and "a rule with no reason is a rule the next agent 'improves'" (census).

**1.4 State named by path, with one authoritative marker** (census).
- Checkable form: every file the skill reads or writes between runs is named by full path, and one line says which marker proves an item is done, never "the folder is empty" or "the chat said so" (census). A leaf skill with no state between runs names none and creates none: the leaf rule in § 2 wins.
- Example: "State tracking (authoritative = the item's own ID, not folder presence): an item is processed only if its ID is found in the output index; the index is the source of truth."
- Missing → the agent re-derives state from the chat and loses it the moment the chat is compacted (census).

**1.5 One ending that says what was produced and hands off** (census).
- Checkable form: the last section names what was produced, by path, and the final line is the close line, exact: `Done. Feedback loop: 1, 2, 3, or later? (usual: N)`. N is 1 for a leaf, 3 when F1 or F5 is set, otherwise 2, and the user may change it. The line above the close line points at this standard's § 7, so the AI in the chat knows what the user's bare "1", "2", "3" or "later" means.
- Missing → the skill grows its own ending, and it starts to contradict the feedback loop; in the census, only 4 of 33 skills printed the close line exactly (census).

## 2. The six flags, and the block each "yes" adds
The five things above are the whole frame; everything else varies by capability, and a skill can trip several flags (census). Answer each yes or no when building or checking; a "yes" adds the named block, a "no" adds nothing (census).

**F1 · Does the skill dispatch sub-agents** (helper AIs it hands work to)? Yes →
- A model plus effort line per task, or a ladder when tasks differ (census).
- The brief on disk, never only in chat (census).
- Read each checker's own output, never a relay (census).
- The model rule stated in the mode line, pointing at wherever the model choice is decided (census).

**F2 · Does state live outside the skill folder?** Yes →
- The state files named by full path, and which one is authoritative (census).
- The check an agent runs before touching an item, to prove processed-state (census).
- A claim protocol (who may write, how a writer takes its turn) when two writers can collide (census).
- A hand-off template for the next chat (census).

**F3 · Does the skill take an irreversible or costly action**: money, a send, a write to a system of record, a publish? Yes →
- The rules block sits **above** the spine, so the "never" lines are read first; the ordering is the safety mechanism (census).
- An explicit approval gate before the act (census).
- Negative-knowledge records: what was tried, why it failed, the condition for retrying, each with an expiry ("verified <date>, do not retry without new evidence") (cost: a fix already ruled out was retried without checking why it had failed, and it failed again the same way).
- A ledger of every act, inside the skill or the state slot (census).
- These decisions stay at the loop's lowest, draft-and-wait rung forever (census).

**F4 · Is the user in the loop throughout**: turn by turn for the whole run, a ritual or a thought partner, not a one-shot request that ends in one deliverable? Yes →
- Gate phrasing that varies, never a robotic "ready to move on?" every time (census).
- Absorb-the-mess rules: input arrives raw and the skill sorts it, never asks the user to (census).
- An elastic depth path (a quick pass and a full pass) (census).
- Output shaped for how it will be consumed (for example flowing prose for a text-to-speech reader, no tables or bullets) (census).
- Expect thin feedback-loop signal: a run that is all discussion produces no correction, and discussion is not a correction (census).

**F5 · Does it ship something to someone outside the operation?** Yes →
- A sanitize gate (strip private names, numbers, profile facts) with a grep proof pasted into the run (census).
- A cold test by a zero-context agent that starts from the published thing, not the working copy (census).
- A run floor ("it ran"), not a score gate (census).
- A per-recipient forbidden-phrase list (census).

**F6 · Does it run unattended or on a schedule?** Yes →
- A "How it runs" block: the runner, the schedule, and how you know it broke (census).
- The close line printed at the end of every run, so the feedback loop has a row even when nobody watched (census).
- Never an always-on local process that needs the user's machine awake; a scheduled catch-up job instead (cost: an always-on process needed the machine kept awake to keep running, and it broke silently the first time the machine slept).

**The leaf rule: no flag set.** A leaf skill gets an anti-growth line and a time budget, and is forbidden the scaffolding above: no sub-agent block, no state files, no tracker, no script "to support" it (census).
- Example: "**Time budget: 5 minutes typical, 20 max.** Past 20, ship what you have." "One file. Never a tracker, dashboard, script, or new folder to 'support' this: that's the anxiety pattern; shrink the step instead." (census)

## 3. How to write a rule
- Classify the failure before writing the line; the form that fixes one kind of failure measurably backfires on another (superpowers writing-skills).
- A discipline failure (the agent knew the rule and broke it under pressure) gets a prohibition: "Never click Send, Confirm, or Pay." (superpowers writing-skills).
- An output-shape failure (the agent complied but the output was bloated, buried, or the wrong shape) gets a recipe stating what the output *is*, its parts in order, never a "don't" list; in head-to-head tests a prohibition produced more of the unwanted output than no rule at all (superpowers writing-skills).
- A missing required element gets a named slot in the template, not a reminder (superpowers writing-skills).
- Conditional behavior is keyed to something observable ("when the recipient is outside the operation"), never to a judgment ("when it matters") (superpowers writing-skills).
- No nuance clauses ("don't X unless it matters") and no exemption clauses ("this limit doesn't apply to code blocks"): both reopen the negotiation (superpowers writing-skills).
- A rule that would not have changed the run is not written; a line earns its place only if the run would have gone differently without it (superpowers writing-skills).
- One rule, one home: a rule stated twice drifts; the second mention is a pointer to the first (census).
- Every rule ends with its source: a date and who set it, a file and line, a research finding, or the cost that set it; an unattributed rule is the one the next agent "improves" (census).
- Write for an AI reading cold: plain English, no term the reader has to look up without its definition in the same sentence.

## 4. Frontmatter (the block between the two `---` lines at the top of SKILL.md)
- `name` equals the skill's name in the skills home (the shortcut your platform resolves to the folder): bare kebab-case, 1 to 64 characters, no "claude" or "anthropic" in it (Anthropic docs).
- `description`: one clause of what the skill does, then the trigger phrases in the user's own words, then what it is not when a neighbor skill could catch the same phrase; never the steps: an agent that reads a workflow summary in the description follows it and skips the body (superpowers writing-skills).
- Third person; the trigger part reads "Use when…"; slightly pushy, since the platform under-triggers skills left to guess (cost: a description written passively was skipped over by the model even on a matching prompt).
- Length 1,024 characters hard limit, aim about 500; the skill list has a character budget across all installed skills, and the least-used descriptions drop first when it overflows (Anthropic docs).
- No angle brackets anywhere in the description; a literal placeholder is a real fail, not a placeholder (cost: a literal angle-bracket placeholder shipped in a description and read as broken syntax instead of a fill-in-the-blank).
- Parity: every trigger phrase the user gave appears in the description, in their words; a phrase they would say that is missing is a skill that will not fire (cost: a trigger phrase the user actually used was left out of the description, and the skill never fired on it).
- Optional keys worth knowing, all platform-documented: `when_to_use` (appended to the description) · `model` · `effort` (`low` through `max`) · `disable-model-invocation: true` (never auto-loaded) · `argument-hint` · `context: fork` plus `agent` (run in an isolated helper) (Anthropic docs).
- Size: SKILL.md 500 lines hard limit, about 150 target; a reference file about 120 lines: this file is the one exception, no word cap (Anthropic docs).
- Fleet finding: SKILL.md ran 10 to 433 lines across the census, median 121: the target is reachable (census).

## 5. The folder
| What | When to use it | Rule | Source |
|---|---|---|---|
| **SKILL.md** | Always | The direction: frontmatter, title, mode line, spine, rules block, ending. | (census) |
| **references/** | Knowledge the skill needs that the model lacks | One topic per file; pointers to outside sources, never copies: a copy drifts from its source; the spine names the file at the step that reads it. | (Anthropic docs) |
| **scripts/** | Only when the output must be identical every run (a calculation, a file generator, an API call) | State the runtime; resolve paths from the skill's own root, never from the skill's depth in the tree: a hard-coded number of parent hops breaks on any move. | (cost: a path resolver broke on the first folder move because it counted parent folders instead of walking up to a marker file) |
| **assets/** | Static files handed over unchanged | The skill never edits them. | (census) |
| **templates/** | Starter files the skill fills in | Skill-local only; the name can collide with a workspace-level templates folder outside the skill. | (census) |
| The state slot | Anything the skill must remember between runs | A **history/** folder inside the skill, or files in the project the skill serves; either way named by full path in SKILL.md: the build's own history lives in the build's own folder in the workspace, never inside the skill. | (census) |
| **references/runs.md** + **references/lessons.md** | The feedback loop's, not the builder's | The loop creates them on its first run, the only files it may create in a skill it did not build; an empty lessons file carries a "none yet" line so "none yet" can be told from "not maintained". | (standard § 7) |

What never lives in a skill folder: test prompts (the build's own tests folder) · design docs · generated data · backups · a README: SKILL.md is the README-equivalent (census).

## 6. Where things live
- Direction → `SKILL.md`: what to do (census).
- Knowledge → `references/`: what to know, loaded at the step that needs it (census).
- Solutions → `scripts/`: what must be identical every run (census).
- State → the state slot in § 5: what must be remembered between runs, by full path (census).
- Learning → **references/runs.md** (the raw log, never edited) plus **references/lessons.md** (routed lessons, with an autonomy table at its head) (standard § 7).
- History → the build's own folder in the workspace: spec, research, plans, tests, a log; never inside the skill (census).

## 7. What the feedback loop needs from a skill
This section is the one home of the loop's definition; nothing else restates it (census).
- The close line, exact, as the last line of the top-level skill; the user's bare "1", "2", "3" or "later" is the invocation (census).
- A skill called by another never prints its own close line; only the top-level skill the user invoked gets the loop (census).
- One rule per line: every loop edit is a delta that appends or patches one identified line, never a regenerated file (census).
- Every path full and resolvable: a path one folder short is a FAIL (census).
- A hands-off marker pair, `<!-- feedback-loop: hands-off -->` on its own line before and after the user's verbatim text; inside the markers the loop may only propose, never apply (census).
- Attribution on every rule, so the loop can tell the user's own rule (propose only) from wording it may clarify on its own (census).
- The loop creates **references/runs.md** and **references/lessons.md** at its first run, never the builder; any patch to a skill goes behind the snapshot (census).
- The autonomy table at the head of lessons.md is seeded by the loop at its first run, not by the builder; a decision not in the table is at the lowest rung (ask first) by definition (census).
- Skills are named by their skills-home name in the loop's own files, never by a numbered folder path (census).
- Depth 1 = one row appended to **references/runs.md** (date, depth, summary, corrections, signal). Depth 2 = the row, plus a re-read of the skill for the one rule the run bent and a one-line patch proposed to the user. Depth 3 = the row, the re-read, and a fresh-eyes read of what the run produced, a day later. "later" = nothing now; the next run asks again. The AI in the chat runs it; a build protocol with its own loop runs the same three depths (census).

## 8. Registration
- The link recipe, in this order (only when skills are kept in the workspace and linked into the folder the platform auto-loads): check what is already there (list the target name; expect "no such file", or a link you mean to replace) → make the link (`ln -sfn "<target folder>" "<link>"`) → verify by following the link (a plain listing that resolves the link, not just shows it). Windows form beside it: `mklink /J "<link>" "<target>"`, then `dir "<link>"` to confirm the junction resolves (cost: a plain link made directly over an existing one nested inside it instead of replacing it, and the skill silently stopped loading).
- One registry row per skill, in the file the user's setup names as the registry (a skills index, a README table, or none if the folder listing is the list); a new or renamed skill is seen only by a fresh session, never mid-chat (census).
- Retire what a skill replaces with a pointer line ("Retired `<date>` → now the `<name>` skill."), and leave the old file in place; never delete it, or the old copy gets found and followed by mistake (cost: a replaced file's old body stayed live after the replacement, and it got found and followed by mistake).
- Description parity, checked at registration: every trigger phrase the user gave is in the description, in their words (census).
- Every touch to a link, a hook, or a standing-instructions file gets its own ask, always; the registry row itself is a do-and-report exception when the setup says so (census).

## 9. What the standard does not impose
- A fixed gate string on every step of a build protocol: that belongs to the build protocol, not to this standard; a thought-partner skill varies its gate phrasing on purpose (census).
- Rule position: the rules block moves above the spine only when F3 is set; a fleet-wide "rules after steps" would make an F3 skill worse (census).
- A pipeline batching its human gates into one pass so a queue can run unattended, and a model ladder tied to which resource a task holds, rather than one mode line: that is the pipeline's own design, not a standard requirement (census).
- A run that is not one chat: a pipeline can survive being compacted and hand off to a fresh orchestrator; this standard does not require or forbid it (census).
- A skill's existing state files stay where they are once they work; this standard does not force a working skill to relocate its state slot (census).
- Not touched by this file: any skill's behavior, the feedback loop's own behavior, or a validator's bugs. "It's not broken, so it doesn't need fixing." (census)
