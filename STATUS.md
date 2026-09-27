# Kit progress

> Maintained by the installing AI. Tick tasks as they complete; record decisions the moment they're made. A fresh session resumes from this file alone.

## Scan results (Phase 0)

| Check | Finding |
|---|---|
| Consent to look at the skills setup and instructions file given? | _pending_ |
| Platform and capabilities (files? shell? Python 3.9+? sub-agents?) | _pending_ |
| Operating system | _pending_ |
| How the platform discovers skills | _pending_ |
| The directory it reads | _pending_ |
| Where the user's work lives (the workspace) | _pending_ |
| The standing-instructions file, and does the platform actually auto-read it | _pending_ |
| Skills that already exist (count and names) | _pending_ |
| An existing skills index | _pending_ |
| An installed build protocol with a plan the user approves | _pending_ |
| Do the user's skills sit in a git repo | _pending_ |

## Decisions (Phase 1)

| # | Decision | Choice | Notes |
|---|---|---|---|
| DP-1 | Where skills live and how the AI finds them | _pending_ | |
| DP-2 | What hands Blacksmith a new skill to shape | _pending_ | |
| DP-3 | How much feedback loop skills get | _pending_ | |
| DP-4 | Who does the cold read | _pending_ | |
| DP-5 | How the mechanical check runs | _pending_ | |
| DP-6 | Where the list of skills is kept | _pending_ | |

## Tasks

### Phase 0: Environment scan
- [ ] Consent asked and given
- [ ] Platform, capabilities and operating system identified
- [ ] Skills-discovery method and directory found (or chat-only path confirmed)
- [ ] Workspace located
- [ ] Standing-instructions file read, and its auto-read behavior confirmed
- [ ] Existing skills, index, build protocol and git status checked
- [ ] Scan results recorded above

### Phase 1: Decisions
- [ ] DP-1 through DP-6 decided and recorded above

### Phase 2: Install
- [ ] `skill/` copied to the DP-1 location as `blacksmith/`
- [ ] `scripts/blacksmith.json` edited for DP-1, DP-3 and DP-6
- [ ] `templates/fixture.md` and `templates/plan-card.md` confirmed inside the installed `blacksmith` folder
- [ ] Named edits to `SKILL.md` / `standard.md` applied for the relevant DP branches
- [ ] The blacksmith row added to the skills index (DP-6 A: the user's own index, after asking; DP-6 B: `templates/skills-index.md` installed first)
- [ ] `check.py --selftest` and the check on `blacksmith` both PASS (or the by-hand checklist walked, DP-5 B)
- [ ] Standing-instructions file wired with the quoted line
- [ ] Build protocol's build step edited (DP-2 A only)
- [ ] Every install path recorded below

| Install paths | |
|---|---|
| `blacksmith` folder | _pending_ |
| `blacksmith.json` final contents | _pending_ |
| Named edits made to `SKILL.md` / `standard.md` | _pending_ / none |
| Skills index (if installed) | _pending_ / n/a |
| Instructions file edited | _pending_ |
| Build protocol edited | _pending_ / n/a |
| Link created (DP-1 B only) | _pending_ / n/a |

### Phase 3: First live run
- [ ] Skill (or plan-card thing) chosen with the user; smallest first
- [ ] Snapshot taken and restore command printed (door 2) or folder drafted (door 1)
- [ ] Check run before any change
- [ ] Two-bucket report given; user ruled on Needs-you items
- [ ] Approved changes applied behind the snapshot
- [ ] Check re-run after
- [ ] Verification test (a): check passes on the target, fails on `example/dirty-skill`
- [ ] Verification test (b): fresh session fires blacksmith unnamed
- [ ] Verification test (c): the cold read completes, per DP-4

| First run | |
|---|---|
| Skill or thing worked on | _pending_ |
| Check result before / after | _pending_ / _pending_ |
| Snapshot stamp | _pending_ / n/a |
| Elapsed minutes, install / first run | _pending_ |

### Phase 4: Wrap
- [ ] User walked through what's installed and where
- [ ] Install record (scan table + decisions table) copied to `<blacksmith install path>/references/install-record.md`
- [ ] This file fully ticked; final state recorded

## Blockers

- none
