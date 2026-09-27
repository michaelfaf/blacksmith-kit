#!/usr/bin/env python3
"""check.py: the standard's mechanical check of one skill folder. python3 (3.9+), stdlib only.

  python3 check.py <skill-name-or-path> [--fixture FILE] [--json]
  python3 check.py --snapshot <skill-name-or-path>
  python3 check.py --restore <name> <stamp>
  python3 check.py --selftest

A bare name resolves through the configured skills home (blacksmith.json, next to this script);
a path (anything with a slash, or starting with . or ~) is used as-is. Ten checks, one line each
(check 10 only with --fixture): PASS / FAIL / WARN / SKIP / INFO, then the verdict:
`PASS <name>` (exit 0) or `FAIL <name>: <n> failures` (exit 1). WARN and INFO never move the verdict.
This is the automatic half of the standard's check; the other half is a cold read of the skill
by a fresh agent or a second person, from the fixture's paths.
"""
import argparse, contextlib, io, json, os, re, shlex, shutil, sys, tempfile, time
from datetime import datetime
from pathlib import Path

MAX_DESC, WARN_DESC = 1024, 600
MAX_LINES, WARN_LINES = 500, 150
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
CODE_SPAN = re.compile(r"`[^`\n]*`")
TRIGGER_RE = re.compile(r"\buse\b[^.]{0,60}\b(when|whenever|for|after|if)\b|\btrigger", re.I)
TOKEN_RE = re.compile(r"`([^`\n]+)`|\[\[([^\]\n]+)\]\]|\]\(([^)\s]+)\)")
PLACEHOLDER = "[NEEDS " + "CLARIFICATION"        # two halves so this file never carries the literal it hunts
SKIP_TOKENS = ("[", "]", "<", ">", "…", "...", "{", "YYYY", "$", "http")
EXTS = (".md", ".py", ".sh", ".json", ".csv", ".html", ".txt", ".yaml", ".yml")
LOGS = {"runs.md", "lessons.md"}
EXCLUDE_DIRS = {".git", ".venv", "__pycache__", "node_modules", "backups", "history"}
DEFAULT_CONFIG = {"skills_home": None, "workspace_root": None, "registry": None,
                   "close_line": "Done. Feedback loop: 1, 2, 3, or later? (usual: N)"}

def blacksmith_folder():
    return Path(__file__).absolute().parents[1]   # one level up from this script's own folder

def load_config():
    # blacksmith.json next to this script; missing file or key -> the default; skills_home null -> the blacksmith folder's parent (no link resolution).
    cfg = dict(DEFAULT_CONFIG); cfg_path = Path(__file__).absolute().parent / "blacksmith.json"
    if cfg_path.is_file():
        try: data = json.loads(cfg_path.read_text(errors="replace"))
        except (OSError, ValueError): data = {}
        cfg.update({k: data[k] for k in DEFAULT_CONFIG if k in data})
    cfg["skills_home"] = Path(cfg["skills_home"]).expanduser() if cfg["skills_home"] else Path(__file__).absolute().parents[2]
    cfg["workspace_root"] = Path(cfg["workspace_root"]).expanduser() if cfg.get("workspace_root") else None
    return cfg

def resolve_config_path(p, cfg):
    # a configured path (e.g. registry) may be relative: anchor to workspace_root, else skills_home, else the current directory.
    if not p:
        return None
    pp = Path(p).expanduser(); return pp if pp.is_absolute() else (cfg.get("workspace_root") or cfg.get("skills_home") or Path.cwd()) / pp

def resolve_target(arg, skills_home):
    # (root, bare_name_or_None). A bare name always means the skill of that name in the skills home; a local folder is written ./name.
    p = Path(arg).expanduser()
    if "/" in arg or os.sep in arg or arg.startswith(("~", ".")):
        return p.resolve(), None
    return (skills_home / arg), arg

def frontmatter(text):
    m = re.match(r"^---\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|$)", text, re.S)
    return m.group(1) if m else None

def fm_scalar(fm, key):
    # a top-level key's value: plain, quoted, or a `>` / `|` block scalar (indented lines joined: folded with a space, literal with a newline; a few chars of drift from YAML's own blank-line folding).
    lines = fm.splitlines()
    for i, ln in enumerate(lines):
        m = re.match(rf"^{re.escape(key)}:[ \t]*(.*)$", ln)
        if not m:
            continue
        val = m.group(1).strip()
        if re.fullmatch(r"[>|][+-]?\d?", val):
            block = []
            for nxt in lines[i + 1:]:
                if nxt.strip() == "":
                    continue
                if nxt[:1] not in (" ", "\t"):
                    break
                block.append(nxt.strip())
            return (" " if val[0] == ">" else "\n").join(block).strip(), "block (" + val[0] + ")"
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            val = val[1:-1]
        else:
            val = re.sub(r"\s+#.*$", "", val)      # a YAML comment after a plain value
        return val, "plain"
    return None, None

def build_path_prefix(workspace_root):
    # a token is checked when absolute, `~/`, or under one of the skill's own folders: or, with workspace_root set, under one of its top-level folders (contract § 6, check 4).
    base = r"^(/[^/]+/|~/|\./|references/|scripts/|templates/|assets/|history/"
    if workspace_root and workspace_root.is_dir():
        tops = sorted({d.name for d in workspace_root.iterdir() if d.is_dir()}, key=len, reverse=True)
        if tops:
            base += "|" + "|".join(re.escape(t) + "/" for t in tops)
    return re.compile(base + ")")

def path_exists(tok, root, md, workspace_root):
    p = Path(os.path.expanduser(tok))
    cands = [p] if p.is_absolute() else [md.parent / p, root / p] + ([workspace_root / p] if workspace_root else [])
    if not tok.endswith(EXTS) and not tok.endswith("/"):
        cands += [c.with_name(c.name + ".md") for c in list(cands)]   # `folder/README` → README.md
    return any(c.exists() for c in cands)

def check_paths_in(md, root, workspace_root, path_prefix, seen, bad):
    # ponytail: heuristic, not a Markdown parser. A whole path-shaped token is checked as-is (spaces allowed); a command line is split with shlex so quoted paths survive and only its path-shaped pieces are checked; anything else is ignored rather than guessed.
    text, count = md.read_text(errors="replace"), 0
    for m in TOKEN_RE.finditer(text):
        tok = m.group(1) or (m.group(2) or m.group(3)).split("|")[0].split("#")[0]
        tok = re.sub(r":\d+(?:-\d+)?(?::\d+)?$", "", tok.strip())     # file.md:16-34 → file.md
        if not (("/" in tok or tok.endswith(EXTS)) and not any(s in tok for s in SKIP_TOKENS)):
            continue
        if path_prefix.match(tok):
            pieces = [tok]
        elif " " in tok:
            try: parts = shlex.split(tok)
            except ValueError: parts = tok.split()
            pieces = [p for p in parts if path_prefix.match(p) and (("/" in p or p.endswith(EXTS)) and not any(s in p for s in SKIP_TOKENS))]
        else:
            continue
        for pc in pieces:
            count += 1
            if pc in seen:
                continue
            if not path_exists(pc, root, md, workspace_root):
                seen.add(pc)
                bad.append((f"{md.relative_to(root)}:{text.count(chr(10), 0, m.start()) + 1}", pc))
    return count

def skill_docs(root):
    # every .md in the folder minus the feedback loop's two logs (history/ excluded above, a record, not direction).
    docs = [root / "SKILL.md"] + sorted(p for p in root.rglob("*.md") if p != root / "SKILL.md")
    return [d for d in docs if d.is_file() and d.name not in LOGS and not EXCLUDE_DIRS & set(d.relative_to(root).parts)]

class Report:
    def __init__(self): self.rows = []
    def add(self, n, name, status, detail, where=None): self.rows.append({"check": n, "name": name, "status": status, "detail": detail, "where": where})
    @property
    def failures(self): return sum(r["status"] == "FAIL" for r in self.rows)

def run_checks(target, cfg, fixture=None):
    root, bare = resolve_target(target, cfg["skills_home"])
    workspace_root, close_line = cfg.get("workspace_root"), cfg.get("close_line")
    rep, name = Report(), bare or Path(target).name
    if not root.is_dir():
        rep.add(0, "target", "FAIL", f"no folder at {root}"); return rep, name
    skill = root / "SKILL.md"
    if not skill.is_file():
        rep.add(0, "target", "FAIL", f"no SKILL.md at {root}"); return rep, name
    text = skill.read_text(errors="replace")
    lines = text.splitlines()
    fm = frontmatter(text)
    fm_name = None
    # 1 · name
    if fm is None:
        rep.add(1, "frontmatter", "FAIL", "no frontmatter block (--- … ---) at the top of SKILL.md", "SKILL.md:1")
    else:
        fm_name, _ = fm_scalar(fm, "name")
        if not fm_name:
            rep.add(1, "name", "FAIL", "frontmatter has no name", "SKILL.md:2")
        elif not NAME_RE.match(fm_name):
            rep.add(1, "name", "FAIL", f"name {fm_name!r} is not bare kebab-case (lowercase letters, digits, hyphens; 1–64 chars)", "SKILL.md:2")
        elif "claude" in fm_name or "anthropic" in fm_name:
            rep.add(1, "name", "FAIL", f"name {fm_name!r} must not contain \"claude\" or \"anthropic\"", "SKILL.md:2")
        elif bare and fm_name != bare:
            rep.add(1, "name", "FAIL", f"name {fm_name!r} ≠ the skill's name {bare!r}", "SKILL.md:2")
        else:
            rep.add(1, "name", "PASS", f"name {fm_name!r}" + (" equals the skill's name" if bare else " is bare kebab-case (path target: name not compared)"), "SKILL.md:2")
        if not bare and fm_name and NAME_RE.match(fm_name):
            name = fm_name
    # 2 · description
    if fm is not None:
        desc, style = fm_scalar(fm, "description")
        if desc is None:
            rep.add(2, "description", "FAIL", "frontmatter has no description")
        elif not desc.strip():
            rep.add(2, "description", "FAIL", "description is empty")
        else:
            n, probs = len(desc), []
            if n > MAX_DESC:
                probs.append(f"{n} chars > {MAX_DESC}")
            if "<" in desc or ">" in desc:
                probs.append("contains angle brackets: write [skill], not <skill>")
            if not TRIGGER_RE.search(desc):   # ponytail: heuristic: never says when it fires
                probs.append("no trigger phrases: say when it fires (\"Use when …\")")
            st2 = "FAIL" if probs else "WARN" if n > WARN_DESC else "PASS"
            rep.add(2, "description", st2, ("; ".join(probs) + f" ({style})") if probs else (f"{n} chars: aim ≈ 500, hard cap {MAX_DESC} ({style})" if st2 == "WARN" else f"{n} chars ({style})"))
    # 3 · size
    n = len(lines)
    st3 = "FAIL" if n > MAX_LINES else "WARN" if n > WARN_LINES else "PASS"
    rep.add(3, "size", st3, f"SKILL.md is {n} lines" + (f" > {MAX_LINES}" if st3 == "FAIL" else f": target ≈ {WARN_LINES}, hard cap {MAX_LINES}" if st3 == "WARN" else ""))
    # 4 · paths resolve
    path_prefix = build_path_prefix(workspace_root)
    seen, bad, count = set(), [], 0
    for md in skill_docs(root):
        count += check_paths_in(md, root, workspace_root, path_prefix, seen, bad)
    if bad:
        rep.add(4, "paths", "FAIL", f"{len(bad)} missing of {count} checked: " + " · ".join(f"{w} `{p}`" for w, p in bad), bad[0][0])
    else:
        rep.add(4, "paths", "PASS", f"{count} path-shaped tokens resolve; paths in plain text are not checked" + ("" if workspace_root else " (no workspace root set: only skill-relative and absolute paths checked)"))
    # 5 · close line (its own `N` inside `(usual: N)` matches 1, 2 or 3; everything else literal)
    if close_line is None:
        rep.add(5, "close line", "SKIP", "no feedback loop chosen: close_line is null in blacksmith.json")
    else:
        parts = close_line.split("(usual: N)", 1)
        pattern = (re.escape(parts[0]) + r"\(usual: [123]\)" + re.escape(parts[1])) if len(parts) == 2 else re.escape(close_line)
        close_re = re.compile(r"^\s*" + pattern + r"\s*$")
        exact = [i + 1 for i, ln in enumerate(lines) if close_re.match(ln)]
        last = max((i + 1 for i, ln in enumerate(lines) if ln.strip()), default=0)
        if exact:
            at = exact[-1]
            rep.add(5, "close line", "PASS" if at == last else "FAIL",
                     "exact, last line" if at == last else f"exact at line {at} but not the last line (last non-blank line is {last}): standard § 1.5", f"SKILL.md:{at}")
        else:
            km = re.match(r"^\s*Done\.\s*(.+?):", close_line)   # the phrase before the first colon, to spot a near-miss
            keyword = (km.group(1) + ":") if km else None
            near = [(i + 1, ln.strip()) for i, ln in enumerate(lines) if keyword and keyword in ln and ("Done" in ln or "later" in ln)]
            if near:
                at, ln = near[-1]
                rep.add(5, "close line", "FAIL", f"near-miss: expected `{close_line}`, found `{ln[:140]}`", f"SKILL.md:{at}")
            elif "never prints the close line" in text or "nesting rule" in text:
                rep.add(5, "close line", "SKIP", "absent by design: SKILL.md says it is called only from another skill")
            else:
                rep.add(5, "close line", "FAIL", f"absent: add `{close_line}` as the last line")
    # 6 · placeholders (a backticked mention is quoted text, not a placeholder)
    hits = []
    for f in sorted(root.rglob("*")):
        rel = f.relative_to(root)
        if not f.is_file() or EXCLUDE_DIRS & set(rel.parts) or f.stat().st_size > 2_000_000:
            continue
        try: body = f.read_text(errors="replace")
        except OSError: continue
        for i, ln in enumerate(body.splitlines(), 1):
            if PLACEHOLDER in CODE_SPAN.sub("", ln):
                hits.append(f"{rel}:{i}")
    rep.add(6, "placeholders", "FAIL" if hits else "PASS",
            (PLACEHOLDER + " left in a shipped skill: " + ", ".join(hits)) if hits else ("no " + PLACEHOLDER + " in the folder"),
            hits[0] if hits else None)
    # 7 · feedback-loop files (an empty lessons file needs a "none yet" line)
    refs = root / "references"
    present = [n for n in ("runs.md", "lessons.md") if (refs / n).is_file()]
    empty_at = None
    if "lessons.md" in present:
        ll = (refs / "lessons.md").read_text(errors="replace").splitlines()
        if not any(l.strip() for l in ll):
            empty_at = 1
        for i, ln in enumerate(ll):
            if re.match(r"^##\s+Lessons\b", ln, re.I):
                body = []
                for nxt in ll[i + 1:]:
                    if nxt.startswith("#"):
                        break
                    body.append(nxt)
                if not any(b.strip() for b in body):
                    empty_at = i + 1
                break
    if empty_at:
        rep.add(7, "feedback-loop files", "FAIL", "empty lessons file needs a 'none yet' line", f"references/lessons.md:{empty_at}")
    elif present and fixture:   # a fixture means door 1, a skill being built: any log present was pre-created
        rep.add(7, "feedback-loop files", "FAIL", "pre-created by the builder: the feedback loop creates these on its first run: " + ", ".join(present))
    elif present:
        rep.add(7, "feedback-loop files", "INFO", "present, the feedback loop's (never pre-created by the standard): " + ", ".join(present))
    else:
        rep.add(7, "feedback-loop files", "PASS", "runs.md / lessons.md not pre-created")
    # 8 · discovery
    if bare:
        found = (cfg["skills_home"] / bare / "SKILL.md").is_file()
        rep.add(8, "discovery", "PASS" if found else "FAIL", f"{bare} {'resolves inside' if found else 'does not resolve, inside'} {cfg['skills_home']} to a folder with SKILL.md")
    else:
        rep.add(8, "discovery", "SKIP", "path target: no discovery check")
    # 9 · registry (one configurable file)
    if not bare:
        rep.add(9, "registry", "SKIP", "path target: a copy is not registered by design")
    elif not cfg.get("registry"):
        rep.add(9, "registry", "SKIP", "no registry configured: registry is null in blacksmith.json")
    else:
        reg_path = resolve_config_path(cfg["registry"], cfg)
        if not reg_path.is_file():
            rep.add(9, "registry", "SKIP", f"registry file not found at {reg_path}")
        else:
            word = re.compile(rf"(?<![A-Za-z0-9-]){re.escape(bare)}(?![A-Za-z0-9-])")
            hit = any(word.search(l) for l in reg_path.read_text(errors="replace").splitlines() if re.match(r"\s*(\||[-*] |\d+\. )", l))   # a table row or a list item
            rep.add(9, "registry", "PASS" if hit else "FAIL", f"{bare} {'listed in' if hit else 'not listed in'} {reg_path}")
    # 10 · fixture
    if fixture:
        fp = Path(fixture).expanduser()
        if not fp.is_file():
            rep.add(10, "fixture", "FAIL", f"not found: {fp}")
        else:
            body = re.sub(r"<!--.*?-->", "", fp.read_text(errors="replace"), flags=re.S)
            probs, quoted = [], 0
            if "SKILL.md" not in body:
                probs.append("does not name the SKILL.md path")
            if not re.search(r"(?im)^[ \t]*(>[ \t]*\S|.*prompt[^:\n]*:[ \t]*\S)", body):
                probs.append("no prompt given")
            if re.search(r"<[^<>\n]+>", body):
                probs.append("a template field is still unfilled")
            run, start = 0, None
            for i, ln in enumerate(body.splitlines(), 1):
                s = ln.strip()   # a path, heading, blank or "prompt" line resets the run; >3 lines of anything else, or of quoted text, looks like pasted reference text.
                quoted += s.startswith(">") and len(s) > 1
                if not s or s.startswith(("#", ">")) or "/" in s or s.endswith(EXTS) or re.search(r"prompt", s, re.I):
                    run = 0
                    continue
                run += 1
                start = start if run > 1 else i
                if run > 3:
                    probs.append(f"pasted text longer than 3 lines from line {start}: paths only")
                    break
            if quoted > 3:
                probs.append(f"{quoted} quoted lines: a prompt is short, a reference is a path")
            rep.add(10, "fixture", "FAIL" if probs else "PASS", "; ".join(probs) if probs else f"names SKILL.md, a prompt, and paths only ({fp.name})", str(fp) if probs else None)
    return rep, name

def emit(rep, name, as_json):
    verdict = "PASS" if rep.failures == 0 else "FAIL"
    if as_json:
        print(json.dumps(rep.rows + [{"check": "verdict", "name": name, "status": verdict, "failures": rep.failures}], ensure_ascii=False, indent=1))
    else:
        for r in rep.rows:
            where = f"  [{r['where']}]" if r["where"] else ""; print(f"{r['status']:<4} {str(r['check']):>2} {r['name']}: {r['detail']}{where}")
        print(f"PASS {name}" if verdict == "PASS" else f"FAIL {name}: {rep.failures} failure{'s' if rep.failures != 1 else ''}")
    return 0 if verdict == "PASS" else 1

def snapshots_home(home=None):
    return (home or blacksmith_folder()) / "history" / "snapshots"

SOURCE_NOTE = ".blacksmith-source"          # inside each snapshot: the folder it was taken from
LEFT_OUT = ("history", ".git", "__pycache__")   # top level of the skill only: state and tooling, not direction

def do_snapshot(arg, cfg, home=None):
    # the guard: copy the skill folder to history/snapshots/<name>-<stamp>/ and print the restore command.
    # ponytail: the skill's own top-level history/ is state, not direction; it stays out of the snapshot and a restore leaves it alone.
    root, bare = resolve_target(arg, cfg["skills_home"]); name = bare or root.name
    if not root.is_dir():
        print(f"no folder at {root}"); return 1
    while True:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S"); dest = snapshots_home(home) / f"{name}-{stamp}"
        if not dest.exists():
            break
        time.sleep(1)                       # two snapshots of one skill in the same second
    dest.parent.mkdir(parents=True, exist_ok=True)
    top = str(root)
    shutil.copytree(root, dest, symlinks=True, ignore=lambda d, names: [n for n in names if d == top and n in LEFT_OUT])
    (dest / SOURCE_NOTE).write_text(str(root.absolute()) + "\n")
    print(f"snapshot: {dest}"); print(f'restore command: python3 "{Path(__file__).absolute()}" --restore {shlex.quote(name)} {stamp}')
    return 0

def do_restore(name, stamp, cfg, home=None):
    src = snapshots_home(home) / f"{name}-{stamp}"
    if not src.is_dir():
        print(f"no snapshot at {src}: refusing to restore"); return 1
    note = src / SOURCE_NOTE                 # restore to where the snapshot was taken, not to whatever the name means today
    root = Path(note.read_text().strip()) if note.is_file() else resolve_target(name, cfg["skills_home"])[0]
    root.mkdir(parents=True, exist_ok=True)
    for child in root.iterdir():            # everything the snapshot covers goes; what it left out stays
        if child.name in LEFT_OUT:
            continue
        shutil.rmtree(child) if child.is_dir() and not child.is_symlink() else child.unlink()
    shutil.copytree(src, root, symlinks=True, dirs_exist_ok=True, ignore=shutil.ignore_patterns(SOURCE_NOTE))
    print(f"restored {root} from {src}"); return 0

def selftest():
    # synthetic skills in a temp folder with their own fake skills home and workspace root: touches nothing real; the config below is built in memory and handed to run_checks directly.
    tmp = Path(tempfile.mkdtemp(prefix="blacksmith-selftest-"))
    skills_home, workspace = tmp / "skills", tmp / "workspace"
    skills_home.mkdir()
    (workspace / "docs").mkdir(parents=True)
    (workspace / "docs" / "README.md").write_text("# map\n")
    registry = workspace / "docs" / "skills-index.md"
    registry.write_text("- clean-skill\n")
    close_line = "Done. Feedback loop: 1, 2, 3, or later? (usual: N)"
    cfg = {"skills_home": skills_home, "workspace_root": workspace, "close_line": close_line, "registry": str(registry)}
    checks = 0

    def status(rep, n): return [r["status"] for r in rep.rows if r["check"] == n]
    def detail(rep, n): return " | ".join(r["detail"] for r in rep.rows if r["check"] == n)

    def ok(cond, msg):
        nonlocal checks
        assert cond, msg
        checks += 1

    def mk(nm, content, **kw):
        d = skills_home / nm; d.mkdir(parents=True, exist_ok=True); (d / "SKILL.md").write_text(content)
        return run_checks(nm, kw.pop("cfg", cfg), **kw)
    # dirty: folded description, real missing path, placeholder skipped, near-miss close line, empty lessons
    dirty = skills_home / "dirty-skill"; (dirty / "references").mkdir(parents=True)
    folded = "Use when testing the check on a synthetic skill with a folded description."
    (dirty / "SKILL.md").write_text("---\nname: dirty-skill\ndescription: >\n  Use when testing the check on a\n  synthetic skill with a folded description.\n---\n# dirty\n\nMode: test.\n\n1. Read `docs/README.md` now.\n2. Read `docs/<category>/<nn> placeholder/SKILL.md` (placeholder, skipped).\n3. Read `docs/99 nope/references/missing.md`.\n4. Decide " + PLACEHOLDER + ": which model].\n\nDone. Feedback loop: 1, 2, 3 or later? (usual: 2)\n")
    (dirty / "references" / "lessons.md").write_text("# dirty-skill: lessons\n\n## Lessons\n\n")
    rep, name = run_checks("dirty-skill", cfg)
    ok(name == "dirty-skill", name)
    ok(status(rep, 1) == ["PASS"], detail(rep, 1))
    ok(status(rep, 2) == ["PASS"] and f"{len(folded)} chars (block (>))" in detail(rep, 2), detail(rep, 2))
    ok(status(rep, 4) == ["FAIL"] and "99 nope" in detail(rep, 4) and "placeholder" not in detail(rep, 4) and "README" not in detail(rep, 4) and "1 missing" in detail(rep, 4), detail(rep, 4))
    ok(status(rep, 5) == ["FAIL"] and "near-miss" in detail(rep, 5) and "3 or later" in detail(rep, 5), detail(rep, 5))
    ok(status(rep, 6) == ["FAIL"] and "SKILL.md:14" in detail(rep, 6), detail(rep, 6))
    ok(status(rep, 7) == ["FAIL"] and "none yet" in detail(rep, 7), detail(rep, 7))
    ok(status(rep, 8) == ["PASS"], detail(rep, 8))
    ok(status(rep, 9) == ["FAIL"], detail(rep, 9))   # dirty-skill is not in the registry
    ok(rep.failures == 5, f"expected 5 failures, got {rep.failures}: {[r for r in rep.rows if r['status'] == 'FAIL']}")
    # clean: exact close line, backticked placeholder mention, paths resolve, listed in the registry
    clean = skills_home / "clean-skill"; (clean / "references").mkdir(parents=True)
    (clean / "SKILL.md").write_text("---\nname: clean-skill\ndescription: \"Use when testing the check on a clean synthetic skill; triggers on 'clean test'.\"\n---\n# clean\n\nMode: test.\n\n1. Read `references/notes.md` now; it points at `docs/README.md`.\n2. A `" + PLACEHOLDER + "` mention in backticks is quoted text, not a placeholder.\n\n## Hard rules\n- One rule.\n\nDone. Feedback loop: 1, 2, 3, or later? (usual: 1)\n")
    (clean / "references" / "notes.md").write_text("Pointer: `docs/README.md` (fake workspace).\n")
    rep, name = run_checks("clean-skill", cfg)
    ok(rep.failures == 0 and name == "clean-skill", [r for r in rep.rows if r["status"] == "FAIL"])
    ok(status(rep, 5) == ["PASS"] and status(rep, 6) == ["PASS"] and status(rep, 7) == ["PASS"] and status(rep, 9) == ["PASS"], [r for r in rep.rows if r["check"] in (5, 6, 7, 9)])
    ok(status(rep, 2) == ["PASS"] and "(plain)" in detail(rep, 2), detail(rep, 2))
    # fixtures: good (paths + prompt) vs bad (pasted text); a pre-created log fails only with a fixture
    good, bad = tmp / "fixture-good.md", tmp / "fixture-bad.md"
    good.write_text(f"SKILL.md: {clean / 'SKILL.md'}\nPrompt: clean test\nReferences: {clean / 'references'}\n")
    bad.write_text(f"SKILL.md: {clean / 'SKILL.md'}\nPrompt: clean test\n\nThe voice is direct.\nNo filler.\nShort sentences.\nNo AI phrasing.\n")
    rep, _ = run_checks("clean-skill", cfg, fixture=str(good))
    ok(status(rep, 10) == ["PASS"], detail(rep, 10))
    rep, _ = run_checks("clean-skill", cfg, fixture=str(bad))
    ok(status(rep, 10) == ["FAIL"] and "pasted text" in detail(rep, 10), detail(rep, 10))
    (clean / "references" / "runs.md").write_text("# runs\n")
    rep, _ = run_checks("clean-skill", cfg, fixture=str(good))
    ok(status(rep, 7) == ["FAIL"] and "pre-created" in detail(rep, 7), detail(rep, 7))
    rep, _ = run_checks("clean-skill", cfg)
    ok(status(rep, 7) == ["INFO"], detail(rep, 7))
    (clean / "references" / "runs.md").unlink()
    # no trigger phrase + close line not last + close_line null -> SKIP
    rep, _ = mk("notrig", "---\nname: notrig\ndescription: Logs gym sessions from a voice note.\n---\n# n\n\nDone. Feedback loop: 1, 2, 3, or later? (usual: 1)\n\nTrailing line after the close line.\n")
    ok(status(rep, 2) == ["FAIL"] and "trigger" in detail(rep, 2), detail(rep, 2))
    ok(status(rep, 5) == ["FAIL"] and "not the last line" in detail(rep, 5), detail(rep, 5))
    rep, _ = run_checks("notrig", dict(cfg, close_line=None))
    ok(status(rep, 5) == ["SKIP"] and "no feedback loop chosen" in detail(rep, 5), detail(rep, 5))
    # "claude" in the name + angle bracket/over-long description; no frontmatter + nested-skill SKIP
    rep, _ = mk("claude-helper", f"---\nname: claude-helper\ndescription: Use when prepping <Person> {'x' * 1030}\n---\n# f\n\nDone. Feedback loop: 1, 2, 3, or later? (usual: 1)\n")
    ok(status(rep, 1) == ["FAIL"] and "claude" in detail(rep, 1), detail(rep, 1))
    ok(status(rep, 2) == ["FAIL"] and "angle brackets" in detail(rep, 2) and "> 1024" in detail(rep, 2), detail(rep, 2))
    rep, _ = mk("nofm", "# no frontmatter\n\nCalled only from another skill: never prints the close line (nesting rule).\n")
    ok(status(rep, 1) == ["FAIL"] and status(rep, 5) == ["SKIP"], detail(rep, 1) + detail(rep, 5))
    # discovery SKIP on a path target; registry SKIP when null
    rep, _ = run_checks(str(clean), cfg)
    ok(status(rep, 8) == ["SKIP"] and status(rep, 9) == ["SKIP"], detail(rep, 8) + detail(rep, 9))
    rep, _ = run_checks("clean-skill", dict(cfg, registry=None))
    ok(status(rep, 9) == ["SKIP"] and "no registry" in detail(rep, 9), detail(rep, 9))
    # a workspace-rooted path that resolves, and one that does not (check 4, top-level-folder rule)
    rep, _ = mk("resolves", "---\nname: resolves\ndescription: \"Use when testing a workspace-rooted path.\"\n---\n# r\n\n1. See `docs/README.md`.\n\nDone. Feedback loop: 1, 2, 3, or later? (usual: 1)\n")
    ok(status(rep, 4) == ["PASS"], detail(rep, 4))
    rep, _ = mk("missing", "---\nname: missing\ndescription: \"Use when testing a workspace-rooted path that fails.\"\n---\n# m\n\n1. See `docs/nope.md`.\n\nDone. Feedback loop: 1, 2, 3, or later? (usual: 1)\n")
    ok(status(rep, 4) == ["FAIL"] and "docs/nope.md" in detail(rep, 4), detail(rep, 4))
    # the guard: snapshot then restore returns a changed file to its snapshot content
    guarded = skills_home / "guarded"; mk("guarded", "original content\n")
    (guarded / "history").mkdir(); (guarded / "history" / "ledger.md").write_text("kept\n")
    ok(do_snapshot("guarded", cfg, home=tmp) == 0, "snapshot did not return 0")
    snaps = sorted(snapshots_home(tmp).glob("guarded-*"))
    ok(len(snaps) == 1, f"expected one guarded snapshot, found {snaps}")
    stamp = snaps[0].name.split("guarded-", 1)[1]
    (guarded / "SKILL.md").write_text("changed content: should be reverted\n")
    ok(do_restore("guarded", stamp, cfg, home=tmp) == 0, "restore did not return 0")
    ok((guarded / "SKILL.md").read_text() == "original content\n", "restore did not return the original content")
    ok((guarded / "history" / "ledger.md").read_text() == "kept\n" and not (snaps[0] / "history").exists(), "history/ must stay out of the snapshot and survive the restore")
    ok(do_restore("guarded", "19990101-000000", cfg, home=tmp) == 1, "restore of a missing snapshot should refuse")
    away = tmp / "elsewhere" / "guarded"; (away / "references" / "history").mkdir(parents=True)
    (away / "SKILL.md").write_text("the copy\n"); (away / "references" / "history" / "evidence.md").write_text("evidence\n")
    ok(do_snapshot(str(away), cfg, home=tmp) == 0, "snapshot of a path did not return 0")
    stamp2 = sorted(snapshots_home(tmp).glob("guarded-*"))[-1].name.split("guarded-", 1)[1]
    (away / "SKILL.md").write_text("edited\n")
    ok(do_restore("guarded", stamp2, cfg, home=tmp) == 0 and (away / "SKILL.md").read_text() == "the copy\n", "a path snapshot must restore to its own folder")
    ok((guarded / "SKILL.md").read_text() == "original content\n", "restoring a path snapshot must not touch the skill of the same name")
    ok((away / "references" / "history" / "evidence.md").read_text() == "evidence\n" and not (away / SOURCE_NOTE).exists(), "a nested history folder is part of the snapshot and survives")
    blank = tmp / "fixture-blank.md"; blank.write_text("SKILL.md path: <path to the skill's SKILL.md>\n\nOne real test prompt:\n\n>\n")
    rep, _ = run_checks(str(clean), cfg, fixture=str(blank))
    ok(status(rep, 10) == ["FAIL"] and "unfilled" in detail(rep, 10) and "no prompt" in detail(rep, 10), detail(rep, 10))
    (clean / "references" / "lessons.md").write_text("")
    rep, _ = run_checks(str(clean), cfg)
    ok(status(rep, 7) == ["FAIL"] and "none yet" in detail(rep, 7), detail(rep, 7))
    (clean / "references" / "lessons.md").unlink()
    shutil.rmtree(tmp)
    print(f"SELFTEST PASS ({checks} assertions: dirty skill 5 FAILs with the folded description parsed · clean skill PASS, listed in the registry · fixture PASS/FAIL · pre-created log FAIL with a fixture, INFO without · no-trigger description + close line not last FAIL · close_line null SKIP · claude-in-name + angle-bracket/long description FAIL · no frontmatter FAIL + nested-skill close line SKIP · discovery SKIP on a path target · registry SKIP when null · workspace-rooted path resolves/fails · snapshot then restore returns a changed file to its snapshot content, and refuses a restore of a missing snapshot)")
    return 0

def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("target", nargs="?", help="the skill's bare name (via the configured skills home) or a folder path")
    p.add_argument("--fixture", help="the fixture file to check (paths only)"); p.add_argument("--json", action="store_true", help="print the rows as a JSON list")
    p.add_argument("--selftest", action="store_true")
    p.add_argument("--snapshot", metavar="NAME_OR_PATH", help="copy the skill folder to history/snapshots/ and print the restore command")
    p.add_argument("--restore", nargs=2, metavar=("NAME", "STAMP"), help="copy a snapshot back over the skill folder")
    a = p.parse_args()
    if a.selftest:
        buf = io.StringIO()            # the guard tests print as they run; only the verdict is shown
        with contextlib.redirect_stdout(buf):
            rc = selftest()
        print(buf.getvalue().strip().splitlines()[-1]); sys.exit(rc)
    cfg = load_config()
    if a.snapshot: sys.exit(do_snapshot(a.snapshot, cfg))
    if a.restore: sys.exit(do_restore(a.restore[0], a.restore[1], cfg))
    if not a.target: p.error("give a skill name or path, or --selftest, --snapshot, --restore")
    rep, name = run_checks(a.target, cfg, a.fixture)
    sys.exit(emit(rep, name, a.json))

if __name__ == "__main__":
    main()
