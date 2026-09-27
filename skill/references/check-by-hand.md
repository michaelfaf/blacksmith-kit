# The ten checks, by hand

Run these with a text search and your eyes when there is no shell, or when you want to see for yourself. Each check names what to look at, what PASS looks like, and what FAIL looks like.

**1. name.** Look at: the `name:` line in SKILL.md's frontmatter. PASS: bare kebab-case, 1 to 64 characters, no "claude" or "anthropic" in it, and it equals the skill's name in the skills home. FAIL: missing, capitalized, contains a space, or does not match the skills-home name.

**2. description.** Look at: the `description:` line. PASS: present, 1,024 characters or fewer, no angle brackets, and it says when the skill fires. FAIL: over the limit, has `<` or `>`, or never says "use when" or similar.

**3. size.** Look at: the number of lines in SKILL.md (a last line with no line break still counts). PASS: 500 lines or fewer (warn if over 150). FAIL: over 500.

**4. paths.** Look at: every path written in backticks or as a link target in the skill's `.md` files that is absolute or starts with `./`, `~/`, references/, scripts/, templates/, assets/, history/ or the name of a top-level folder of the workspace. Paths in plain text are not checked. PASS: each one resolves from the file that names it, from the skill folder, or from the workspace root. FAIL: a path that resolves from none of them.

**5. close line.** Look at: the last non-blank line of SKILL.md. PASS: the exact close line the setup uses, with its number filled in. FAIL: missing, reworded, or not the last line. Skip if the skill is called only from another skill, or if `close_line` is null in Blacksmith's `scripts/blacksmith.json` (no feedback loop in this install).

**6. placeholders.** Look at: a text search for `[NEEDS CLARIFICATION` outside backticks. PASS: no matches. FAIL: any match.

**7. feedback-loop files.** Look at: **references/runs.md** and **references/lessons.md**. PASS: absent on a brand-new skill (the loop creates them on its first run), and if present, an empty lessons file carries a "none yet" line. FAIL: either file pre-created by the builder with no loop run behind it.

**8. discovery.** Look at: the skill's bare name inside the skills home. PASS: it resolves to a folder holding SKILL.md. FAIL: no such folder, or it resolves somewhere else. Skip on a path target.

**9. registry.** Look at: the registry file the setup names. PASS: the skill's name appears as a row. FAIL: no row. Skip if there is no registry, or on a path target.

**10. fixture.** Look at: the fixture file, when one was given. PASS: every field is filled in, it names the SKILL.md path and one prompt, and everything else is a path: no pasted text longer than 3 lines, quoted or not. FAIL: a field left as the template had it, pasted content instead of a path, or no prompt.

## The snapshot, by hand

Before any door 2 edit: copy the skill folder to `history/snapshots/[name]-[date]/` inside the blacksmith skill folder, leaving out the skill's own top-level history folder. Keep the copy until the re-check after the edit passes. To restore: delete everything in the live folder except its history folder, then copy the snapshot back in. Copying over the top without deleting first would leave behind any file the bad edit created.
