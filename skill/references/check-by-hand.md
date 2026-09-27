# The ten checks, by hand

Run these with a text search and your eyes when there is no shell, or when you want to see for yourself. Each check names what to look at, what PASS looks like, and what FAIL looks like.

**1. name.** Look at: the `name:` line in SKILL.md's frontmatter. PASS: bare kebab-case, 1 to 64 characters, no "claude" or "anthropic" in it, and it equals the skill's name in the skills home. FAIL: missing, capitalized, contains a space, or does not match the skills-home name.

**2. description.** Look at: the `description:` line. PASS: present, 1,024 characters or fewer, no angle brackets, and it says when the skill fires. FAIL: over the limit, has `<` or `>`, or never says "use when" or similar.

**3. size.** Look at: `wc -l SKILL.md`. PASS: 500 lines or fewer (warn if over 150). FAIL: over 500.

**4. paths.** Look at: every path-shaped token in the skill's `.md` files. PASS: each one resolves, checked from the skill folder, as an absolute path, or, when it starts with a top-level folder of the workspace, from the workspace root. FAIL: any path that does not exist at that location.

**5. close line.** Look at: the last non-blank line of SKILL.md. PASS: the exact close line the setup uses, with its number filled in. FAIL: missing, reworded, or not the last line. Skip if the skill is called only from another skill.

**6. placeholders.** Look at: a text search for `[NEEDS CLARIFICATION` outside backticks. PASS: no matches. FAIL: any match.

**7. feedback-loop files.** Look at: **references/runs.md** and **references/lessons.md**. PASS: absent on a brand-new skill (the loop creates them on its first run), and if present, an empty lessons file carries a "none yet" line. FAIL: either file pre-created by the builder with no loop run behind it.

**8. discovery.** Look at: the skill's bare name inside the skills home. PASS: it resolves to a folder holding SKILL.md. FAIL: no such folder, or it resolves somewhere else. Skip on a path target.

**9. registry.** Look at: the registry file the setup names. PASS: the skill's name appears as a row. FAIL: no row. Skip if there is no registry, or on a path target.

**10. fixture.** Look at: the fixture file, when one was given. PASS: it names the SKILL.md path and one prompt, and every other line is a path, no pasted text longer than 3 lines. FAIL: pasted content instead of a path, or no prompt.

## The snapshot, by hand

Before any door 2 edit: copy the whole skill folder to `history/snapshots/<name>-<date>/` inside the blacksmith skill folder. Keep the copy until the re-check after the edit passes. To restore, copy that snapshot back over the live folder.
