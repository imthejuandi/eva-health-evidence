#!/usr/bin/env python3
"""make-evidence.py: rebuild EVA's evidence record of the physician sign-off programme.

It reads the sources and writes only under the evidence folder (OUT). It never changes,
moves or deletes a source. It runs no test suite and no acceptance-test runner: it is a
record of what was run, not a re-run.

Sources (read only):
  1. the repository REPO (committed records, worktrees and branches, read through git);
  2. the session transcripts under SESSION_DIR (main conversation, subagents, workflows,
     tool-results);
  3. the scratch folder SCRATCH and the tasks folder TASKS;
  4. the cloud sessions this session started, found in the main transcript;
  5. the test fixtures left in /tmp/dsrt-* (listed, never copied).

Steps (all by default, or pick with --steps):
  snapshot     fix the byte size of every transcript file now; later steps read only that much
  index        parse every transcript into .work/index/*.jsonl (tool calls, texts, agents)
  transcripts  scrub and compress the transcripts into transcripts/*.tar.xz parts (<= 45 MB)
  scratch      scrub and compress the scratch folder's proof into scratch/*.tar.xz parts
  repo         hash the repository's proof paths; list worktrees, branches and sessions
  dsrt         list /tmp/dsrt-* folders into dsrt-fixtures.json and .md
  tests        TESTS-SUMMARY.md and tests.json
  deletions    DELETIONS.md
  manifest     manifest.json and MANIFEST.md
  readme       README.md

Usage:  python3 -I make-evidence.py [--steps a,b,c] [--keep-work]
Needs Python 3.8 or later, git and the standard library only.
"""
import argparse
import collections
import datetime as dt
import hashlib
import io
import json
import lzma
import os
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import time
from multiprocessing import Pool

# ----------------------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------------------
REPO = "/home/user/eva-health"
BRANCH = "claude/wonderful-meitner-l4g7p5"
SESSION_ID = "4e1a7523-c199-547a-904f-d87e53286958"
CLOUD_SESSION = "session_016mEXZE6RheLMXSZTgYDUrW"
PROJECT_DIR = "/root/.claude/projects/-home-user-eva-health"
SESSION_DIR = os.path.join(PROJECT_DIR, SESSION_ID)
MAIN_TRANSCRIPT = SESSION_DIR + ".jsonl"
TMP_ROOT = "/tmp/claude-0/-home-user-eva-health/" + SESSION_ID
SCRATCH = os.path.join(TMP_ROOT, "scratchpad")
TASKS = os.path.join(TMP_ROOT, "tasks")
OUT = os.path.join(SCRATCH, "evidence")
WORK = os.path.join(OUT, ".work")
IDX = os.path.join(WORK, "index")
DSRT_GLOB_DIR = "/tmp"
DSRT_PREFIX = "dsrt-"

# Scratch folders that hold tools and downloads, not proof (not archived, listed only).
SCRATCH_TOOLS = ["venv", "src", "dl"]
# Folders the orchestrator named as still being written when this record was first made.
# They are listed as in progress and never read. Anything else written in the last
# RECENT_MINUTES before the snapshot is treated the same way.
IN_PROGRESS = [
    "ws3-wave2/WS3-09-fix",
    "ws3-wave2/WS3-35-fix",
    "mopup-decisions/arbiter",
]
IN_PROGRESS_WORKTREES = ["ws3-e", "ws3-f"]
RECENT_MINUTES = 20

PART_LIMIT = 45_000_000      # bytes; every archive part stays at or under this
PART_TARGET = 42_000_000     # start a new part once the compressed size passes this
XZ_PRESET = 6
DISK_FLOOR = 5_000_000_000  # keep at least 5 GB (5,000,000,000 bytes) free on /

# The CEO's address is kept hex-encoded so that it never appears in plain text in the uploaded record.
CEO_EMAIL = bytes.fromhex("6a75616e6c61676f393640676d61696c2e636f6d").decode()
CEO_TOKEN = "[CEO email]"
SECRET_TOKEN = "[redacted secret]"

# Repository paths that hold committed proof (the manifest hashes every tracked file in them).
REPO_PROOF_PATHS = [
    "docs/signoff",
    "docs/biomarker-evidence",
    "docs/audit",
    "audit",
    "ml/biological-age",
    "docs/biomarker-optimal-ranges-sources.md",
    "docs/biological-age-plan.md",
    "docs/integration-readiness-audit.md",
    "docs/pre-launch-checklist.md",
    "supabase/seed-data",
    "supabase/migrations",
    "scripts",
    "src/lib/signoff",
]


# ----------------------------------------------------------------------------------------
# Small helpers
# ----------------------------------------------------------------------------------------
def now_utc():
    return dt.datetime.now(dt.timezone.utc)


def iso(ts=None):
    return (ts or now_utc()).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def ensure_dir(p):
    assert os.path.abspath(p).startswith(OUT), "refusing to write outside the evidence folder: " + p
    os.makedirs(p, exist_ok=True)


RECORD_REDACTIONS = collections.Counter()


def write_text(path, text, scrubbed=True):
    """Write a file of the record. Its text goes through the same scrubber as the archives, because the record
    quotes commands, outputs and reports from the transcripts. Files under .work are not scrubbed (never uploaded)."""
    assert os.path.abspath(path).startswith(OUT), "refusing to write outside the evidence folder: " + path
    ensure_dir(os.path.dirname(path))
    data = text.encode("utf-8")
    if scrubbed and not os.path.abspath(path).startswith(WORK):
        data, counts = scrub(data)
        if counts:
            RECORD_REDACTIONS.update({(os.path.relpath(path, OUT), k): v for k, v in counts.items()})
            _note_record_redactions(os.path.relpath(path, OUT), counts)
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, path)


def _note_record_redactions(name, counts):
    p = os.path.join(WORK, "redactions-record.json")
    try:
        cur = json.load(open(p))
    except Exception:
        cur = {}
    cur[name] = dict(counts)
    os.makedirs(WORK, exist_ok=True)
    with open(p, "w") as f:
        json.dump(cur, f)


def write_json(path, obj):
    write_text(path, json.dumps(obj, indent=1, ensure_ascii=False) + "\n")


def read_jsonl(path):
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                out.append(json.loads(line))
    return out


def sha256_file(path, limit=None):
    h = hashlib.sha256()
    n = 0
    with open(path, "rb") as f:
        while True:
            want = 1 << 20
            if limit is not None:
                want = min(want, limit - n)
                if want <= 0:
                    break
            b = f.read(want)
            if not b:
                break
            h.update(b)
            n += len(b)
    return h.hexdigest()


def free_bytes(path="/"):
    st = os.statvfs(path)
    return st.f_bavail * st.f_frsize


def check_disk(what):
    fb = free_bytes("/")
    log(f"disk free on / {fb / 1024 ** 3:.2f} GiB ({what})")
    if fb < DISK_FLOOR:
        raise SystemExit(f"stopping: less than 5 GB free on / ({fb / 1e9:.2f} GB) during {what}")
    return fb


def git(*args, cwd=REPO, check=True):
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_PAGER="cat", LC_ALL="C")
    r = subprocess.run(["git", "--no-optional-locks"] + list(args), cwd=cwd, env=env,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and r.returncode != 0:
        raise RuntimeError("git " + " ".join(args) + ": " + r.stderr.decode(errors="replace")[:500])
    return r.stdout.decode("utf-8", errors="replace")


def human(n):
    for unit in ("B", "KB", "MB", "GB"):
        if abs(n) < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024.0
    return str(n)


def md_escape(s):
    return (s or "").replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def rel_session(path):
    """Name of a transcript file as the record uses it."""
    if path == MAIN_TRANSCRIPT:
        return "main.jsonl"
    return os.path.relpath(path, SESSION_DIR)


def parse_ts(s):
    if not s:
        return None
    try:
        return dt.datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=dt.timezone.utc)
    except Exception:
        return None


# ----------------------------------------------------------------------------------------
# Step: snapshot
# ----------------------------------------------------------------------------------------
def transcript_files():
    files = [MAIN_TRANSCRIPT]
    for root, dirs, fs in os.walk(SESSION_DIR):
        dirs.sort()
        for f in sorted(fs):
            files.append(os.path.join(root, f))
    return files


def step_snapshot():
    """Fix the size of every transcript file. Files are append-only, so reading up to the
    recorded size (cut at the last complete line for .jsonl) gives one consistent snapshot."""
    ensure_dir(WORK)
    snap = {"taken_at": iso(), "files": []}
    for p in transcript_files():
        try:
            st = os.lstat(p)
        except FileNotFoundError:
            continue
        if not stat.S_ISREG(st.st_mode):
            continue
        size = st.st_size
        if p.endswith(".jsonl") and size:
            # cut at the last newline so a line being written is left for the next refresh
            with open(p, "rb") as f:
                back = min(size, 4 << 20)
                f.seek(size - back)
                tail = f.read(back)
            k = tail.rfind(b"\n")
            size = size - back + k + 1 if k >= 0 else 0
        snap["files"].append({"path": p, "name": rel_session(p), "size": size,
                              "mtime": iso(dt.datetime.fromtimestamp(st.st_mtime, dt.timezone.utc))})
    write_json(os.path.join(WORK, "snapshot.json"), snap)
    log(f"snapshot: {len(snap['files'])} transcript files, {sum(f['size'] for f in snap['files']) / 1e6:.0f} MB")
    return snap


def load_snapshot():
    p = os.path.join(WORK, "snapshot.json")
    if not os.path.exists(p):
        return step_snapshot()
    return json.load(open(p))


def read_snapshot_bytes(entry):
    with open(entry["path"], "rb") as f:
        return f.read(entry["size"])


# ----------------------------------------------------------------------------------------
# Step: index (parse transcripts)
# ----------------------------------------------------------------------------------------
HEREDOC_RE = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")


def strip_heredocs(cmd):
    """Remove here-document bodies, so a script being written is not taken for a run."""
    out_lines = []
    lines = cmd.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        out_lines.append(line)
        delims = [m.group(2) for m in HEREDOC_RE.finditer(line)]
        i += 1
        for d in delims:
            while i < len(lines) and lines[i].strip() != d:
                i += 1
            i += 1  # skip the delimiter line
    return "\n".join(out_lines)


def strip_inline_code(cmd):
    """Remove python -c / node -e bodies that are quoted, so parsing helpers are not runs."""
    cmd = re.sub(r"(python3?\s+(?:-I\s+)?-c\s+)\"(?:[^\"\\]|\\.)*\"", r"\1\"…\"", cmd, flags=re.S)
    cmd = re.sub(r"(python3?\s+(?:-I\s+)?-c\s+)'[^']*'", r"\1'…'", cmd, flags=re.S)
    cmd = re.sub(r"(node\s+(?:--input-type=module\s+)?-e\s+)\"(?:[^\"\\]|\\.)*\"", r"\1\"…\"", cmd, flags=re.S)
    cmd = re.sub(r"(node\s+(?:--input-type=module\s+)?-e\s+)'[^']*'", r"\1'…'", cmd, flags=re.S)
    return cmd


B = r"(?:^|[;&|(`\n]|\bthen\b|\bdo\b|\belse\b|\btimeout\s+\S+|\benv\b|[A-Z_][A-Z0-9_]*=\S*|\bnice\b|\btime\b)\s*"
KINDS = [
    ("vitest", re.compile(B + r"(?:npx\s+(?:--\S+\s+)*vitest\b(?!\.config)|\S*node_modules/\.bin/vitest\b|vitest\s+(?:run|--run)\b|npm\s+(?:run\s+)?test\b|npm\s+t\b)", re.M)),
    ("typecheck", re.compile(B + r"(?:npx\s+(?:--\S+\s+)*tsc\b|\S*node_modules/\.bin/tsc\b|tsc\s+(?:--noEmit|-p|--project|-b)\b|npm\s+run\s+typecheck\b)", re.M)),
    ("lint", re.compile(B + r"(?:npx\s+(?:--\S+\s+)*eslint\b|\S*node_modules/\.bin/eslint\b|npm\s+run\s+lint\b)", re.M)),
    ("node-test", re.compile(B + r"node\s+(?:--\S+\s+)*--test\b", re.M)),
    ("dsrt", re.compile(r"(?:\b(?:tsx|node|ts-node|bun)\s+(?:--\S+\s+)*\S*scripts/signoff/dsrt\.ts|npm\s+run\s+dsrt\b)")),
    ("build", re.compile(B + r"(?:npx\s+next\s+build\b|next\s+build\b|npm\s+run\s+build\b)", re.M)),
    ("signoff-tool", re.compile(r"\bnode\s+(?:--\S+\s+)*\S*?\b(compile|validate|quote-check|ledger|ownership|scorecard|build-briefs|build-inputs)\.js\b")),
    ("pytest", re.compile(r"\bpytest\b|python3?\s+(?:-\S+\s+)*-m\s+pytest\b")),
    ("probe", re.compile(r"\b(?:node|tsx|npx\s+tsx|python3?|bash|sh|deno|bun)\s+(?:-\S+\s+)*\S*[Pp]robe\S*\.(?:m?[jt]s|cjs|mts|py|sh)\b")),
    ("mutation", re.compile(r"\b(?:node|tsx|npx\s+tsx|python3?|bash|sh)\s+(?:-\S+\s+)*\S*(?:[Mm]utat|[Mm]utant)\S*\.(?:m?[jt]s|cjs|mts|py|sh)\b")),
    ("tsx-script", re.compile(r"\b(?:npx\s+)?tsx\s+(?:--\S+\s+)*(?!scripts/signoff/dsrt\.ts)\S+\.(?:m?ts|tsx)\b")),
    ("python-script", re.compile(r"\bpython3?\s+(?:-[IuOB]+\s+)*(?!-c\b|-m\b)\S+\.py\b")),
    ("node-script", re.compile(r"\bnode\s+(?:--\S+\s+)*(?!-e\b|--test\b)\S+\.(?:m?js|cjs)\b")),
]
# A python, node or tsx script counts as a check when its name says so, or when it lives in the repository's
# audit, calibration or verification folders.
CHECKY = re.compile(r"(audit|calib|check|verif|valid|test|probe|mutat|mutant|reproduc|replica|compare|cmp|parity|diff|regress|sensitiv|holdout|harness|recheck|smoke|assert|lint|gate|selftest|self-test|fixture|scan|count)", re.I)
REPO_SCRIPT = re.compile(r"(ml/biological-age/|scripts/[^ ]+\.(py|ts)|audit/|docs/signoff/tools/|docs/biomarker-evidence/)")


QUOTED_RE = re.compile(r'"(?:[^"\\\n]|\\.)*"|\'[^\'\n]*\'')
NOT_RUN_CMD = re.compile(r"(?:^|[;&|(\n`])\s*(?:[A-Za-z_]\w*=\S*\s+)*(?:grep|egrep|fgrep|rg|sed|awk|echo|printf|git\s+(?:commit|merge|tag|log|grep|show))\b[^;&|\n]*$")


def strip_not_runs(body):
    """Blank commit messages and the quoted arguments of grep, sed, awk, echo and printf: text, not runs."""
    body = re.sub(r'(\s-m\s+)"(?:[^"\\]|\\.)*"', r'\1""', body, flags=re.S)
    def rep(m):
        before = body[max(0, m.start() - 400):m.start()]
        return '""' if NOT_RUN_CMD.search(before) else m.group(0)
    return QUOTED_RE.sub(rep, body)


def classify_command(cmd, desc=""):
    """Return the list of check kinds a shell command runs (empty for none)."""
    body = strip_not_runs(strip_inline_code(strip_heredocs(cmd)))
    kinds = []
    for name, rx in KINDS:
        for m in rx.finditer(body):
            if name in ("tsx-script", "python-script", "node-script"):
                frag = m.group(0)
                if not (CHECKY.search(frag) or REPO_SCRIPT.search(frag)):
                    continue
                if name == "node-script" and re.search(r"\b(compile|validate|quote-check|ledger|ownership|scorecard|build-briefs|build-inputs)\.js\b", frag):
                    continue
                if name == "node-script" and re.search(r"probe|mutat|mutant", frag, re.I):
                    continue
            if name not in kinds:
                kinds.append(name)
            break
    if desc and re.search(r"mutat|mutant", desc, re.I) and any(k in kinds for k in ("vitest", "node-test", "node-script", "tsx-script")) and "mutation" not in kinds:
        kinds.append("mutation")
    if desc and re.search(r"\bprobe", desc, re.I) and any(k in kinds for k in ("vitest", "node-test", "node-script", "tsx-script", "python-script")) and "probe" not in kinds:
        kinds.append("probe")
    return kinds


def result_text(content):
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    parts = []
    if isinstance(content, list):
        for x in content:
            if isinstance(x, dict):
                if x.get("type") == "text":
                    parts.append(x.get("text", ""))
                elif x.get("type") == "image":
                    parts.append("[image]")
                elif x.get("type") == "tool_reference":
                    parts.append("[tool reference " + str(x.get("tool_name", "")) + "]")
                else:
                    parts.append(json.dumps(x)[:2000])
            else:
                parts.append(str(x))
    return "\n".join(parts)


PERSISTED_RE = re.compile(r"Full output saved to: (\S+)")


def full_result(text, persisted_path):
    """If the output was too large for the transcript, the full text is in tool-results/."""
    p = persisted_path
    if not p:
        m = PERSISTED_RE.search(text[:3000])
        if m:
            p = m.group(1)
    if p and p.startswith(SESSION_DIR) and os.path.exists(p):
        try:
            with open(p, encoding="utf-8", errors="replace") as f:
                return f.read(), os.path.relpath(p, SESSION_DIR)
        except Exception:
            pass
    return text, (os.path.relpath(p, SESSION_DIR) if p and p.startswith(SESSION_DIR) else p)


def clip(s, head=3000, tail=3000):
    if len(s) <= head + tail + 50:
        return s
    return s[:head] + f"\n…[{len(s) - head - tail} characters left out of this index; the transcript has them all]…\n" + s[-tail:]


def text_blocks(content):
    if isinstance(content, str):
        return [content]
    out = []
    if isinstance(content, list):
        for x in content:
            if isinstance(x, dict) and x.get("type") == "text":
                out.append(x.get("text", ""))
    return out


def index_one(entry):
    """Parse one transcript file (up to its snapshot size). Returns records for the index."""
    path, name = entry["path"], entry["name"]
    calls, texts = [], []
    pending = {}
    agent = {"f": name, "lines": 0, "first_ts": None, "last_ts": None, "final_text": None,
             "final_ts": None, "final_ln": None, "structured": [], "handback": None,
             "agentIds": set(), "cwds": collections.Counter(), "models": collections.Counter(),
             "n_calls": 0, "n_checks": 0, "prompt": None}
    data = read_snapshot_bytes(entry)
    is_main = path == MAIN_TRANSCRIPT
    for ln, raw in enumerate(data.split(b"\n"), 1):
        if not raw.strip():
            continue
        try:
            o = json.loads(raw)
        except Exception:
            continue
        agent["lines"] = ln
        ts = o.get("timestamp")
        if ts:
            agent["first_ts"] = agent["first_ts"] or ts
            agent["last_ts"] = ts
        if o.get("agentId"):
            agent["agentIds"].add(o["agentId"])
        if o.get("cwd"):
            agent["cwds"][o["cwd"]] += 1
        typ = o.get("type")
        msg = o.get("message") if isinstance(o.get("message"), dict) else None
        if typ == "assistant" and msg:
            if msg.get("model"):
                agent["models"][msg["model"]] += 1
            content = msg.get("content")
            if isinstance(content, list):
                for p in content:
                    if not isinstance(p, dict):
                        continue
                    if p.get("type") == "text" and p.get("text", "").strip():
                        agent["final_text"] = p["text"]
                        agent["final_ts"] = ts
                        agent["final_ln"] = ln
                        if is_main:
                            texts.append({"f": name, "ln": ln, "ts": ts, "role": "assistant",
                                          "uuid": o.get("uuid"), "side": o.get("isSidechain"),
                                          "text": p["text"]})
                    elif p.get("type") == "tool_use":
                        inp = p.get("input") or {}
                        tool = p.get("name")
                        rec = {"f": name, "ln": ln, "ts": ts, "cwd": o.get("cwd"), "br": o.get("gitBranch"),
                               "agent": o.get("agentId"), "id": p.get("id"), "tool": tool}
                        if tool == "Bash":
                            rec["cmd"] = inp.get("command", "")
                            rec["desc"] = inp.get("description", "")
                            rec["bg"] = bool(inp.get("run_in_background"))
                            rec["kinds"] = classify_command(rec["cmd"], rec["desc"])
                        else:
                            s = json.dumps(inp, ensure_ascii=False)
                            rec["inp"] = s if len(s) <= 20000 else s[:20000] + "…"
                            rec["kinds"] = []
                        if tool == "StructuredOutput":
                            agent["structured"].append({"ln": ln, "ts": ts, "input": inp})
                        if tool == "SubagentHandback":
                            agent["handback"] = {"ln": ln, "ts": ts, "message": inp.get("message", "")}
                        agent["n_calls"] += 1
                        pending[p.get("id")] = rec
        elif typ == "user" and msg:
            content = msg.get("content")
            tur = o.get("toolUseResult") if isinstance(o.get("toolUseResult"), dict) else {}
            if isinstance(content, list):
                for p in content:
                    if isinstance(p, dict) and p.get("type") == "tool_result":
                        rec = pending.pop(p.get("tool_use_id"), None)
                        if rec is None:
                            continue
                        text = result_text(p.get("content"))
                        full, ppath = full_result(text, tur.get("persistedOutputPath"))
                        rec["rln"] = ln
                        rec["rts"] = ts
                        rec["err"] = bool(p.get("is_error"))
                        rec["rlen"] = len(full)
                        if ppath:
                            rec["persisted"] = ppath
                        if rec.get("kinds"):
                            agent["n_checks"] += 1
                            rec["res"] = full if len(full) <= 400_000 else clip(full, 200_000, 200_000)
                        elif rec["tool"] in ("Agent", "Task", "Workflow", "mcp__Claude_Code_Remote__create_session",
                                             "mcp__Claude_Code_Remote__get_session", "mcp__Claude_Code_Remote__list_sessions",
                                             "SendMessage", "TaskOutput", "StructuredOutput", "SubagentHandback"):
                            rec["res"] = full if len(full) <= 100_000 else clip(full, 50_000, 50_000)
                        else:
                            rec["res"] = clip(full, 4000, 4000)
                        calls.append(rec)
            if is_main and not o.get("isMeta") and not o.get("isCompactSummary"):
                blocks = text_blocks(content)
                if blocks and not (isinstance(content, list) and any(isinstance(x, dict) and x.get("type") == "tool_result" for x in content)):
                    t = "\n".join(blocks)
                    if t.strip():
                        texts.append({"f": name, "ln": ln, "ts": ts, "role": "user", "uuid": o.get("uuid"),
                                      "side": o.get("isSidechain"), "text": t})
            if is_main and o.get("isCompactSummary"):
                texts.append({"f": name, "ln": ln, "ts": ts, "role": "summary", "uuid": o.get("uuid"),
                              "side": False, "text": "\n".join(text_blocks(content))})
            if agent["prompt"] is None and not is_main:
                b = text_blocks(content)
                if b:
                    agent["prompt"] = "\n".join(b)[:4000]
        elif typ == "queue-operation" and is_main and o.get("content"):
            c = o.get("content")
            if isinstance(c, str) and "<task-notification>" in c:
                texts.append({"f": name, "ln": ln, "ts": ts, "role": "notification", "uuid": None, "side": False,
                              "text": c[:20000]})
    # tool calls that never got a result (still running, or cut off)
    for rec in pending.values():
        rec["rln"] = None
        rec["res"] = ""
        rec["rlen"] = 0
        rec["err"] = None
        rec["no_result"] = True
        calls.append(rec)
    agent["agentIds"] = sorted(agent["agentIds"])
    agent["cwds"] = agent["cwds"].most_common(3)
    agent["models"] = agent["models"].most_common(3)
    if agent["final_text"] and len(agent["final_text"]) > 60000:
        agent["final_text"] = agent["final_text"][:60000] + "…"
    return name, calls, texts, agent


def step_index():
    snap = load_snapshot()
    ensure_dir(IDX)
    entries = [e for e in snap["files"] if e["path"].endswith(".jsonl")]
    entries.sort(key=lambda e: -e["size"])
    t0 = time.time()
    n_calls = 0
    with open(os.path.join(IDX, "calls.jsonl.tmp"), "w", encoding="utf-8") as fc, \
            open(os.path.join(IDX, "texts.jsonl.tmp"), "w", encoding="utf-8") as ft, \
            open(os.path.join(IDX, "agents.jsonl.tmp"), "w", encoding="utf-8") as fa:
        with Pool(2) as pool:
            for name, calls, texts, agent in pool.imap_unordered(index_one, entries, chunksize=4):
                for c in calls:
                    fc.write(json.dumps(c, ensure_ascii=False) + "\n")
                for t in texts:
                    ft.write(json.dumps(t, ensure_ascii=False) + "\n")
                fa.write(json.dumps(agent, ensure_ascii=False) + "\n")
                n_calls += len(calls)
    for n in ("calls", "texts", "agents"):
        os.replace(os.path.join(IDX, n + ".jsonl.tmp"), os.path.join(IDX, n + ".jsonl"))
    log(f"index: {len(entries)} transcripts, {n_calls} tool calls, {time.time() - t0:.0f} s")


# ----------------------------------------------------------------------------------------
# Scrubbing: the CEO's email and anything that looks like a secret
# ----------------------------------------------------------------------------------------
PLACEHOLDER = re.compile(rb"(?i)placeholder|example|dummy|changeme|change-me|xxxx|your[-_]|<|\$\{|\$[A-Z]|process\.env|import\.meta|os\.environ|getenv|redacted|\*\*\*")
NOT_ALNUM = rb"(?<![A-Za-z0-9+/_-])"
# (kind, pattern, group to replace or 0 for the whole match, needs a value check)
SECRET_RULES = [
    ("CEO email", re.compile(rb"(?i)" + re.escape(CEO_EMAIL.split("@")[0].encode()) + rb"(?:@|%40|\\u0040|&#64;|&#x40;)" + re.escape(CEO_EMAIL.split("@")[1].encode())), 0, False),
    ("private key", re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S), 0, False),
    ("JWT", re.compile(NOT_ALNUM + rb"eyJ[A-Za-z0-9_-]{8,}\.eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}"), 0, False),
    ("Anthropic API key", re.compile(NOT_ALNUM + rb"sk-ant-[A-Za-z0-9_-]{20,}"), 0, False),
    ("OpenAI-style API key", re.compile(rb"(?<![A-Za-z0-9+/_:-])sk-(?!ant-)(?:proj-|svcacct-)?[A-Za-z0-9_-]{32,}"), 0, False),
    ("Stripe key", re.compile(NOT_ALNUM + rb"(?:sk|rk|pk)_(?:live|test)_[A-Za-z0-9]{16,}"), 0, False),
    ("Stripe webhook secret", re.compile(NOT_ALNUM + rb"whsec_[A-Za-z0-9]{16,}"), 0, False),
    ("GitHub token", re.compile(NOT_ALNUM + rb"(?:(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})"), 0, False),
    ("Google API key", re.compile(NOT_ALNUM + rb"AIza[0-9A-Za-z_-]{35}(?![A-Za-z0-9_-])"), 0, False),
    ("Google OAuth token", re.compile(NOT_ALNUM + rb"ya29\.[0-9A-Za-z_-]{20,}"), 0, False),
    ("AWS access key", re.compile(rb"(?<![A-Z0-9])(?:AKIA|ASIA)[0-9A-Z]{16}(?![A-Z0-9])"), 0, False),
    ("Slack token", re.compile(NOT_ALNUM + rb"xox[abposr]-[A-Za-z0-9-]{10,}"), 0, False),
    ("Supabase token", re.compile(NOT_ALNUM + rb"(?:sbp_[A-Za-z0-9]{20,}|sb_(?:secret|publishable)_[A-Za-z0-9_-]{16,})"), 0, False),
    ("Resend API key", re.compile(NOT_ALNUM + rb"re_[A-Za-z0-9]{8,}_[A-Za-z0-9]{12,}"), 0, False),
    ("npm token", re.compile(NOT_ALNUM + rb"npm_[A-Za-z0-9]{36}"), 0, False),
    ("Hugging Face token", re.compile(NOT_ALNUM + rb"hf_[A-Za-z0-9]{30,}"), 0, False),
    ("Perplexity API key", re.compile(NOT_ALNUM + rb"pplx-[A-Za-z0-9]{30,}"), 0, False),
    ("Sentry DSN", re.compile(rb"https://[0-9a-f]{32}@[a-z0-9.-]*sentry\.io/\d+"), 0, False),
    ("connection string", re.compile(rb"(?i)\b(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|rediss?|amqps?|mssql)://[^\s\"'<>/:@\\]+:[^\s\"'<>@\\]+@[^\s\"'<>\\]+"), 0, False),
    ("URL with a password", re.compile(rb"(?i)\bhttps?://[^\s\"'/:@\\]+:([^\s\"'@/\\]{8,})@"), 1, True),
    ("Authorization header", re.compile(rb"(?i)(?:authorization|proxy-authorization)[\"']?\s*[:=]\s*[\"']?(?:bearer|basic|token)\s+([A-Za-z0-9._~+/=-]{12,})"), 1, True),
    ("API key header", re.compile(rb"(?i)(?:x-api-key|apikey|x-auth-token|api-key)[\"']?\s*[:=]\s*[\"']?([A-Za-z0-9._~+/=-]{16,})"), 1, True),
    ("secret in a variable", re.compile(rb"(?<![A-Za-z0-9_])[A-Z][A-Z0-9_]*(?:KEY|TOKEN|SECRET|PASSWORD|PASSWD|PWD)\s*=\s*[\"']?([A-Za-z0-9._~+/=:-]{16,})"), 1, True),
    ("password", re.compile(rb"(?i)[\"']?(?:password|passwd|client_secret|service_role_key|access_token|refresh_token|api_key|secret_key)[\"']?\s*[:=]\s*[\"']([^\"'\s\\]{8,})[\"']"), 1, True),
]


def looks_secret(value):
    """For the context rules: a real credential has letters and digits and is not a placeholder."""
    if PLACEHOLDER.search(value):
        return False
    if not re.search(rb"[A-Za-z]", value) or not re.search(rb"[0-9]", value):
        return False
    if re.fullmatch(rb"[a-z_]+[0-9]?", value):
        return False
    return True


def scrub(data):
    """Return (scrubbed bytes, Counter of kind -> count)."""
    counts = collections.Counter()
    for kind, rx, grp, check in SECRET_RULES:
        if kind == "CEO email":
            if CEO_EMAIL.split("@")[0].encode() not in data.lower():
                continue
        def rep(m, kind=kind, grp=grp, check=check):
            if grp:
                val = m.group(grp)
                if check and not looks_secret(val):
                    return m.group(0)
                counts[kind] += 1
                s, e = m.span(grp)
                o = m.start()
                whole = m.group(0)
                return whole[:s - o] + SECRET_TOKEN.encode() + whole[e - o:]
            counts[kind] += 1
            return (CEO_TOKEN if kind == "CEO email" else SECRET_TOKEN).encode()
        data = rx.sub(rep, data)
    return data, counts


# ----------------------------------------------------------------------------------------
# Archive writer: self-contained .tar.xz parts of at most PART_LIMIT bytes
# ----------------------------------------------------------------------------------------
BINARY_EXT = {".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".zip", ".gz", ".xz", ".bz2", ".7z",
              ".rda", ".rds", ".xpt", ".parquet", ".sqlite", ".db", ".bin", ".woff", ".woff2", ".ico", ".npy", ".npz", ".pkl"}


class _XZSink:
    def __init__(self, path):
        self.f = open(path, "wb")
        self.c = lzma.LZMACompressor(format=lzma.FORMAT_XZ, check=lzma.CHECK_CRC64, preset=XZ_PRESET)
        self.raw = 0

    def write(self, b):
        self.raw += len(b)
        out = self.c.compress(b)
        if out:
            self.f.write(out)
        return len(b)

    def written(self):
        return self.f.tell()

    def close(self):
        self.f.write(self.c.flush())
        self.f.close()


class PartWriter:
    """Writes members into numbered, self-contained .tar.xz parts. A part is closed before a member
    whose conservative compressed estimate would take it past PART_TARGET."""

    def __init__(self, folder, stem):
        ensure_dir(folder)
        self.folder, self.stem = folder, stem
        self.parts = []
        self.sink = None
        self.tar = None
        self.members = []

    def _open(self):
        n = len(self.parts) + 1
        name = f"{self.stem}.part{n:02d}.tar.xz"
        self.cur_name = name
        self.sink = _XZSink(os.path.join(self.folder, name))
        self.tar = tarfile.open(fileobj=self.sink, mode="w|", format=tarfile.PAX_FORMAT)
        self.members = []

    def _close(self):
        if not self.tar:
            return
        self.tar.close()
        raw = self.sink.raw
        self.sink.close()
        path = os.path.join(self.folder, self.cur_name)
        size = os.path.getsize(path)
        if size > PART_LIMIT:
            raise SystemExit(f"part {self.cur_name} is {size} bytes, over the {PART_LIMIT} limit: lower PART_TARGET")
        self.parts.append({"name": self.cur_name, "size": size, "sha256": sha256_file(path),
                           "members": len(self.members), "uncompressed_tar_bytes": raw,
                           "first": self.members[0] if self.members else None,
                           "last": self.members[-1] if self.members else None})
        log(f"  closed {self.cur_name}: {size / 1e6:.1f} MB, {len(self.members)} members")
        self.tar = None
        self.sink = None
        check_disk("compression")

    @staticmethod
    def estimate(name, size):
        ext = os.path.splitext(name)[1].lower()
        return size if ext in BINARY_EXT else size / 3.0

    def add_bytes(self, arcname, data, mtime, mode=0o644):
        est = self.estimate(arcname, len(data)) + 600
        if self.tar and self.members and self.sink.written() + 1_000_000 + est > PART_TARGET:
            self._close()
        if not self.tar:
            self._open()
        ti = tarfile.TarInfo(arcname)
        ti.size = len(data)
        ti.mtime = int(mtime)
        ti.mode = mode & 0o7777
        ti.uid = ti.gid = 0
        ti.uname = ti.gname = "root"
        self.tar.addfile(ti, io.BytesIO(data))
        self.members.append(arcname)

    def add_symlink(self, arcname, target, mtime):
        if not self.tar:
            self._open()
        ti = tarfile.TarInfo(arcname)
        ti.type = tarfile.SYMTYPE
        ti.linkname = target
        ti.mtime = int(mtime)
        ti.mode = 0o777
        ti.uid = ti.gid = 0
        ti.uname = ti.gname = "root"
        self.tar.addfile(ti)
        self.members.append(arcname)

    def finish(self):
        self._close()
        return self.parts


def verify_parts(folder, parts):
    """Read every part back: the xz stream and the tar index must be whole."""
    for p in parts:
        path = os.path.join(folder, p["name"])
        n = 0
        with tarfile.open(path, mode="r:xz") as t:
            for _ in t:
                n += 1
        p["verified_members"] = n
        if n != p["members"]:
            raise SystemExit(f"{p['name']}: {n} members read back, {p['members']} written")


def write_sums(folder, parts, title):
    lines = [f"{p['sha256']}  {p['name']}" for p in parts]
    write_text(os.path.join(folder, "SHA256SUMS"), "\n".join(lines) + "\n")


def jsonl_still_valid(before, after):
    """Count .jsonl lines that parsed before scrubbing and do not after (should be 0)."""
    if before == after:
        return 0
    bad = 0
    for a, b in zip(before.split(b"\n"), after.split(b"\n")):
        if a != b:
            try:
                json.loads(a)
            except Exception:
                continue
            try:
                json.loads(b)
            except Exception:
                bad += 1
    return bad


def step_transcripts():
    """Scrub and compress every transcript file of the snapshot. Nothing uncompressed is written."""
    snap = load_snapshot()
    folder = os.path.join(OUT, "transcripts")
    if os.path.isdir(folder):
        for f in os.listdir(folder):
            if f.endswith(".tar.xz") or f in ("SHA256SUMS", "parts.json"):
                os.remove(os.path.join(folder, f))
    ensure_dir(folder)
    order = sorted(snap["files"], key=lambda e: (0 if e["name"] == "main.jsonl" else
                                                1 if e["name"].startswith("subagents/") and "/workflows/" not in e["name"] else
                                                2 if e["name"].startswith("subagents/workflows/") else
                                                3 if e["name"].startswith("workflows/") else
                                                4 if e["name"].startswith("tool-results/") else 5, e["name"]))
    pw = PartWriter(folder, "transcripts")
    red = []
    members = []
    t0 = time.time()
    for e in order:
        raw = read_snapshot_bytes(e)
        clean, counts = scrub(raw)
        bad = jsonl_still_valid(raw, clean) if e["name"].endswith(".jsonl") and counts else 0
        arc = (SESSION_ID + ".jsonl") if e["name"] == "main.jsonl" else (SESSION_ID + "/" + e["name"])
        mtime = parse_ts(e["mtime"]).timestamp() if parse_ts(e["mtime"]) else time.time()
        pw.add_bytes(arc, clean, mtime)
        members.append({"name": e["name"], "arcname": arc, "part": pw.cur_name, "snapshot_bytes": len(raw),
                        "archived_bytes": len(clean), "sha256_archived": hashlib.sha256(clean).hexdigest(),
                        "sha256_snapshot": hashlib.sha256(raw).hexdigest(), "mtime": e["mtime"]})
        if counts:
            red.append({"archive": "transcripts", "file": arc, "counts": dict(counts), "broken_json_lines": bad})
    parts = pw.finish()
    verify_parts(folder, parts)
    write_sums(folder, parts, "transcripts")
    write_json(os.path.join(folder, "parts.json"), {"made_at": iso(), "snapshot_taken_at": snap["taken_at"],
                                                    "parts": parts, "members": members})
    write_json(os.path.join(WORK, "redactions-transcripts.json"), red)
    log(f"transcripts: {len(members)} files in {len(parts)} parts, {time.time() - t0:.0f} s")
    write_redactions()


# ----------------------------------------------------------------------------------------
# Repository copies in the scratch folder (made with git archive): store only what differs
# ----------------------------------------------------------------------------------------
ARCHIVE_RE = re.compile(r"git\s+(?:-C\s+(\S+)\s+)?archive\s+(?:--format=tar\s+)?(?:--prefix=\S+\s+)?([^\s|;&]+)[^|\n;]*\|\s*tar\s+(?:-?x\S*)\s+(?:-f\s*-\s+)?-C\s+(\S+)")
ASSIGN_RE = re.compile(r"(?:^|[\s;&(])([A-Za-z_][A-Za-z0-9_]*)=(\"[^\"]*\"|'[^']*'|[^\s;&|()]+)")


def expand_vars(s, env):
    def rep(m):
        k = m.group(1) or m.group(2)
        return env.get(k, m.group(0))
    for _ in range(3):
        s2 = re.sub(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)", rep, s)
        if s2 == s:
            break
        s = s2
    return s


def shell_env(cmd, upto=None):
    env = {}
    for m in ASSIGN_RE.finditer(cmd if upto is None else cmd[:upto]):
        v = m.group(2)
        if v[:1] in "\"'":
            v = v[1:-1]
        env[m.group(1)] = expand_vars(v, env)
    return env


def git_blob_sha(path):
    with open(path, "rb") as f:
        data = f.read()
    h = hashlib.sha1(b"blob %d\0" % len(data))
    h.update(data)
    return h.hexdigest()


def find_repo_copies():
    """Folders under SCRATCH made with `git archive REV | tar -x -C DIR`, latest creation per folder."""
    copies = {}
    for c in read_jsonl(os.path.join(IDX, "calls.jsonl")):
        cmd = c.get("cmd")
        if not cmd or "archive" not in cmd:
            continue
        for m in ARCHIVE_RE.finditer(cmd):
            env = shell_env(cmd, m.start())
            d = expand_vars(m.group(3), env).rstrip("/")
            rev = expand_vars(m.group(2), env)
            gitdir = expand_vars(m.group(1), env) if m.group(1) else None
            if not d.startswith("/"):
                continue
            d = os.path.normpath(d)
            if not d.startswith(SCRATCH + "/"):
                continue
            prev = copies.get(d)
            if prev is None or (c["ts"] or "") > (prev["ts"] or ""):
                copies[d] = {"dir": d, "rev": rev, "ts": c["ts"], "f": c["f"], "ln": c["ln"], "id": c["id"],
                             "cwd": c.get("cwd"), "gitdir": gitdir}
    return copies


def resolve_rev(rev, cwd, ts):
    """A commit id for REV as it stood at time TS in the checkout CWD."""
    if re.fullmatch(r"[0-9a-f]{7,40}", rev or ""):
        r = git("rev-parse", "--verify", "--quiet", rev + "^{commit}", check=False).strip()
        if r:
            return r
    if rev in ("HEAD", "@") or rev:
        h = head_at(cwd or REPO, None, ts) if rev in ("HEAD", "@") else None
        if h:
            return h
        r = git("rev-parse", "--verify", "--quiet", rev + "^{commit}", check=False).strip()
        if r and rev not in ("HEAD", "@"):
            return r
    return None


def copy_plan(copies):
    """For each copy, the files identical to the commit (not stored) and the rest (stored)."""
    plans = {}
    for d, info in copies.items():
        if not os.path.isdir(d):
            continue
        commit = resolve_rev(info["rev"], info.get("gitdir") or info.get("cwd"), info["ts"])
        if not commit:
            continue
        tree = {}
        for line in git("ls-tree", "-r", "-z", commit).split("\0"):
            if not line:
                continue
            meta, path = line.split("\t", 1)
            parts = meta.split()
            if len(parts) == 3 and parts[1] == "blob":
                tree[path] = parts[2]
        same, differ, added = [], [], []
        for root, dirs, files in os.walk(d):
            dirs[:] = [x for x in dirs if x != "node_modules" and not os.path.islink(os.path.join(root, x))]
            for fn in files:
                p = os.path.join(root, fn)
                rel = os.path.relpath(p, d)
                if os.path.islink(p):
                    added.append(rel)
                    continue
                if rel in tree:
                    try:
                        (same if git_blob_sha(p) == tree[rel] else differ).append(rel)
                    except OSError:
                        differ.append(rel)
                else:
                    added.append(rel)
        missing = sorted(set(tree) - set(same) - set(differ))
        if tree and len(same) >= 0.5 * len(tree):
            plans[d] = {"commit": commit, "rev": info["rev"], "made": info["ts"], "proof": f"{info['f']} line {info['ln']} ({info['id']})",
                        "same": len(same), "differ": sorted(differ), "added": sorted(added), "missing": missing[:200],
                        "missing_count": len(missing), "same_set": set(same)}
    return plans


# ----------------------------------------------------------------------------------------
# Step: scratch (the scratch folder's proof)
# ----------------------------------------------------------------------------------------
def scratch_inventory(now_ts):
    """Walk SCRATCH and TASKS. Returns (files to archive, symlinks, excluded folders with reasons)."""
    excluded = []
    recent_cut = now_ts - RECENT_MINUTES * 60
    # in-progress folders: named by the orchestrator, or written in the last RECENT_MINUTES
    in_prog = set(os.path.join(SCRATCH, p) for p in IN_PROGRESS)
    for top in sorted(os.listdir(SCRATCH)):
        tp = os.path.join(SCRATCH, top)
        if top in SCRATCH_TOOLS or top == "evidence" or not os.path.isdir(tp) or os.path.islink(tp):
            continue
        cand = [tp] + [os.path.join(tp, x) for x in sorted(os.listdir(tp)) if os.path.isdir(os.path.join(tp, x)) and not os.path.islink(os.path.join(tp, x))]
        for c in cand[1:] if len(cand) > 1 else cand:
            newest = 0
            for root, dirs, files in os.walk(c):
                dirs[:] = [x for x in dirs if x != "node_modules"]
                for fn in files:
                    try:
                        newest = max(newest, os.lstat(os.path.join(root, fn)).st_mtime)
                    except OSError:
                        pass
            if newest >= recent_cut:
                in_prog.add(c)
        if len(cand) == 1:
            pass
    files, links = [], []
    for root, dirs, fs in os.walk(SCRATCH):
        rel_root = os.path.relpath(root, SCRATCH)
        keep = []
        for x in sorted(dirs):
            p = os.path.join(root, x)
            rel = os.path.normpath(os.path.join(rel_root, x))
            if rel_root == "." and (x in SCRATCH_TOOLS or x == "evidence"):
                excluded.append({"path": "scratchpad/" + x, "reason": "the evidence folder itself" if x == "evidence" else "tools or downloads, not proof"})
                continue
            if p in in_prog:
                excluded.append({"path": "scratchpad/" + rel, "reason": "in progress (still being written at the snapshot); not read"})
                continue
            if x == "node_modules":
                if os.path.islink(p):
                    links.append((p, "scratchpad/" + rel))
                else:
                    excluded.append({"path": "scratchpad/" + rel, "reason": "installed packages, not proof"})
                continue
            if os.path.islink(p):
                links.append((p, "scratchpad/" + rel))
                continue
            keep.append(x)
        dirs[:] = keep
        for fn in sorted(fs):
            p = os.path.join(root, fn)
            rel = os.path.normpath(os.path.join(rel_root, fn))
            if rel_root == "." and os.path.join(SCRATCH, fn) in in_prog:
                continue
            if os.path.islink(p):
                links.append((p, "scratchpad/" + rel))
            else:
                try:
                    if os.lstat(p).st_mtime >= recent_cut:
                        excluded.append({"path": "scratchpad/" + rel, "reason": "written in the last %d minutes before the snapshot; not read" % RECENT_MINUTES})
                        continue
                except OSError:
                    continue
                files.append((p, "scratchpad/" + rel))
    if os.path.isdir(TASKS):
        for fn in sorted(os.listdir(TASKS)):
            p = os.path.join(TASKS, fn)
            if os.path.islink(p):
                links.append((p, "tasks/" + fn))
            elif os.path.isfile(p):
                files.append((p, "tasks/" + fn))
    return files, links, excluded


def step_scratch():
    now_ts = time.time()
    started = iso()
    folder = os.path.join(OUT, "scratch")
    if os.path.isdir(folder):
        for f in os.listdir(folder):
            if f.endswith(".tar.xz") or f in ("SHA256SUMS", "parts.json"):
                os.remove(os.path.join(folder, f))
    ensure_dir(folder)
    files, links, excluded = scratch_inventory(now_ts)
    copies = find_repo_copies()
    plans = copy_plan(copies)
    log(f"scratch: {len(files)} files, {len(links)} links, {len(plans)} repository copies stored as differences")
    pw = PartWriter(folder, "scratch")
    members, red, skipped_same = [], [], collections.Counter()
    t0 = time.time()
    for p, arc in files:
        # a file of a git-archive copy that is identical to its commit is not stored
        skip = False
        for d, plan in plans.items():
            if p.startswith(d + "/"):
                rel = os.path.relpath(p, d)
                if rel in plan["same_set"]:
                    skip = True
                    skipped_same[d] += 1
                break
        if skip:
            continue
        try:
            st = os.lstat(p)
            with open(p, "rb") as f:
                raw = f.read()
        except OSError as ex:
            excluded.append({"path": arc, "reason": "could not be read: " + str(ex)[:80]})
            continue
        clean, counts = scrub(raw)
        pw.add_bytes(arc, clean, st.st_mtime, st.st_mode)
        members.append({"arcname": arc, "part": pw.cur_name, "bytes": len(clean), "sha256_archived": hashlib.sha256(clean).hexdigest(),
                        "sha256_source": hashlib.sha256(raw).hexdigest(),
                        "mtime": iso(dt.datetime.fromtimestamp(st.st_mtime, dt.timezone.utc))})
        if counts:
            red.append({"archive": "scratch", "file": arc, "counts": dict(counts), "broken_json_lines": 0})
    for p, arc in links:
        try:
            target = os.readlink(p)
            st = os.lstat(p)
        except OSError:
            continue
        pw.add_symlink(arc, target, st.st_mtime)
        members.append({"arcname": arc, "part": pw.cur_name, "symlink_to": target})
    parts = pw.finish()
    verify_parts(folder, parts)
    write_sums(folder, parts, "scratch")
    copies_out = []
    for d, plan in sorted(plans.items()):
        copies_out.append({"path": "scratchpad/" + os.path.relpath(d, SCRATCH), "commit": plan["commit"], "rev_given": plan["rev"],
                           "made_at": plan["made"], "made_by": plan["proof"], "files_identical_not_stored": skipped_same[d],
                           "files_changed_stored": plan["differ"], "files_added_stored": len(plan["added"]),
                           "files_of_commit_missing": plan["missing_count"],
                           "rebuild": f"git archive {plan['commit'][:12]} | tar -x -C <folder>, then unpack this folder's stored files over it"})
    write_json(os.path.join(folder, "parts.json"), {"read_started_at": started, "made_at": iso(), "parts": parts, "members": members,
                                                   "excluded": excluded, "repository_copies": copies_out})
    write_json(os.path.join(WORK, "redactions-scratch.json"), red)
    log(f"scratch: {len(members)} members in {len(parts)} parts, {time.time() - t0:.0f} s")
    write_redactions()


def write_redactions():
    red = []
    for n in ("transcripts", "scratch"):
        p = os.path.join(WORK, f"redactions-{n}.json")
        if os.path.exists(p):
            red += json.load(open(p))
    p = os.path.join(WORK, "redactions-record.json")
    if os.path.exists(p):
        for name, counts in sorted(json.load(open(p)).items()):
            if name not in ("redactions.md", "redactions.json"):
                red.append({"archive": "record", "file": name, "counts": counts, "broken_json_lines": 0})
    tot = collections.Counter()
    files_by_kind = collections.Counter()
    for r in red:
        for k, v in r["counts"].items():
            tot[k] += v
            files_by_kind[k] += 1
    L = ["# Redactions", "",
         "Every redaction made while packing the archives, by file and kind. No value is shown.",
         "",
         f"- The CEO's email address is replaced with `{CEO_TOKEN}`.",
         f"- Anything that looks like a secret is replaced with `{SECRET_TOKEN}`. For a header, a variable or a",
         "  password field only the value is replaced; the name stays so the reader sees what was there.",
         "- Files in the repository are not packed here (they are listed with their hashes in MANIFEST.md),",
         "  so they are not redacted. The repository holds no live secret: its `.env.example` has placeholders.",
         "- The rules are in `make-evidence.py` (`SECRET_RULES`). Values that look like placeholders",
         "  (`placeholder`, `example`, `process.env.X`, `${X}` and similar) are left as they are.",
         "",
         "## Totals", "", "| Kind | Replacements | Files |", "|---|---|---|"]
    for k, v in tot.most_common():
        L.append(f"| {k} | {v} | {files_by_kind[k]} |")
    if not tot:
        L.append("| none | 0 | 0 |")
    L += ["", "## By file", "", "| Archive | File | Kind | Count |", "|---|---|---|---|"]
    for r in sorted(red, key=lambda r: (r["archive"], r["file"])):
        for k, v in sorted(r["counts"].items()):
            L.append(f"| {r['archive']} | `{md_escape(r['file'])}` | {k} | {v} |")
    broken = [r for r in red if r.get("broken_json_lines")]
    L += ["", "## JSON lines changed in form", ""]
    if broken:
        for r in broken:
            L.append(f"- `{r['file']}`: {r['broken_json_lines']} lines no longer parse after the replacement.")
    else:
        L.append("None: every transcript line that parsed before a replacement still parses after it.")
    vpath = os.path.join(WORK, "verify.json")
    ver = json.load(open(vpath)) if os.path.exists(vpath) else None
    L += ["", "## Check after packing", ""]
    if ver:
        L.append(f"On {ver['checked_at']} every part was read back and every archived file scanned again with the same rules.")
        L += ["", "| Part | Size | Under 45 MB | sha256 matches | Files read | Matches left |", "|---|---|---|---|---|---|"]
        for sub, rows in ver["archives"].items():
            for r in rows:
                left = ", ".join(f"{k} {v}" for k, v in r["remaining_matches"].items()) or "none"
                L.append(f"| `{sub}/{r['part']}` | {human(r['size'])} | {'yes' if r['under_limit'] else 'NO'} | {'yes' if r['sha256_ok'] else 'NO'} | {r['members_read']} | {left} |")
    else:
        L.append("Not run yet (step `verify`).")
    write_text(os.path.join(OUT, "redactions.md"), "\n".join(L) + "\n")
    write_json(os.path.join(OUT, "redactions.json"), {"totals": dict(tot), "files": red, "check_after_packing": ver})


# ----------------------------------------------------------------------------------------
# Git history: which commit a checkout held at a given time
# ----------------------------------------------------------------------------------------
_REFLOGS = None


def _read_reflog(path):
    out = []
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                m = re.match(r"([0-9a-f]{40}) ([0-9a-f]{40}) .*? (\d{9,11}) [+-]\d{4}\t?(.*)", line)
                if m:
                    out.append((int(m.group(3)), m.group(2), m.group(4).strip()))
    except OSError:
        pass
    return out


def reflogs():
    global _REFLOGS
    if _REFLOGS is not None:
        return _REFLOGS
    gd = os.path.join(REPO, ".git")
    worktrees = {REPO: _read_reflog(os.path.join(gd, "logs", "HEAD"))}
    wt_dir = os.path.join(gd, "worktrees")
    if os.path.isdir(wt_dir):
        for name in os.listdir(wt_dir):
            try:
                wpath = open(os.path.join(wt_dir, name, "gitdir")).read().strip()
            except OSError:
                continue
            wpath = os.path.dirname(wpath)
            worktrees[wpath] = _read_reflog(os.path.join(wt_dir, name, "logs", "HEAD"))
    branches = {}
    heads = os.path.join(gd, "logs", "refs", "heads")
    for root, dirs, files in os.walk(heads):
        for fn in files:
            p = os.path.join(root, fn)
            branches[os.path.relpath(p, heads)] = _read_reflog(p)
    # first-parent history of the programme branch, for times before the reflog starts
    fp = []
    for line in git("log", "--first-parent", "--format=%H %ct", BRANCH).splitlines():
        h, t = line.split()
        fp.append((int(t), h, "commit (first-parent history)"))
    fp.sort()
    _REFLOGS = {"worktrees": worktrees, "branches": branches, "first_parent": fp}
    return _REFLOGS


def _at(entries, t):
    best = None
    for ts, sha, msg in entries:
        if ts <= t:
            best = sha
        else:
            break
    return best


def worktree_of(d):
    rl = reflogs()["worktrees"]
    best = None
    for w in rl:
        if d == w or d.startswith(w.rstrip("/") + "/"):
            if best is None or len(w) > len(best):
                best = w
    # a removed worktree under .claude/worktrees is not the main checkout
    wt_root = os.path.join(REPO, ".claude", "worktrees") + "/"
    if best == REPO and d.startswith(wt_root):
        return None
    return best


def removed_worktree_branch(d):
    """Branch of a worktree that no longer exists (the Workflow tool names them worktree-<name>)."""
    wt_root = os.path.join(REPO, ".claude", "worktrees") + "/"
    if d and d.startswith(wt_root):
        name = d[len(wt_root):].split("/")[0]
        for cand in ("worktree-" + name, name):
            if cand in reflogs()["branches"]:
                return cand
    return None


def head_at(d, branch, ts):
    """HEAD of the checkout that holds directory D at time TS (ISO string). None if unknown."""
    t = parse_ts(ts)
    if t is None:
        return None
    t = t.timestamp()
    R = reflogs()
    w = worktree_of(d) if d else None
    if w and w != REPO:
        e = R["worktrees"].get(w) or []
        if e and e[0][0] <= t:
            return _at(e, t)
    if w == REPO:
        e = R["worktrees"][REPO]
        if e and e[0][0] <= t:
            return _at(e, t)
        return _at(R["first_parent"], t)
    rb = removed_worktree_branch(d)
    for b in (rb, branch):
        if b and b in R["branches"]:
            e = R["branches"][b]
            if e and e[0][0] <= t:
                return _at(e, t)
    return None


def branch_at(branch, ts):
    t = parse_ts(ts)
    e = reflogs()["branches"].get(branch) if t else None
    if not e or e[0][0] > t.timestamp():
        return None
    return _at(e, t.timestamp())


CHECKOUT_RE = re.compile(r"git\s+(?:-C\s+\S+\s+)?(?:checkout|switch)((?:\s+-{1,2}[A-Za-z][\w-]*)*)\s+([^\s;&|<>-][^\s;&|<>]*)")


def branch_switches(items):
    """Branches each transcript created and checked out: {file: [(time, branch), ...]} from (file, time, command)."""
    out = collections.defaultdict(list)
    for f, ts, cmd in items:
        for m in CHECKOUT_RE.finditer(strip_heredocs(cmd or "")):
            tok = m.group(2)
            if re.fullmatch(r"[0-9a-f]{7,40}", tok):
                full = git("rev-parse", "--verify", "--quiet", tok + "^{commit}", check=False).strip()
                if full:
                    out[f].append((ts or "", "commit:" + full))
            elif tok in reflogs()["branches"]:
                out[f].append((ts or "", tok))
    for f in out:
        out[f].sort()
    return out


def removed_worktree_commit(d, cwd, br, ts, switches=()):
    """A run in a worktree since removed. The Workflow tool made each worktree on a branch worktree-<name>; its
    agent then created and checked out a branch of its own (signoff-runner-r4 and so on) and committed there.
    The commit is that branch's tip at the time of the run, from its reflog. The branch field of a transcript line
    is not used when it names the programme branch: for workflow agents it is the parent session's branch."""
    wt_root = os.path.join(REPO, ".claude", "worktrees") + "/"
    wt = (wt_root + d[len(wt_root):].split("/")[0]) if d and d.startswith(wt_root) else None
    sw = [b for t, b in switches if t <= (ts or "")]
    if sw and sw[-1].startswith("commit:"):
        return sw[-1][7:], "removed worktree, detached at a commit the agent checked out"
    if sw and sw[-1] in reflogs()["branches"]:
        c = branch_at(sw[-1], ts)
        if c:
            return c, "removed worktree, on branch " + sw[-1] + " (checked out by the agent)"
    same = bool(wt and cwd and (cwd == wt or cwd.startswith(wt + "/")))
    if same and br and br != BRANCH and br in reflogs()["branches"]:
        return branch_at(br, ts), "removed worktree, on branch " + br
    rb = removed_worktree_branch(d)
    c = branch_at(rb, ts) if rb else None
    return c, "removed worktree, branch " + (rb or "unknown") + " at its base (no other branch checked out in its transcript)"


# ----------------------------------------------------------------------------------------
# Step: tests (TESTS-SUMMARY.md and tests.json)
# ----------------------------------------------------------------------------------------
KIND_LABEL = {
    "vitest": "unit tests (vitest)", "typecheck": "typecheck (tsc)", "lint": "lint (eslint)",
    "node-test": "node tests", "dsrt": "DSRT acceptance-test runner", "build": "build (next build)",
    "signoff-tool": "sign-off tool", "pytest": "pytest", "probe": "probe", "mutation": "mutation run",
    "tsx-script": "check script (tsx)", "python-script": "Python audit or check", "node-script": "check script (node)",
}

BG_RE = re.compile(r"Command running in background with ID: (\S+?)\.? Output is being written to: (\S+)")
CD_RE = re.compile(r"(?:^|[;&|(\n]|\bthen\b|\bdo\b)\s*cd\s+(\"[^\"]+\"|'[^']+'|[^\s;&|)]+)")


def effective_dir(cmd, cwd):
    """Directory the first check of a command runs in: the last `cd` before it, else the shell's cwd."""
    body = strip_inline_code(strip_heredocs(cmd))
    first = None
    for name, rx in KINDS:
        m = rx.search(body)
        if m and (first is None or m.start() < first):
            first = m.start()
    upto = body if first is None else body[:first]
    d = cwd
    env = shell_env(upto)
    for m in CD_RE.finditer(upto):
        x = m.group(1).strip("\"'")
        x = expand_vars(x, env)
        if x.startswith("$") or x == "-":
            continue
        if x.startswith("/"):
            d = os.path.normpath(x)
        elif d:
            d = os.path.normpath(os.path.join(d, x))
    return d


def _counts(s):
    out = {}
    for n, w in re.findall(r"(\d+)\s+(passed|failed|skipped|todo|errors?|pending)", s):
        out[w.rstrip("s") if w.startswith("error") else w] = int(n)
    return out


def parse_outcome(kinds, text, err):
    """Numbers a check printed. Returns (dict, one-line summary)."""
    o = {}
    parts = []
    t = text or ""
    # vitest
    vt = [(_counts(a), int(b)) for a, b in re.findall(r"^\s*Tests\s+((?:\d+\s+\w+\s*\|?\s*)+)\((\d+)\)", t, re.M)]
    vf = [(_counts(a), int(b)) for a, b in re.findall(r"^\s*Test Files\s+((?:\d+\s+\w+\s*\|?\s*)+)\((\d+)\)", t, re.M)]
    if vt:
        o["vitest"] = [{"passed": c.get("passed", 0), "failed": c.get("failed", 0), "skipped": c.get("skipped", 0) + c.get("todo", 0), "total": n} for c, n in vt]
        o["vitest_files"] = [{"passed": c.get("passed", 0), "failed": c.get("failed", 0), "total": n} for c, n in vf]
        for i, r in enumerate(o["vitest"]):
            s = f"vitest {r['passed']} passed" + (f", {r['failed']} failed" if r["failed"] else "") + (f", {r['skipped']} skipped" if r["skipped"] else "") + f" of {r['total']}"
            if i < len(o["vitest_files"]):
                f = o["vitest_files"][i]
                s += f" ({f['total']} files" + (f", {f['failed']} failing" if f["failed"] else "") + ")"
            parts.append(s)
    if re.search(r"No test files found", t):
        parts.append("vitest: no test files found")
    # node --test (TAP summary, or the newer 'ℹ' lines)
    nt = re.findall(r"^\s*(?:#|ℹ)\s*(tests|pass|fail|cancelled|skipped|todo)\s+(\d+)\s*$", t, re.M)
    if nt:
        runs, cur = [], {}
        for k, v in nt:
            if k == "tests" and cur:
                runs.append(cur)
                cur = {}
            cur[k] = int(v)
        if cur:
            runs.append(cur)
        o["node_test"] = runs
        for r in runs:
            parts.append(f"node --test {r.get('pass', 0)} passed, {r.get('fail', 0)} failed" + (f" of {r['tests']}" if "tests" in r else "") + (f", {r['skipped']} skipped" if r.get("skipped") else "") + (f", {r['cancelled']} cancelled" if r.get("cancelled") else ""))
    # pytest
    pt = re.findall(r"=+\s+((?:\d+\s+(?:passed|failed|skipped|errors?|xfailed|xpassed|warnings?)[, ]*)+)\s+in\s+[\d.]+s", t)
    if pt:
        o["pytest"] = pt
        parts.append("pytest " + pt[-1].strip())
    # tsc
    if "typecheck" in kinds:
        n_err = len(re.findall(r"error TS\d+", t))
        found = re.findall(r"Found (\d+) errors?", t)
        o["tsc_errors"] = int(found[-1]) if found else n_err
        parts.append(f"tsc {o['tsc_errors']} errors" if o["tsc_errors"] else "tsc no errors printed")
    # eslint
    es = re.findall(r"✖ (\d+) problems? \((\d+) errors?, (\d+) warnings?\)", t)
    if es:
        p, e, w = es[-1]
        o["eslint"] = {"problems": int(p), "errors": int(e), "warnings": int(w)}
        parts.append(f"eslint {e} errors, {w} warnings")
    elif "lint" in kinds:
        parts.append("eslint no problems printed")
    # DSRT
    dr = re.findall(r"round (\S+): pass (\d+), fail (\d+), blocked (\d+)", t)
    dd = re.findall(r"\{'(pass|fail|blocked)': (\d+)(?:, '(pass|fail|blocked)': (\d+))?(?:, '(pass|fail|blocked)': (\d+))?\}", t)
    if dr:
        o["dsrt"] = [{"round": r, "pass": int(p), "fail": int(f), "blocked": int(b)} for r, p, f, b in dr]
        for x in o["dsrt"]:
            parts.append(f"DSRT round {x['round']}: {x['pass']} pass, {x['fail']} fail, {x['blocked']} blocked")
    elif dd:
        o["dsrt_counts"] = []
        for g in dd:
            d = {}
            for i in range(0, 6, 2):
                if g[i]:
                    d[g[i]] = int(g[i + 1])
            o["dsrt_counts"].append(d)
        for d in o["dsrt_counts"]:
            parts.append("DSRT " + ", ".join(f"{v} {k}" for k, v in d.items()))
    if "dsrt" in kinds and not (dr or dd):
        ch = re.findall(r"^([A-Z]\d{1,2})\s+(pass|fail|blocked)\s", t, re.M)
        if ch:
            c = collections.Counter(s for _, s in ch)
            o["dsrt_checks"] = {k: s for k, s in ch}
            parts.append("DSRT checks shown: " + ", ".join(f"{k} {s}" for k, s in ch[:12]) + (" …" if len(ch) > 12 else ""))
    # validate.js
    va = re.findall(r"^(VALID|INVALID) (\S+) (\S+): (\d+) errors, (\d+) warnings", t, re.M)
    if va:
        o["validate"] = [{"result": a, "kind": b, "file": c, "errors": int(d), "warnings": int(e)} for a, b, c, d, e in va]
        ok = sum(1 for x in va if x[0] == "VALID")
        parts.append(f"validate {ok} VALID, {len(va) - ok} INVALID")
    # quote-check
    qc = re.findall(r"quote-check (\S+): (\d+)/(\d+) found \(([\d.]+)%; (\d+) exact\), (\d+) weak, (\d+) not found, (\d+) unopenable", t)
    if qc:
        o["quote_check"] = [{"file": a, "found": int(b), "total": int(c), "pct": float(d), "exact": int(e), "weak": int(f), "not_found": int(g), "unopenable": int(h)} for a, b, c, d, e, f, g, h in qc]
        for x in o["quote_check"][:6]:
            parts.append(f"quote-check {x['found']}/{x['total']} found ({x['pct']}%), {x['not_found']} not found, {x['unopenable']} unopenable")
    # compile.js
    for m in re.finditer(r"\{\"out_dir\":.*?\}(?=\s*$|\n)", t, re.M):
        try:
            cj = json.loads(m.group(0))
            o.setdefault("compile", []).append(cj)
            parts.append(f"compile: seed rows {cj.get('seed_rows')}, {cj.get('rows_changed')} rows changed, {cj.get('unexplained')} unexplained")
        except Exception:
            pass
    # mutation verdicts
    kill = len(re.findall(r"\b(?:KILLED|killed|caught|CAUGHT|DETECTED)\b", t))
    surv = len(re.findall(r"\b(?:SURVIVES|SURVIVED|survived|survives|NOT CAUGHT)\b", t))
    if ("mutation" in kinds) and (kill or surv):
        o["mutation"] = {"killed_mentions": kill, "survived_mentions": surv}
        parts.append(f"mutants: {kill} killed or caught, {surv} survived (as printed)")
    # exit codes printed by the command
    ex = re.findall(r"(?im)^\s*\[?(?:([a-z][\w./-]*)\s+)?exit(?:ed with)?(?:\s*code)?\s*[=:]?\s*(\d+)\]?\s*$", t)
    if ex:
        o["exits"] = [{"what": a or "", "code": int(b)} for a, b in ex]
        parts.append("exit " + ", ".join(f"{a + ' ' if a else ''}{b}" for a, b in ex[:6]))
    if err:
        parts.append("the command returned a non-zero exit")
    if not parts:
        lines = [x.strip() for x in t.strip().split("\n") if x.strip()]
        tail = " / ".join(lines[-3:])[:300] if lines else "(no output)"
        parts.append("output ends: " + tail)
    return o, "; ".join(parts)


def verdict_of(text, structured):
    """Short verdict words and an excerpt from an agent's final report."""
    t = text or ""
    words = []
    for rx in (r"(?i)\bverdict\b[\s*:_-]*\**\s*([A-Za-z][A-Za-z ,'-]{2,60})",
               r"(?i)\b(approve[sd]?|not approved|reject(?:ed|s)?|request(?:s|ed)? changes|changes requested|do not merge|safe to merge|ready to merge|merge as is)\b",
               r"(?i)\b(no blocking issues?|\d+ blocking issues?|blocking: \d+|\d+ confirmed|\d+ refuted)\b",
               r"(?i)\b(\d+(?:\.\d+)?)\s*(?:/|out of)\s*10\b"):
        for m in re.finditer(rx, t):
            w = m.group(1).strip().rstrip(".,")
            if w and w.lower() not in [x.lower() for x in words]:
                words.append(w)
            if len(words) >= 6:
                break
    sv = []
    if structured:
        inp = structured[-1].get("input") or {}
        if isinstance(inp, dict):
            for k, v in inp.items():
                if isinstance(v, bool) or isinstance(v, (int, float)):
                    sv.append(f"{k}={v}")
                elif isinstance(v, str) and len(v) <= 60 and "\n" not in v:
                    sv.append(f"{k}={v}")
                elif isinstance(v, list):
                    sv.append(f"{k}: {len(v)}")
                if len(sv) >= 10:
                    break
    stopped = None
    if re.search(r"(?i)out of usage credits|hit your (?:5-hour|weekly|session) limit|usage limit|rate limit", t[:400]) and not structured:
        stopped = "stopped on a usage limit before finishing"
    excerpt = re.sub(r"\s+", " ", t).strip()[:400]
    if structured and (len(t) < 200 or not t):
        excerpt = re.sub(r"\s+", " ", json.dumps(structured[-1].get("input"), ensure_ascii=False))[:400]
    return {"words": words[:6], "structured": sv[:10], "stopped": stopped, "excerpt": excerpt}


NUM_RE = re.compile(r"(?<![\w.\-/:#])(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)(%?)(?![\w/:]|\.\d)")
MONTHS = r"(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)"


def sig_numbers(s):
    """Numbers in a statement that carry a result: not dates, times, years, versions or ids."""
    out = []
    for m in NUM_RE.finditer(s):
        raw, pct = m.group(1), m.group(2)
        a, b = m.start(), m.end()
        before, after = s[max(0, a - 12):a], s[b:b + 12]
        if re.search(MONTHS + r"\s*$", before, re.I) or re.match(r"\s*" + MONTHS, after, re.I):
            continue
        if re.search(r"(?i)(fable|opus|sonnet|haiku|version|v|node|next|react|python)\s*$", before):
            continue
        if re.search(r"(?i)(round|wave|step|session|section|part|batch|phase|rule|line|lines|item|package|chain|page|D|C|B|WS)\s*$", before) and not pct:
            continue
        if re.match(r"\s*(?:UTC|h\b|am\b|pm\b|minutes?|min\b|hours?|days?|GB|MB|KB|ms\b|s\b)", after):
            continue
        v = raw.replace(",", "")
        try:
            f = float(v)
        except ValueError:
            continue
        if not pct and "." not in v and f < 10:
            continue
        if not pct and 2020 <= f <= 2030 and "." not in v:
            continue
        out.append(v + pct)
    return out


def norm_numbers(text):
    s = set()
    for m in NUM_RE.finditer(text):
        v = m.group(1).replace(",", "")
        s.add(v)
        s.add(v + "%")
        if "." in v:
            s.add(v.rstrip("0").rstrip("."))
    for m in re.finditer(r"\d+(?:\.\d+)?", text):
        v = m.group(0)
        s.add(v)
        if "." in v:
            ip, dp = v.split(".", 1)
            for k in range(1, min(len(dp), 3)):
                s.add(f"{round(float(v), k):.{k}f}")
    return s


TEST_NOUN = re.compile(r"(?i)\b(tests?|checks?|typecheck|tsc|lint|eslint|vitest|dsrt|probes?|mutants?|mutation|verdicts?|reviews?|reviewers?|judges?|refuters?|quotes?|validator|validates?|compiles?|compiled|builds?|audits?|calibration|suites?|runner|assertions?)\b|\b[CDEKMLPSBXNQG]\d{1,2}\b")
RESULT_WORD = re.compile(r"(?i)\b(pass(?:es|ed|ing)?|fail(?:s|ed|ing|ures?)?|blocked|green|clean|approved?|rejected|refuted|confirmed|found|errors?|warnings?|violations?|mismatches|blocking|killed|survived?|caught|holds?|held)\b")
STOP = set("that this with from were they them their there then than have been into also only each more most what when which while where about after before other some such over under same just like will would could should does done made make your ours very much many every both through because these those being here once".split())


GENERIC = set("pass passe passed passing fail failed failing failure test tested testing check checked checking error warning found clean green blocked result review reviewed run running all every none after before still also total file number item count value step round now new old done well".split())


def _stem(w):
    w = w.lower()
    if len(w) > 4 and w.endswith("s") and not w.endswith("ss"):
        w = w[:-1]
    return w


def content_words(s):
    """Distinctive words of a statement (generic result words only when nothing else is left)."""
    ws = set(_stem(w) for w in re.findall(r"[A-Za-z][A-Za-z-]{3,}", s) if w.lower() not in STOP)
    distinct = set(w for w in ws if w not in GENERIC)
    return distinct or ws


TESTY = re.compile(r"(?i)\b(tests?|suites?|pass(?:es|ed)?|fixtures?|cases?)\b")


def test_summary_hit(seg, num):
    """NUM printed as a test count: `Tests 897 passed`, `# pass 105`, `897 passed`, `(1468)`."""
    n = re.escape(num.rstrip("%"))
    return re.search(r"(?i)(?:tests?\s+(?:\d+\s+\w+\s*\|\s*)*" + n + r"\s+passed|#\s*(?:pass|tests)\s+" + n + r"\b|(?<![\d.])" + n + r"\s+(?:tests?|passed|passing|pass)\b|\(\s*" + n + r"\s*\))", seg) is not None


def split_claims(text):
    """Sentences and table rows of an assistant message that state a test or check result.
    Returns (claim, words used for matching). A table row borrows its table's header words."""
    claims = []
    header = None
    prev_table = False
    for block in text.split("\n"):
        b = block.strip()
        if not b:
            prev_table = False
            header = None
            continue
        is_row = b.startswith("|")
        if is_row and re.fullmatch(r"\|?[\s:|-]+\|?", b):
            continue
        if is_row and not prev_table:
            header = b
            prev_table = True
            continue
        if not is_row:
            prev_table = False
            header = None
        pieces = [b] if is_row else re.split(r"(?<=[.;!?])\s+(?=[A-Z0-9\"'(*])", b)
        for p in pieces:
            p = p.strip(" -*")
            if len(p) < 12:
                continue
            ctx = (header + " " + p) if (is_row and header) else p
            if TEST_NOUN.search(ctx) and RESULT_WORD.search(ctx):
                claims.append((p, ctx))
    return claims


def _num_pattern(num):
    """Regex for NUM as printed, allowing a printed value that rounds to it (1.26 for 1.3)."""
    n = num.rstrip("%")
    if "." in n:
        ip, dp = n.split(".", 1)
        return re.escape(ip) + r"\." + r"\d+", (float(n), len(dp))
    return re.escape(n), None


def _match_ok(m, rnd):
    if rnd is None:
        return True
    try:
        return round(float(m.group(0)), rnd[1]) == rnd[0]
    except ValueError:
        return False


def number_near_words(text, num, words, window=160, testy=False):
    """True when NUM occurs in TEXT within WINDOW characters of one of WORDS, or, for a statement
    about tests, where NUM is printed as a test count."""
    pat, rnd = _num_pattern(num)
    if rnd is not None:
        digits = len(re.sub(r"\D", "", num))
        for m in re.finditer(r"(?<![\d.])" + pat + r"(?![\d])", text):
            if not _match_ok(m, rnd):
                continue
            if digits >= 4:
                return True
            seg = text[max(0, m.start() - window):m.end() + window].lower()
            if any(w in seg for w in words):
                return True
        return False
    pat = re.escape(num.rstrip("%"))
    digits = len(re.sub(r"\D", "", num))
    if digits >= 4:
        return re.search(r"(?<![\d.])" + pat + r"(?![\d])", text) is not None
    for m in re.finditer(r"(?<![\d.])" + pat + r"(?![\d])", text):
        seg = text[max(0, m.start() - window):m.end() + window].lower()
        for w in words:
            if w in seg:
                return True
        if testy and test_summary_hit(text[max(0, m.start() - 60):m.end() + 40], num):
            return True
    return False


def load_meta(name):
    if name == "main.jsonl":
        return {}
    p = os.path.join(SESSION_DIR, name[:-6] + ".meta.json")
    try:
        return json.load(open(p))
    except Exception:
        return {}


def step_tests():
    calls = read_jsonl(os.path.join(IDX, "calls.jsonl"))
    texts = read_jsonl(os.path.join(IDX, "texts.jsonl"))
    agents = read_jsonl(os.path.join(IDX, "agents.jsonl"))
    snap = load_snapshot()
    copies = find_repo_copies()
    metas = {a["f"]: load_meta(a["f"]) for a in agents}
    agent_desc = {a["f"]: (metas[a["f"]].get("description") or "") for a in agents}
    # ---- every check run
    switches = branch_switches((c["f"], c["ts"], c.get("cmd")) for c in calls if c.get("cmd"))
    runs = []
    for c in calls:
        if not c.get("kinds"):
            continue
        res = c.get("res") or ""
        bgfile = None
        m = BG_RE.search(res[:2000])
        if m:
            p = m.group(2)
            if os.path.exists(p) and not os.path.islink(p):
                try:
                    with open(p, encoding="utf-8", errors="replace") as f:
                        res = f.read()
                    bgfile = p
                except OSError:
                    pass
            else:
                bgfile = p + " (not found)"
        o, summary = parse_outcome(c["kinds"], res, c.get("err"))
        d = effective_dir(c["cmd"], c.get("cwd"))
        commit, where = None, None
        copy_of = None
        main_at = None
        if d:
            for cd, info in copies.items():
                if d == cd or d.startswith(cd + "/"):
                    copy_of = info
                    break
        if copy_of:
            cm = resolve_rev(copy_of["rev"], copy_of.get("gitdir") or copy_of.get("cwd"), copy_of["ts"])
            commit = cm
            where = "copy made with git archive " + copy_of["rev"]
        else:
            w = worktree_of(d) if d else None
            main_at = None
            if w == REPO:
                where = "main checkout"
                commit = head_at(d, c.get("br"), c["ts"])
            elif w:
                where = "worktree " + os.path.basename(w)
                commit = head_at(d, c.get("br"), c["ts"])
            elif removed_worktree_branch(d):
                commit, where = removed_worktree_commit(d, c.get("cwd"), c.get("br"), c["ts"], switches.get(c["f"], ()))
            else:
                where = "scratch folder (not a git checkout)" if d and d.startswith(SCRATCH) else "other folder (not a git checkout)"
                commit = None
                main_at = head_at(REPO, None, c["ts"])
        who = "orchestrator" if c["f"] == "main.jsonl" else ("agent: " + agent_desc.get(c["f"], "")[:80])
        lines = c["cmd"].split("\n")
        runs.append({
            "id": c["id"], "ts": c["ts"], "f": c["f"], "ln": c["ln"], "rln": c.get("rln"), "who": who,
            "kinds": c["kinds"], "cmd": c["cmd"], "desc": c.get("desc", ""), "dir": d, "where": where,
            "commit": commit, "main_at": None if copy_of else main_at, "outcome": o, "summary": summary, "err": c.get("err"),
            "background_output": bgfile, "persisted": c.get("persisted"), "cmd_lines": len(lines),
        })
    runs.sort(key=lambda r: (r["ts"] or "", r["f"], r["ln"]))
    for i, r in enumerate(runs, 1):
        r["n"] = i
    # ---- agents: final reports and verdicts
    agent_rows = []
    for a in agents:
        if a["f"] == "main.jsonl" or a["f"].endswith("/journal.jsonl"):
            continue
        meta = metas.get(a["f"], {})
        final = a.get("final_text") or ""
        src_ln = a.get("final_ln")
        source = "final message" if final else None
        if a.get("handback"):
            final = a["handback"]["message"] or final
            src_ln = a["handback"]["ln"]
            source = "handback"
        elif a.get("structured") and (len(final) < 200):
            src_ln = a["structured"][-1]["ln"]
            source = "structured output"
        v = verdict_of(final, a.get("structured"))
        agent_rows.append({"f": a["f"], "desc": meta.get("description") or (a.get("prompt") or "")[:120],
                           "type": meta.get("agentType"), "phase": meta.get("workflowPhase"),
                           "model": meta.get("model") or meta.get("pickedEffortModel") or (a["models"][0][0] if a.get("models") else None),
                           "models_used": a.get("models"), "first_ts": a.get("first_ts"), "last_ts": a.get("last_ts"),
                           "final_ts": a.get("final_ts"), "final_ln": src_ln, "report_source": source, "n_calls": a.get("n_calls"),
                           "n_checks": a.get("n_checks"), "verdict": v, "finished": meta.get("finished"),
                           "final_text": final})
    agent_rows.sort(key=lambda r: r["first_ts"] or "")
    # ---- workflow run records
    wf_rows = []
    wdir = os.path.join(SESSION_DIR, "workflows")
    for fn in sorted(os.listdir(wdir)) if os.path.isdir(wdir) else []:
        if not fn.endswith(".json"):
            continue
        try:
            w = json.load(open(os.path.join(wdir, fn)))
        except Exception:
            continue
        res = w.get("result")
        rs = json.dumps(res, ensure_ascii=False) if res is not None else ""
        jr = os.path.join("subagents", "workflows", w.get("runId") or "", "journal.jsonl")
        wf_rows.append({"journal": jr if os.path.exists(os.path.join(SESSION_DIR, jr)) else None, "f": "workflows/" + fn, "runId": w.get("runId"), "ts": w.get("timestamp"), "name": w.get("workflowName"),
                        "status": w.get("status"), "agents": w.get("agentCount"), "duration_min": round((w.get("durationMs") or 0) / 60000, 1),
                        "summary": w.get("summary"), "result": rs[:200000]})
    wf_rows.sort(key=lambda r: r["ts"] or "")
    # ---- proof corpus for statements: results visible before each statement
    corpus = []   # (ts, label, text)
    main_full = {}
    for e in snap["files"]:
        if e["name"] == "main.jsonl":
            data = read_snapshot_bytes(e)
            for ln, raw in enumerate(data.split(b"\n"), 1):
                if b"tool_result" not in raw:
                    continue
                try:
                    o = json.loads(raw)
                except Exception:
                    continue
                msg = o.get("message") if isinstance(o.get("message"), dict) else {}
                for p in msg.get("content") or []:
                    if isinstance(p, dict) and p.get("type") == "tool_result":
                        main_full[p.get("tool_use_id")] = (ln, o.get("timestamp"), result_text(p.get("content")))
    for c in calls:
        if c["f"] == "main.jsonl" and c["id"] in main_full:
            ln, ts, txt = main_full[c["id"]]
            full, _ = full_result(txt, None)
            m = BG_RE.search(full[:2000])
            if m and os.path.exists(m.group(2)) and not os.path.islink(m.group(2)):
                try:
                    full += "\n" + open(m.group(2), encoding="utf-8", errors="replace").read()
                except OSError:
                    pass
            corpus.append((c.get("rts") or c["ts"], f"main.jsonl line {ln}, result of {c['tool']} call {c['id']}", full))
        else:
            corpus.append((c.get("rts") or c["ts"], f"{c['f']} line {c.get('rln')}, result of {c['tool']} call {c['id']}", c.get("res") or ""))
    for a in agent_rows:
        if a["final_text"]:
            corpus.append((a["final_ts"] or a["last_ts"], f"{a['f']} line {a['final_ln']}, final report of agent '{a['desc'][:60]}'", a["final_text"]))
    for t in texts:
        if t["role"] in ("notification",):
            corpus.append((t["ts"], f"main.jsonl line {t['ln']}, task notification", t["text"]))
    for w in wf_rows:
        corpus.append((w["ts"], f"{w['f']}, workflow '{w['name']}' result", (w["summary"] or "") + "\n" + w["result"]))
    corpus = [(ts or "", lab, txt) for ts, lab, txt in corpus if txt]
    corpus.sort(key=lambda x: x[0])
    numsets = [norm_numbers(txt) for _, _, txt in corpus]
    post = collections.defaultdict(list)
    for i, ns in enumerate(numsets):
        for n in ns:
            post[n].append(i)
    claims_out = []
    statements = [t for t in texts if t["role"] == "assistant" and not t.get("side")]
    import bisect
    cts = [x[0] for x in corpus]
    KEY_RE = re.compile(r"\b(?:WS\d-\d+|WS\d|[A-Z]\d{1,2}|[Bf]\d{2}(?:-r\d)?|D-\d+|C-\d+|[A-Za-z_-]+\.(?:ts|js|json|md|py|tsx))\b")

    def latest_with(n, words, ts, lo_ts, testy=False):
        """Latest proof item before TS holding number N near one of WORDS; items after LO_TS first."""
        lst = post.get(n, [])
        hi = bisect.bisect_right(cts, ts)
        k = bisect.bisect_left(lst, hi) - 1
        tried = 0
        fallback = None
        while k >= 0 and tried < 300:
            i = lst[k]
            if number_near_words(corpus[i][2], n, words, testy=testy):
                if corpus[i][0] >= lo_ts:
                    return i
                fallback = fallback if fallback is not None else i
                break
            k -= 1
            tried += 1
        return fallback

    for t in statements:
        for cl, ctx in split_claims(t["text"]):
            nums = sig_numbers(cl)
            words = [w for w in content_words(ctx) if len(w) >= 4][:40]
            testy = bool(TESTY.search(cl))
            entry = {"ts": t["ts"], "ln": t["ln"], "uuid": t["uuid"], "claim": cl, "numbers": nums}
            ts = t["ts"] or ""
            tdt = parse_ts(ts)
            lo_ts = iso(tdt - dt.timedelta(hours=72)) if tdt else ""
            if nums:
                need = sorted(set(nums))
                # one proof item that holds every number near the claim's words
                cand = collections.Counter()
                for n in need:
                    for i in post.get(n, ()):
                        if corpus[i][0] <= ts:
                            cand[i] += 1
                single = None
                for i, k in sorted(cand.items(), key=lambda kv: (kv[1], corpus[kv[0]][0]), reverse=True)[:400]:
                    if k < len(need):
                        break
                    if all(number_near_words(corpus[i][2], n, words, testy=testy) for n in need):
                        single = i
                        break
                if single is not None:
                    entry["status"] = "traced"
                    entry["proof"] = corpus[single][1]
                    entry["proof_ts"] = corpus[single][0]
                    entry["missing"] = []
                else:
                    found = {}
                    for n in need:
                        i = latest_with(n, words, ts, lo_ts, testy)
                        if i is not None:
                            found[n] = i
                    missing = [n for n in need if n not in found]
                    items = sorted(set(found.values()), key=lambda i: corpus[i][0])
                    if found and not missing:
                        entry["status"] = "traced across %d items" % len(items) if len(items) > 1 else "traced"
                    elif found:
                        entry["status"] = "partly traced"
                    else:
                        entry["status"] = "not traced"
                    entry["missing"] = missing
                    if items:
                        entry["proof"] = " + ".join(corpus[i][1] + " at " + fmt_ts(corpus[i][0]) for i in items[:4])
                        entry["proof_ts"] = corpus[items[-1]][0]
                        entry["proof_numbers"] = {n: corpus[i][1] for n, i in found.items()}
            else:
                keys = sorted(set(KEY_RE.findall(cl)))
                rw = [w.lower() for w in RESULT_WORD.findall(cl)]
                hit = None
                if keys:
                    hi = bisect.bisect_right(cts, ts)
                    for i in range(hi - 1, max(-1, hi - 20000), -1):
                        txt = corpus[i][2]
                        if all(k in txt for k in keys) and any(w in txt.lower() for w in rw):
                            hit = i
                            break
                if hit is not None:
                    entry["status"] = "traced by name"
                    entry["proof"] = corpus[hit][1]
                    entry["proof_ts"] = corpus[hit][0]
                    entry["keys"] = keys
                else:
                    want = set()
                    for rx, ks in ((r"(?i)typecheck|tsc|type-check", {"typecheck"}), (r"(?i)\blint|eslint", {"lint"}),
                                   (r"(?i)\btests?\b|suite|vitest", {"vitest", "node-test", "pytest", "python-script"}),
                                   (r"(?i)dsrt|acceptance|checks? (?:pass|fail)|\b[A-Z]\d\b", {"dsrt"}),
                                   (r"(?i)probe", {"probe"}), (r"(?i)mutant|mutation", {"mutation"}),
                                   (r"(?i)build", {"build"}), (r"(?i)compile|validat|quote", {"signoff-tool"}),
                                   (r"(?i)audit|seal|sealed|calibrat", {"python-script"})):
                        if re.search(rx, cl):
                            want |= ks
                    prior = [r for r in runs if (r["ts"] or "") <= ts and (not want or want & set(r["kinds"]))]
                    if not prior:
                        prior = [r for r in runs if (r["ts"] or "") <= ts]
                    if prior:
                        r = prior[-1]
                        entry["proof"] = f"{r['f']} line {r['rln'] or r['ln']}, {r['kinds'][0]} run {r['id']} ({r['summary'][:120]})"
                        entry["proof_ts"] = r["ts"]
                        entry["status"] = "no numbers; nearest earlier run"
                    else:
                        entry["status"] = "not traced"
            claims_out.append(entry)
    out = {"made_at": iso(), "snapshot_taken_at": snap["taken_at"], "runs": runs, "agents": agent_rows,
           "workflows": wf_rows, "statements": claims_out}
    write_json(os.path.join(OUT, "tests.json"), out)
    render_tests_md(out)
    log(f"tests: {len(runs)} runs, {len(agent_rows)} agents, {len(wf_rows)} workflows, {len(claims_out)} statements")


def fmt_ts(ts):
    return (ts or "")[:16].replace("T", " ")


# ----------------------------------------------------------------------------------------
# Step: deletions (DELETIONS.md)
# ----------------------------------------------------------------------------------------
DEL_RE = re.compile(r"(?:^|[;&|(\n`]|\bthen\b|\bdo\b|\belse\b|xargs\s+)\s*(rm\s+[^;&|\n]*|rmdir\s+[^;&|\n]*|git\s+(?:-C\s+\S+\s+)?(?:worktree\s+(?:remove|prune)|branch\s+-[dD]|clean\s+-\S+|reset\s+--hard|stash\s+(?:drop|clear)|rm\s)[^;&|\n]*|find\s+[^;&|\n]*(?:-delete|-exec\s+rm)[^;&|\n]*|shred\s+[^;&|\n]*)", re.M)
CODE_DEL_RE = re.compile(r"shutil\.rmtree\(([^)]*)\)|os\.(?:remove|unlink)\(([^)]*)\)|fs\.(?:rmSync|unlinkSync|rmdirSync)\(([^)]*)\)|rimraf")
FOR_RE = re.compile(r"\bfor\s+([A-Za-z_]\w*)\s+in\s+([^;\n]+?)\s*;\s*do\b")
TEMP_PARTS = re.compile(r"(?:^|/)(?:tmp|temp|\.tmp|tmp-[^/]*|[^/]*-tmp|cache|__pycache__|\.cache|node_modules|\.next|dist|coverage)(?:/|$)|\.tmp$")
PATH_RE = re.compile(re.escape(SCRATCH) + r"/[^\s\"'`|;&<>(){}\\,]+")


def _tokens(op):
    try:
        import shlex
        return shlex.split(op, posix=True)
    except Exception:
        return op.split()


def deletion_targets(cmd, op, op_pos, cwd):
    """Paths an rm-like operation names, with variables, loops and the working folder resolved."""
    env = shell_env(cmd, op_pos)
    d = cwd
    for m in CD_RE.finditer(cmd[:op_pos]):
        x = expand_vars(m.group(1).strip("\"'"), env)
        if x.startswith("$") or x == "-":
            continue
        d = os.path.normpath(x if x.startswith("/") else os.path.join(d or "/", x))
    loops = {}
    for m in FOR_RE.finditer(cmd[:op_pos]):
        if "$(" in m.group(2) or "`" in m.group(2):
            loops[m.group(1)] = ["<each item of: " + m.group(2).strip()[:120] + ">"]
            continue
        items = [expand_vars(x.strip("\"'"), env) for x in m.group(2).split()]
        loops[m.group(1)] = items
    toks = _tokens(op)
    if not toks:
        return [], d
    verb = toks[0]
    args = []
    if verb in ("rm", "rmdir", "shred"):
        args = [t for t in toks[1:] if not t.startswith("-") and not t.startswith("2>") and t not in (">", "/dev/null", "2>&1")]
    elif verb == "git":
        if "worktree" in toks and "remove" in toks:
            args = [t for t in toks[toks.index("remove") + 1:] if not t.startswith("-") and not t.startswith("2>")]
        elif "worktree" in toks and "prune" in toks:
            return [("(git worktree prune: records of worktrees whose folders are gone)", "git")], d
        elif "branch" in toks:
            args = ["branch:" + t for t in toks[toks.index("branch") + 2:] if not t.startswith("-")]
        elif "rm" in toks:
            args = [t for t in toks[toks.index("rm") + 1:] if not t.startswith("-")]
        else:
            return [(" ".join(toks[:4]), "git")], d
    elif verb == "find":
        return [("find " + " ".join(toks[1:6]), "find")], d
    out = []
    for a in args:
        if a.startswith("branch:"):
            out.append((a, "branch"))
            continue
        vals = [a]
        for var, items in loops.items():
            if "$" + var in a or "${" + var + "}" in a:
                vals = [a.replace("${" + var + "}", it).replace("$" + var, it) for it in items]
        for v in vals:
            v = expand_vars(v, env)
            if v.startswith("<each item of:"):
                out.append((v, "loop"))
                continue
            if v.startswith("$") or "$(" in v or "`" in v:
                out.append((v, "unresolved"))
                continue
            if not v.startswith("/"):
                v = os.path.normpath(os.path.join(d or REPO, v))
            out.append((os.path.normpath(v), "path"))
    return out, d


def classify_target(p, kind):
    if kind != "path":
        return kind
    rel = os.path.relpath(p, SCRATCH) if p.startswith(SCRATCH + "/") else (os.path.relpath(p, REPO) if p.startswith(REPO + "/") else p)
    if p.startswith("/tmp/") and not p.startswith(TMP_ROOT) and os.path.basename(p).startswith(DSRT_PREFIX):
        return "test fixture in /tmp"
    if TEMP_PARTS.search(rel):
        return "temporary files"
    if p.startswith(os.path.join(REPO, ".claude", "worktrees")):
        return "worktree"
    if p.startswith(REPO + "/"):
        return "repository file or folder"
    if p.startswith(SCRATCH + "/"):
        return "scratch folder or file"
    if p.startswith("/tmp/"):
        return "/tmp folder or file"
    return "other"


def step_deletions():
    calls = read_jsonl(os.path.join(IDX, "calls.jsonl"))
    agents = {a["f"]: a for a in read_jsonl(os.path.join(IDX, "agents.jsonl"))}
    metas = {f: load_meta(f) for f in agents}
    copies = find_repo_copies()
    # mentions of scratch paths, writes with full content, and program outputs
    mentions = collections.defaultdict(list)     # path -> [(ts, f, id)]
    full_text = {}                                # path -> (ts, f, id, how)
    produced = {}                                 # path -> (ts, f, id)
    for c in calls:
        ts = c.get("ts") or ""
        if c["tool"] == "Write":
            try:
                inp = json.loads(c.get("inp") or "{}")
                fp = inp.get("file_path")
                if fp:
                    full_text[os.path.normpath(fp)] = (ts, c["f"], c["id"], "Write tool (full content in the call)")
                    mentions[os.path.normpath(fp)].append((ts, c["f"], c["id"]))
            except Exception:
                pass
            continue
        cmd = c.get("cmd")
        if cmd:
            env = shell_env(cmd)
            # here-documents written to a file keep the full text in the command
            for m in re.finditer(r"cat\s+>\s*(\S+)\s+<<-?\s*['\"]?(\w+)", cmd):
                fp = expand_vars(m.group(1).strip("\"'"), env)
                if fp.startswith("/"):
                    full_text[os.path.normpath(fp)] = (ts, c["f"], c["id"], "here-document (full content in the command)")
            for m in re.finditer(r"(?:>|>>|--out(?:-dir)?|--out-file|-o)\s*=?\s*(\"[^\"]+\"|'[^']+'|[^\s;&|)]+)", cmd):
                fp = expand_vars(m.group(1).strip("\"'"), env)
                if fp.startswith("/") and not fp.startswith("/dev/"):
                    produced.setdefault(os.path.normpath(fp), (ts, c["f"], c["id"]))
            for m in re.finditer(r"\$\{?[A-Za-z_]\w*\}?/[^\s\"'`|;&<>(){}\\,]+|" + PATH_RE.pattern, cmd):
                fp = expand_vars(m.group(0), env)
                if fp.startswith(SCRATCH):
                    fp = re.sub(r":\d+(?::\d+)?$", "", fp.rstrip("./:"))
                    mentions[os.path.normpath(fp)].append((ts, c["f"], c["id"]))
        res = c.get("res") or ""
        if SCRATCH in res:
            for m in PATH_RE.finditer(res):
                fp = re.sub(r":\d+(?::\d+)?$", "", m.group(0).rstrip("./:"))
                mentions[os.path.normpath(fp)].append((c.get("rts") or ts, c["f"], c["id"]))
    mention_paths = sorted(mentions)
    import bisect

    def under(t):
        lo = bisect.bisect_left(mention_paths, t)
        out = []
        for i in range(lo, len(mention_paths)):
            p = mention_paths[i]
            if p == t or p.startswith(t + "/"):
                out.append(p)
            elif p > t + "/￿":
                break
        return out

    events = []
    for c in calls:
        cmd = c.get("cmd")
        if not cmd:
            continue
        body = strip_heredocs(cmd)
        ops = [(m.group(1).strip(), m.start(1)) for m in DEL_RE.finditer(body)]
        code = CODE_DEL_RE.search(cmd)
        if not ops and not code:
            continue
        res = c.get("res") or ""
        denied = bool(re.search(r"Permission for this (?:action|command) was denied", res[:600]))
        for op, pos in ops:
            # the op's position in the full command (here-documents removed above keep earlier text)
            fpos = cmd.find(op)
            targets, d = deletion_targets(cmd, op, fpos if fpos >= 0 else len(cmd), c.get("cwd"))
            for t, k in targets:
                cls = classify_target(t, k)
                recreated = bool(k == "path" and re.search(r"(mkdir\s+-p\s+|git\s+archive[^|]*\|\s*tar[^\n;]*-C\s+|worktree\s+add\s+\S*\s*)" + re.escape(os.path.basename(t)), cmd[fpos:] if fpos >= 0 else cmd))
                events.append({"ts": c["ts"], "f": c["f"], "ln": c["ln"], "id": c["id"], "op": op[:300], "target": t,
                               "class": cls, "denied": denied, "recreated": recreated, "who": "orchestrator" if c["f"] == "main.jsonl" else "agent",
                               "agent": (metas.get(c["f"]) or {}).get("description", "") if c["f"] != "main.jsonl" else "",
                               "exists_now": os.path.lexists(t) if k == "path" else None})
        if code:
            events.append({"ts": c["ts"], "f": c["f"], "ln": c["ln"], "id": c["id"], "op": "code: " + code.group(0)[:200], "target": "(files a script removes)",
                           "class": "removed by a script", "denied": denied, "recreated": False,
                           "who": "orchestrator" if c["f"] == "main.jsonl" else "agent",
                           "agent": (metas.get(c["f"]) or {}).get("description", "") if c["f"] != "main.jsonl" else "", "exists_now": None})
    events.sort(key=lambda e: (e["ts"] or "", e["f"], e["ln"]))
    # a loop over `git worktree list`: the worktrees the last listing before it printed
    for e in events:
        if e["class"] == "loop" and "worktree" in e["op"]:
            prior = [c for c in calls if c["f"] == e["f"] and (c.get("cmd") or "").find("worktree list") >= 0 and (c["ts"] or "") < e["ts"]]
            paths = []
            if prior:
                last = prior[-1]
                for line in (last.get("res") or "").split("\n"):
                    m = re.match(r"\s*(?:worktree\s+)?(\S*/\.claude/worktrees/\S+)", line)
                    if m and m.group(1) not in paths:
                        paths.append(m.group(1))
                e["resolved"] = {"from": f"{last['f']} line {last.get('rln')} ({last['id']}) at {fmt_ts(last['ts'])}", "worktrees": paths}
    # what each removed scratch or repository target held, and what survives
    detail = []
    for e in events:
        if e["denied"] or e["class"] not in ("scratch folder or file", "repository file or folder", "worktree"):
            continue
        t = e["target"]
        held = [p for p in under(t) if any(ts < (e["ts"] or "") for ts, _, _ in mentions[p])]
        files = [p for p in held if os.path.splitext(p)[1]]
        users = collections.Counter()
        for p in held:
            for ts, f, i in mentions[p]:
                if ts < (e["ts"] or ""):
                    users[f] += 1
        in_text = [p for p in files if p in full_text and full_text[p][0] < e["ts"]]
        prog = [p for p in files if p in produced and produced[p][0] < e["ts"] and p not in in_text]
        copy_info = None
        for cd, info in copies.items():
            if cd == t or t.startswith(cd + "/") or cd.startswith(t + "/"):
                if info["ts"] < e["ts"]:
                    copy_info = info
        git_hist = None
        git_later = None
        saved_in_git = []
        if e["class"] == "repository file or folder":
            rel = os.path.relpath(t, REPO)
            h = git("log", "--all", "-1", f"--before={e['ts']}", "--format=%h %cI %s", "--", rel, check=False).strip()
            git_hist = h or None
            h2 = git("log", "--all", "-1", "--format=%h %cI %s", "--", rel, check=False).strip()
            git_later = h2 if h2 and h2 != h else None
        if e["class"] == "worktree":
            name = os.path.basename(t)
            seen = set()
            cur = None
            for line in git("log", "--all", "--format=@@%h %cI", "--name-only", check=False).splitlines():
                if line.startswith("@@"):
                    cur = line[2:]
                elif name in line and line not in seen:
                    seen.add(line)
                    saved_in_git.append(f"{line} (commit {cur})")
                if len(saved_in_git) >= 6:
                    break
        # saved reports beside the folder that still exist (review-WS3-28.txt beside review-WS3-28)
        related = []
        par, base = os.path.dirname(t), os.path.basename(t)
        ids = re.findall(r"(?:WS\d-\d+(?:-\d+)*|B\d{2}|f\d{2}|[A-Z]\d{1,2})", base)
        if os.path.isdir(par) and base:
            for fn in sorted(os.listdir(par)):
                q = os.path.join(par, fn)
                if q == t or not os.path.isfile(q):
                    continue
                stem = os.path.splitext(fn)[0]
                if stem == base or fn.startswith(base + ".") or (fn.startswith(base + "-") and not fn[len(base) + 1:len(base) + 2].isdigit()) or (ids and any(re.search(r"(?<![\w-])" + re.escape(i) + r"(?![\w-]|-\d)", fn) for i in ids)):
                    related.append(os.path.relpath(q, SCRATCH) if q.startswith(SCRATCH) else q)
        detail.append({**e, "n_agents": sum(1 for f in users if f != "main.jsonl"), "related_saved": related[:20], "held_paths": len(held), "held_files": files[:60], "n_files": len(files),
                       "agents": [{"f": f, "desc": (metas.get(f) or {}).get("description", "") if f != "main.jsonl" else "orchestrator", "mentions": n,
                                   "final_report": bool((agents.get(f) or {}).get("final_text") or (agents.get(f) or {}).get("handback"))} for f, n in users.most_common(12)],
                       "full_text_in_transcript": in_text[:60], "n_full_text": len(in_text),
                       "program_outputs": prog[:60], "n_program_outputs": len(prog),
                       "git_archive_copy": ({"rev": copy_info["rev"], "made": copy_info["ts"], "proof": f"{copy_info['f']} line {copy_info['ln']}"} if copy_info else None),
                       "git_history": git_hist, "git_later": git_later, "saved_in_git": saved_in_git})
    # agents the main conversation names whose transcripts are not on this machine
    present = set()
    for root, dirs, fs in os.walk(os.path.join(SESSION_DIR, "subagents")):
        for fn in fs:
            m = re.match(r"agent-([0-9a-f]{17})\.jsonl$", fn)
            if m:
                present.add(m.group(1))
    named = {}
    for c in calls:
        if c["f"] != "main.jsonl":
            continue
        blob = (c.get("inp") or c.get("cmd") or "") + "\n" + (c.get("res") or "")
        for m in re.finditer(r"(?:agentId[\"':\s]+|agent-|tasks/)(a[0-9a-f]{16})\b", blob):
            aid = m.group(1)
            if aid not in named:
                desc = None
                if c["tool"] in ("Agent", "Task"):
                    try:
                        desc = json.loads(c.get("inp") or "{}").get("description")
                    except Exception:
                        desc = None
                named[aid] = {"id": aid, "first_named": c["ts"], "where": f"main.jsonl line {c['ln']} ({c['id']})", "desc": desc}
            elif not named[aid].get("desc") and c["tool"] in ("Agent", "Task"):
                try:
                    named[aid]["desc"] = json.loads(c.get("inp") or "{}").get("description")
                except Exception:
                    pass
    missing_agents = sorted([v for k, v in named.items() if k not in present], key=lambda v: v["first_named"] or "")
    out = {"made_at": iso(), "events": events, "detail": detail, "missing_agent_transcripts": missing_agents,
           "agents_named": len(named), "agents_present": len(present)}
    write_json(os.path.join(WORK, "deletions.json"), out)
    render_deletions_md(out)
    log(f"deletions: {len(events)} targets in {len(set(e['id'] for e in events))} commands; {len(detail)} with content analysed")


# Facts found by reading the transcripts by hand, added to DELETIONS.md as they stand (keep them on a re-run).
HAND_NOTES = [
    "The worktree `.claude/worktrees/approval-fixes` removed on 9 November at 23:26 had been made 7 seconds earlier "
    "(`main.jsonl` line 9116, `git worktree add --detach .claude/worktrees/approval-fixes HEAD`) while the disk was full "
    "(18 MB free, line 9123), so it held no work. It was made again at 23:31 (line 9175). Its work was saved as "
    "`docs/signoff/work/central/approval-fixes-wip.patch` on 10 November at 01:01 (line 9721, commit ad7a9c5), merged "
    "(commits 0c54790 and 69eaa56), and the patch file was then removed with `git rm`; it is still in git history. "
    "The branch `approval-fixes-wip` was deleted at 08:30 (line 10594) after that merge. Nothing of it is lost.",
    "The statements of 7 October at 07:19 and 07:31 that \"all 615 biomarker tests pass\" (`main.jsonl` lines 649 and "
    "730) have no run in the main transcript. That morning's agents (among them the TypeScript port of the vitamin D "
    "add-on, `ae21970f4ffee4cd9`, and the sealed-test verifier, `a637ab0a591207f3e`) have no transcript on this machine, "
    "so the proof of those two statements is lost from the local record.",
]


def render_deletions_md(d):
    ev, det = d["events"], d["detail"]
    main = [e for e in ev if e["who"] == "orchestrator"]
    ag = [e for e in ev if e["who"] == "agent"]
    L = ["# Deletions in this session", "",
         f"AI work product. Made by `make-evidence.py` on {d['made_at']} from the transcripts. It lists every command that",
         "removed files, folders, worktrees or branches (`rm`, `rmdir`, `git worktree remove`, `git worktree prune`,",
         "`git branch -D`, `git rm`, `find -delete` or `-exec rm`, and scripts that call a remove function), when it ran,",
         "who ran it, what the target held as far as the transcripts show, and whether its proof survives elsewhere.",
         "No connector call deleted anything (no Gmail, Drive, Supabase, GitHub or Artifact delete was made).", "",
         "How \"what it held\" is found: every path under the target that a command or an output mentioned before the",
         "deletion. A file written with the Write tool or with a here-document has its full text in the transcript, so it",
         "survives there. A file a program wrote (a log, a JSON result) survives only as far as its output was printed.", ""]
    # summary of what is lost
    lost = [x for x in det if x["who"] == "orchestrator" and x["n_program_outputs"]]
    L += ["## Summary", "",
          f"- {len(set(e['id'] for e in main))} orchestrator commands removed {len(main)} targets; {len(set(e['id'] for e in ag))} agent commands removed {len(ag)} targets.",
          f"- Refused by the safety checks (nothing removed): " + str(sum(1 for e in ev if e["denied"])) + " targets, including every attempt to sweep `/tmp/dsrt-*`.",
          "- The 13,740 `/tmp/dsrt-*` test fixtures were never deleted; they are listed in `dsrt-fixtures.md`.", ""]
    lost_o = [x for x in det if x["who"] == "orchestrator"]
    lost_a = [x for x in det if x["who"] == "agent"]
    n_lost = sum(x["n_program_outputs"] for x in lost_o)
    n_kept = sum(x["n_full_text"] for x in lost_o)
    L += ["### What is lost, plainly", "",
          f"- **Lost:** {n_lost} files that programs wrote into the folders the orchestrator deleted (test and DSRT logs, JSON",
          "  results, compiles, downloaded pages). The commands that made them survive in the transcripts, and so does",
          "  whatever those commands printed. The files themselves do not survive, so a number that was only written to such",
          "  a file, and never printed, cannot be checked any more. Re-running the command at its commit rebuilds the file.",
          f"- **Kept in the transcripts:** {n_kept} files in those folders were written with the Write tool or a here-document,",
          "  so their full text is in the transcript (scripts, probes, mutation scripts, briefs).",
          "- **Kept elsewhere:** every agent that worked in a deleted folder still has its transcript, with its final report",
          "  where it wrote one; reviews the orchestrator saved beside the folders (for example",
          "  `scratchpad/ws3-wave2/review-WS3-28.txt`) are in the scratch archive; results that were committed are in git.",
          f"- Agents' own deletions removed {sum(x['n_program_outputs'] for x in lost_a)} program-written files that were not re-made; most agent deletions",
          "  cleared temporary folders or copies they re-made at once.", "",
          "| Deleted (UTC) | Folder | Files named before | Full text in a transcript | Program files lost | Saved beside it | Agents who worked there |",
          "|---|---|---|---|---|---|---|"]
    for x in sorted(lost_o, key=lambda x: x["ts"] or ""):
        if not x["n_files"] and not x["agents"]:
            continue
        rel = os.path.relpath(x["target"], SCRATCH) if x["target"].startswith(SCRATCH) else x["target"]
        L.append(f"| {fmt_ts(x['ts'])} | `{md_escape(rel)}` | {x['n_files']} | {x['n_full_text']} | {x['n_program_outputs']} | {', '.join('`' + p + '`' for p in (x.get('related_saved') or [])[:3]) or 'none'} | {x.get('n_agents', 0)} |")
    L.append("")
    L += ["## 1. Deletions by the orchestrator", "",
          "| When (UTC) | Command | Target | Kind | Result | Proof |", "|---|---|---|---|---|---|"]
    for e in main:
        res = "refused, nothing removed" if e["denied"] else ("removed, then re-created by the same command" if e["recreated"] else "removed")
        if e["exists_now"]:
            res += "; something exists at that path now (made again later)"
        tgt = e["target"]
        if e.get("resolved"):
            r = e["resolved"]
            tgt = tgt + "; the last listing before it (" + r["from"] + ") shows " + (", ".join(os.path.basename(x) for x in r["worktrees"]) or "no worktree under .claude/worktrees")
        L.append(f"| {fmt_ts(e['ts'])} | `{md_escape(e['op'][:120])}` | `{md_escape(tgt)}` | {e['class']} | {res} | `{e['f']}` line {e['ln']}, `{e['id']}` |")
    L += ["", "## 2. What the orchestrator's deletions held, and what survives", ""]
    for x in det:
        if x["who"] != "orchestrator":
            continue
        L.append(f"### {fmt_ts(x['ts'])} `{x['target']}`")
        L.append("")
        L.append(f"- Command: `{md_escape(x['op'][:200])}` (`{x['f']}` line {x['ln']}, `{x['id']}`)" + ("; re-created by the same command" if x["recreated"] else ""))
        if x.get("git_archive_copy"):
            g = x["git_archive_copy"]
            L.append(f"- It was a copy of the repository made with `git archive {g['rev']}` at {fmt_ts(g['made'])} ({g['proof']}). The committed files survive in git; only changes made inside the copy were lost.")
        if x.get("git_history"):
            L.append(f"- In git history before the deletion: `{x['git_history']}`; that committed version survives there.")
        elif x["class"] == "repository file or folder":
            L.append("- Not committed before it was deleted: the deleted version survives only as far as a transcript printed it.")
        if x.get("git_later"):
            L.append(f"- Made again and committed later: `{x['git_later']}`.")
        if x["class"] == "worktree":
            L.append("- A worktree: what it committed survives in its branch; changes it never committed were lost with the folder.")
            if x.get("saved_in_git"):
                L.append("- Files named after it in git history: " + "; ".join(f"`{p}`" for p in x["saved_in_git"]))
        L.append(f"- The transcripts mention {x['held_paths']} paths under it before the deletion, {x['n_files']} of them files.")
        if x["agents"]:
            L.append("- Worked in by: " + "; ".join(f"`{a['f']}` ({md_escape(a['desc'][:70])}, {a['mentions']} mentions{', final report kept' if a['final_report'] and a['f'] != 'main.jsonl' else ''})" for a in x["agents"][:8]))
        if x.get("related_saved"):
            L.append("- Saved beside it and still there: " + ", ".join(f"`scratchpad/{p}`" for p in x["related_saved"]))
        if x["n_full_text"]:
            L.append(f"- {x['n_full_text']} files have their full text in a transcript (Write tool or here-document), so they survive there: " + ", ".join(f"`{os.path.relpath(p, x['target']) if p.startswith(x['target']) else p}`" for p in x["full_text_in_transcript"][:12]) + (" …" if x["n_full_text"] > 12 else ""))
        if x["n_program_outputs"]:
            L.append(f"- **{x['n_program_outputs']} files were written by programs and are gone; only what their commands printed survives in the transcripts:** " + ", ".join(f"`{os.path.relpath(p, x['target']) if p.startswith(x['target']) else p}`" for p in x["program_outputs"][:15]) + (" …" if x["n_program_outputs"] > 15 else ""))
        other = [p for p in x["held_files"] if p not in x["full_text_in_transcript"] and p not in x["program_outputs"]]
        if other:
            L.append(f"- Other files named in the transcripts (copied in, or of unknown origin): " + ", ".join(f"`{os.path.relpath(p, x['target']) if p.startswith(x['target']) else p}`" for p in other[:12]) + (" …" if len(other) > 12 else ""))
        L.append("")
    # agents
    L += ["## 3. Deletions by agents", "",
          "Agents cleared their own working folders: temporary folders before a run, copies of the repository before",
          "making a fresh one, probe and mutation files they had added to a copy. The table groups them by kind.", ""]
    kinds = collections.Counter(e["class"] for e in ag)
    L += ["| Kind | Targets | Refused | Re-created by the same command |", "|---|---|---|---|"]
    for k, v in kinds.most_common():
        L.append(f"| {k} | {v} | {sum(1 for e in ag if e['class'] == k and e['denied'])} | {sum(1 for e in ag if e['class'] == k and e['recreated'])} |")
    L += ["", "Every agent deletion of something other than temporary files:", "",
          "| When (UTC) | Agent | Command | Target | Kind | Proof |", "|---|---|---|---|---|---|"]
    for e in ag:
        if e["class"] == "temporary files":
            continue
        L.append(f"| {fmt_ts(e['ts'])} | {md_escape(e['agent'][:60])} | `{md_escape(e['op'][:100])}` | `{md_escape(e['target'][:140])}` | {e['class']}{' (refused)' if e['denied'] else ''}{' (re-created)' if e['recreated'] else ''} | `{e['f']}` line {e['ln']} |")
    L += ["", "## 4. Records that are not in the local copy", "",
          "- **The session before 7 October 2026, 06:12 UTC.** The session was created on 22 September 2026",
          f"  ({CLOUD_SESSION}). The local main transcript starts at a compaction boundary on 7 October; the earlier",
          "  conversation is only in the summary at line 2. Its tool calls, outputs and any agent transcripts of that period",
          "  are not on this machine. They may survive on claude.ai; they are not in this record.",
          "- **Worktrees the Workflow tool made** (`.claude/worktrees/wf_*`) are gone. Their own branches (`worktree-wf_*`)",
          "  never moved from the base commit c472974: each agent checked out a branch of its own and committed there",
          "  (`signoff-b01-evidence`, `signoff-runner-r4`, `-r4-verify`, `-r4-repair`, `-r4-repair-verify`, `signoff-runner-r5`,",
          "  `-r5-verify`, `-r5-repair`, `-r5-verify-repair`). Those branches remain (MANIFEST.md, section 6), so what the",
          "  agents committed survives. Changes they never committed are not recoverable.",
          "- **Background agents' scratch copies** listed above under the orchestrator's deletions: the files were removed;",
          "  the agents' transcripts survive with every command and every printed output.", ""]
    miss = d.get("missing_agent_transcripts") or []
    L += [f"### Agents whose transcripts are not on this machine", "",
          f"The main conversation names {d.get('agents_named', 0)} agents; {d.get('agents_present', 0)} agent transcripts are on this machine.",
          f"{len(miss)} named agents have no transcript here. Their commands and outputs are lost from the local record; what",
          "reached the main conversation (their final report or task notification) is in the main transcript.", "",
          "| Agent | First named (UTC) | What it was | Where it is named |", "|---|---|---|---|"]
    for m in miss:
        L.append(f"| `{m['id']}` | {fmt_ts(m['first_named'])} | {md_escape(m.get('desc') or 'not recorded')} | {m['where']} |")
    if not miss:
        L.append("| none | | | |")
    L.append("")
    L += ["## 5. Checked by hand", "",
          "These facts come from reading the transcripts, not from the automatic analysis above.", ""]
    L += ["- " + n for n in HAND_NOTES]
    L.append("")
    write_text(os.path.join(OUT, "DELETIONS.md"), "\n".join(L) + "\n")


def short_cmd(cmd, kinds, limit=600):
    if len(cmd) <= limit and cmd.count("\n") <= 8:
        return cmd, False
    body = strip_heredocs(cmd)
    keep = []
    for line in body.split("\n"):
        if any(rx.search(line) for name, rx in KINDS if name in kinds) or re.search(r"^\s*cd\s", line):
            keep.append(line)
    s = "\n".join(keep)[:1500] if keep else cmd[:limit]
    return s, True


def render_tests_md(d):
    runs, agents, wfs, st = d["runs"], d["agents"], d["workflows"], d["statements"]
    kinds = collections.Counter(k for r in runs for k in r["kinds"])
    by_day = collections.Counter((r["ts"] or "")[:10] for r in runs)
    who = collections.Counter("orchestrator" if r["f"] == "main.jsonl" else "agents" for r in runs)
    stc = collections.Counter(s["status"] for s in st)
    L = ["# Tests and checks: the summary", "",
         f"AI work product. Made by `make-evidence.py` on {d['made_at']} from the transcript snapshot of {d['snapshot_taken_at']}.",
         "It records what was run and what it printed. Nothing here was re-run.", "",
         "## How to read it", "",
         "- Every entry comes from a tool call in the session transcripts: the exact command, the time, the folder it ran in,",
         "  the commit that folder held then, what the command printed, and where the proof is",
         "  (transcript file, line and tool-call id). The transcripts are in `transcripts/` (see README.md).",
         "- The outcome is read from each tool's own summary line: vitest `Tests ... passed`, `node --test` `# pass`,",
         "  tsc `error TS`, eslint `problems`, the DSRT runner `round N: pass, fail, blocked` (or the counts a helper printed),",
         "  `validate.js` VALID or INVALID, `quote-check.js` found of total, `compile.js` its JSON line, and exit codes the",
         "  command echoed. When the output was cut by `tail` or `grep`, the summary says what was shown.",
         "- The commit is HEAD of that checkout at that minute, from the git reflogs (main checkout and worktrees), from the",
         "  branch reflog for a worktree since removed, or from the first-parent history before the reflog starts",
         "  (28 October). The working tree may also have held changes not yet committed. A run in a scratch copy shows the",
         "  commit the copy was made from, when the copy was made with `git archive`.",
         "- The transcript begins on 7 October 2026 at 06:12 UTC. The session itself was created on 22 September 2026; what",
         "  happened before 7 October is only in the summary at line 2 of the main transcript and on claude.ai.", "",
         "## Totals", "",
         f"- {len(runs)} check runs: {who['orchestrator']} by the orchestrator in the main conversation, {who['agents']} by agents.",
         f"- {len(agents)} agent transcripts with their final reports; {len(wfs)} workflow runs with their returned results.",
         f"- {len(st)} statements of a result made to the CEO in the main conversation: " + ", ".join(f"{v} {k}" for k, v in stc.most_common()) + ".",
         "", "| Kind | Runs |", "|---|---|"]
    for k, v in kinds.most_common():
        L.append(f"| {KIND_LABEL.get(k, k)} | {v} |")
    L += ["", "| Day (UTC) | Runs |", "|---|---|"]
    for k in sorted(by_day):
        L.append(f"| {k} | {by_day[k]} |")
    # statements
    L += ["", "## 1. Results stated to the CEO, and their proof", "",
          "Each line is a sentence or table row of an assistant message in the main conversation that states a result.",
          "\"traced\": one earlier proof item holds every number in it. \"partly traced\": the best item holds most of them; the",
          "missing numbers are listed. \"no numbers; nearest earlier run\": a result stated in words; the nearest earlier run is",
          "shown and should be read to confirm it. \"not traced\": no earlier proof item holds its numbers.",
          "Matching is by numbers, so a traced line is a strong pointer, not a proof of meaning: open the proof to confirm.", ""]
    for s in st:
        L.append(f"- **{fmt_ts(s['ts'])}** (main.jsonl line {s['ln']}) {md_escape(s['claim'][:500])}")
        if s.get("proof"):
            extra = f"; missing {', '.join(s['missing'])}" if s.get("missing") else ""
            L.append(f"  - {s['status']}: {md_escape(s['proof'])} at {fmt_ts(s.get('proof_ts'))}{extra}")
        else:
            L.append(f"  - {s['status']}" + (f": none of {', '.join(s.get('missing', []))} appears in an earlier proof item" if s.get("missing") else ""))
    nt = [s for s in st if s["status"] == "not traced"]
    L += ["", "## 2. Statements that could not be traced", "",
          f"{len(nt)} statements. Each needs its proof found by hand, or a correction.", ""]
    for s in nt:
        L.append(f"- {fmt_ts(s['ts'])} (main.jsonl line {s['ln']}): {md_escape(s['claim'][:400])}")
    # reviews and agents
    L += ["", "## 3. Agents: reviews, verdicts and final reports", "",
          "Every agent transcript, in the order the agents started. The verdict words are read from the final report or the",
          "structured output; the excerpt is the start of the final report. \"stopped\" marks an agent that ended on a usage",
          "limit before it finished: its review did not happen.", "",
          "| Started (UTC) | Agent | Phase | Model | Checks run | Verdict or result | Proof |", "|---|---|---|---|---|---|---|"]
    for a in agents:
        v = a["verdict"]
        vt = v["stopped"] or "; ".join(v["words"] + v["structured"]) or ""
        ex = md_escape(v["excerpt"][:260])
        where = f"`{a['f']}` line {a['final_ln']} ({a['report_source']})" if a.get("final_ln") else f"`{a['f']}` (no report in the transcript)"
        L.append(f"| {fmt_ts(a['first_ts'])} | {md_escape(a['desc'][:90])} | {a.get('phase') or a.get('type') or ''} | {md_escape(str(a.get('model') or ''))} | {a['n_checks']} | {md_escape(vt)}{' — ' if vt and ex else ''}{ex} | {where} |")
    L += ["", "## 4. Workflow runs and what they returned", "",
          "| Started (UTC) | Workflow | Status | Agents | Minutes | Summary | Proof |", "|---|---|---|---|---|---|---|"]
    for w in wfs:
        L.append(f"| {fmt_ts(w['ts'])} | {md_escape(w['name'])} | {w['status']} | {w['agents']} | {w['duration_min']} | {md_escape((w['summary'] or '')[:200])} | `{w['f']}`" + (f"; each agent's returned result in `{w['journal']}`" if w.get("journal") else "") + " |")
    # every run
    L += ["", "## 5. Every check run, in time order", "",
          "Times are UTC. \"Proof\" gives the transcript file and the line of the result, and the tool-call id. A long command",
          "shows only its lines that run a check or change folder; tests.json has every command in full.", ""]
    day = None
    for r in runs:
        dday = (r["ts"] or "")[:10]
        if dday != day:
            day = dday
            L += ["", f"### {day}", ""]
        cmd, cut = short_cmd(r["cmd"], r["kinds"])
        kinds_s = ", ".join(KIND_LABEL.get(k, k) for k in r["kinds"])
        L.append(f"**{r['n']}. {fmt_ts(r['ts'])}** · {kinds_s} · {md_escape(r['who'])}")
        cm = r["commit"][:12] if r["commit"] else ("unknown; the main checkout was at " + r["main_at"][:12] if r.get("main_at") else "unknown")
        L.append(f"- where: `{r['dir'] or '?'}` ({r['where'] or 'unknown'}); commit: {cm}")
        L.append(f"- outcome: {md_escape(r['summary'])}")
        proof = f"`{r['f']}` line {r['rln'] or r['ln']}, call `{r['id']}`"
        if r.get("background_output"):
            proof += f"; background output `{r['background_output']}`"
        if r.get("persisted"):
            proof += f"; full output `{r['persisted']}`"
        L.append(f"- proof: {proof}")
        fence = "~~~~" if "```" in cmd or "~~~" in cmd else "```"
        L.append(f"- command{' (the lines that run checks; ' + str(r['cmd_lines']) + ' lines in full)' if cut else ''}:")
        L.append("")
        L.append(fence + "sh")
        L.append(cmd)
        L.append(fence)
        L.append("")
    write_text(os.path.join(OUT, "TESTS-SUMMARY.md"), "\n".join(L) + "\n")


# ----------------------------------------------------------------------------------------
# Step: repo (committed proof, worktrees, branches, cloud sessions)
# ----------------------------------------------------------------------------------------
# (pattern on the repository path, workstream, what it proves); first match wins
PROOF_RULES = [
    (r"^docs/signoff/(PLAN|ACCEPTANCE-TEST|LOOP-PROMPT)\.md$", "WS0 gates and plan", "The programme's plan, the frozen acceptance test (DSRT) and the agents' prompts as written"),
    (r"^docs/signoff/thresholds\.json$", "WS0 gates and plan", "The DSRT pass thresholds, frozen"),
    (r"^docs/signoff/workflows/", "WS0 gates and plan", "The workflow scripts that ran the batch loops"),
    (r"^docs/signoff/tools/test/", "WS0 gates and plan", "Tests of the frozen sign-off tools (run with node --test)"),
    (r"^docs/signoff/tools/", "WS0 gates and plan", "The frozen sign-off tools: compile, validate, quote-check, ledger, ownership, scorecard"),
    (r"^docs/signoff/work/scorecard-B(\d\d)\.md$", "WS1 ranges by family", "Batch scorecard: agents, models, rounds, check results and verdicts for the batch"),
    (r"^docs/signoff/work/checks/", "WS1 ranges by family", "DSRT results saved for a round or batch (check by check, with counts)"),
    (r"^docs/signoff/work/research/", "WS1 ranges by family", "Author's research file for a family: rows and evidence records"),
    (r"^docs/signoff/work/verify/", "WS1 ranges by family", "Verifier's file for a family: verdicts, grades and its own evidence"),
    (r"^docs/signoff/work/judges/", "WS1 ranges by family", "A judge's review of a batch: issues raised and severity"),
    (r"^docs/signoff/work/refutations/", "WS1 ranges by family", "A refuter's verdict on one judge issue (confirmed or refuted)"),
    (r"^docs/signoff/work/ledger/", "WS1 ranges by family", "The issue ledger of a family: every issue and its state"),
    (r"^docs/signoff/work/decisions/", "WS1 ranges by family", "Fixer's decision file for a family: the rows decided and why"),
    (r"^docs/signoff/work/briefs/", "WS1 ranges by family", "Briefs given to the agents of a family"),
    (r"^docs/signoff/work/inputs/", "WS1 ranges by family", "Inputs given to the agents: live rows, the lab's intervals"),
    (r"^docs/signoff/work/questions/", "WS1 ranges by family", "Questions for the physician raised by a family"),
    (r"^docs/signoff/work/sources-cache/", "WS1 ranges by family", "Cached source text that quote-check matched the quotes against"),
    (r"^docs/signoff/work/compiled/", "WS1-K compile", "A compile of the seed files from the decided families (the input of a DSRT run)"),
    (r"^docs/signoff/work/reconciliation/", "WS1-K compile", "Reconciliation of the compiled rows with production"),
    (r"^docs/signoff/work/central/", "Central reviews and approvals", "Central reviews, approvals and known issues of the runner and tools"),
    (r"^docs/signoff/work/governance/", "Governance", "Governance records: decision register, approvals, wording rules, critical limits, rulings"),
    (r"^docs/signoff/work/ws3/", "WS3 score", "Workstream 3 design and the result of each merge"),
    (r"^docs/signoff/work/score/", "WS3 score", "Score regression and checks"),
    (r"^docs/signoff/work/mopup/", "WS1 mop-up round", "The mop-up round's plan and decisions"),
    (r"^docs/signoff/work/v3/", "WS2 biological age v3", "Version 3 sign-off documents"),
    (r"^docs/signoff/work/nhanes/", "WS3 score", "NHANES population data used by the population checks"),
    (r"^docs/signoff/work/", "WS0 gates and plan", "Programme working record"),
    (r"^scripts/signoff/", "WS0 gates and plan", "The DSRT runner and its checks (scripts/signoff/dsrt.ts)"),
    (r"^src/lib/signoff/", "WS0 gates and plan", "Unit tests of the DSRT runner (vitest)"),
    (r"^scripts/governance/", "Governance", "Scripts that generate governance tables"),
    (r"^scripts/", "Biological age and score analyses", "Analysis and validation scripts"),
    (r"^ml/biological-age/(verifier|harness)/", "WS2 biological age v3", "Independent verification and test harness of the biological-age model, with results"),
    (r"^ml/biological-age/addons/", "Biological age add-ons (October)", "The add-on programme: charter, harness, verifier and results"),
    (r"^ml/biological-age/results/", "WS2 biological age v3", "Frozen model results and diagnostics"),
    (r"^ml/biological-age/", "WS2 biological age v3", "The biological-age model, its card, report, proposal and sign-off documents"),
    (r"^docs/biomarker-evidence/", "Biomarker evidence (October)", "Per-biomarker research, verification and longevity review"),
    (r"^docs/audit/", "Audit and calibration reports", "Audit reports"),
    (r"^audit/", "Audit and calibration reports", "Independent audits of the biological age and the longevity score"),
    (r"^supabase/", "Seed data and migrations", "Seed data and prepared migrations (files; nothing applied in this programme)"),
    (r"^docs/", "Audit and calibration reports", "Programme documents"),
]


def proof_rule(path):
    for rx, ws, what in PROOF_RULES:
        m = re.search(rx, path)
        if m:
            if "scorecard-B" in rx:
                what = what.replace("the batch", "batch B" + m.group(1))
            return ws, what
    return "Other", "Repository file"


def git_blob_hashes(commit, paths):
    """sha256 of each blob, read through git cat-file (no working-tree reads)."""
    out = {}
    if not paths:
        return out
    p = subprocess.Popen(["git", "--no-optional-locks", "cat-file", "--batch"], cwd=REPO, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    for path, blob in paths:
        p.stdin.write((blob + "\n").encode())
        p.stdin.flush()
        header = p.stdout.readline().decode()
        parts = header.split()
        size = int(parts[2])
        data = p.stdout.read(size)
        p.stdout.read(1)
        out[path] = (size, hashlib.sha256(data).hexdigest())
    p.stdin.close()
    p.wait()
    return out


def step_repo():
    commit = git("rev-parse", BRANCH).strip()
    head = git("rev-parse", "HEAD").strip()
    taken = iso()
    # tracked files under the proof paths at that commit
    entries = []
    for line in git("ls-tree", "-r", "-z", commit, "--", *REPO_PROOF_PATHS).split("\0"):
        if not line:
            continue
        meta, path = line.split("\t", 1)
        mode, typ, blob = meta.split()
        if typ == "blob":
            entries.append((path, blob))
    hashes = git_blob_hashes(commit, entries)
    # the date each file last changed
    last = {}
    cur = None
    for line in git("log", "--format=@@%h %cI", "--name-only", commit, "--", *REPO_PROOF_PATHS).splitlines():
        if line.startswith("@@"):
            cur = line[2:].split()
        elif line.strip() and cur and line not in last:
            last[line] = (cur[0], cur[1])
    files = []
    for path, blob in entries:
        size, sha = hashes[path]
        ws, what = proof_rule(path)
        lc = last.get(path, (None, None))
        files.append({"path": path, "size": size, "sha256": sha, "git_blob": blob, "workstream": ws,
                      "proves": what, "last_commit": lc[0], "date": lc[1]})
    # not committed at the time (untracked or changed in the main checkout)
    pending = []
    st = git("status", "--porcelain", "--untracked-files=all", "--", *REPO_PROOF_PATHS, check=False)
    for line in st.splitlines():
        if len(line) > 3:
            pending.append({"state": line[:2].strip(), "path": line[3:]})
    # worktrees
    wts = []
    cur = {}
    for line in git("worktree", "list", "--porcelain").splitlines() + [""]:
        if not line.strip():
            if cur:
                wts.append(cur)
            cur = {}
            continue
        k, _, v = line.partition(" ")
        cur[k] = v or True
    wt_out = []
    for w in wts:
        path = w.get("worktree")
        br = (w.get("branch") or "").replace("refs/heads/", "")
        name = os.path.basename(path)
        inprog = name in IN_PROGRESS_WORKTREES or path == REPO and False
        # a worktree whose git index, HEAD or reflog changed in the last RECENT_MINUTES counts as in progress too
        if path != REPO and not inprog:
            try:
                gd = open(os.path.join(path, ".git")).read().split("gitdir:", 1)[1].strip()
                newest = max((os.path.getmtime(os.path.join(gd, x)) for x in ("index", "HEAD", "logs/HEAD") if os.path.exists(os.path.join(gd, x))), default=0)
                if newest >= time.time() - RECENT_MINUTES * 60:
                    inprog = True
            except Exception:
                pass
            try:
                rl = reflogs()["worktrees"].get(path) or []
                if rl and rl[-1][0] >= time.time() - RECENT_MINUTES * 60:
                    inprog = True
            except Exception:
                pass
        rec = {"path": path, "branch": br, "head": w.get("HEAD"), "in_progress": bool(inprog)}
        if br and br != BRANCH:
            log_lines = git("log", "--format=%h %cI %s", f"{commit}..{br}", check=False).strip().splitlines()
            rec["unmerged_commits"] = log_lines
            rec["head_subject"] = git("log", "-1", "--format=%h %cI %s", br, check=False).strip()
        if path != REPO and not inprog:
            s = git("-C", path, "status", "--porcelain", check=False) if os.path.isdir(path) else ""
            rec["uncommitted"] = s.strip().splitlines()[:200]
        elif inprog:
            rec["uncommitted"] = ["(not read: in progress)"]
        rl = reflogs()["worktrees"].get(path) or []
        if rl:
            rec["created"] = iso(dt.datetime.fromtimestamp(rl[0][0], dt.timezone.utc))
            rec["last_move"] = iso(dt.datetime.fromtimestamp(rl[-1][0], dt.timezone.utc))
            rec["last_move_what"] = rl[-1][2][:160]
        wt_out.append(rec)
    # every local branch
    br_out = []
    for line in git("for-each-ref", "--format=%(refname:short) %(objectname:short) %(committerdate:iso-strict)", "refs/heads").splitlines():
        name, sha, date = line.split(" ", 2)
        unmerged = git("log", "--format=%h %cI %s", f"{commit}..{name}", check=False).strip().splitlines() if name != BRANCH else []
        rl = reflogs()["branches"].get(name) or []
        br_out.append({"branch": name, "head": sha, "head_date": date, "unmerged_commits": unmerged,
                       "created": iso(dt.datetime.fromtimestamp(rl[0][0], dt.timezone.utc)) if rl else None})
    # cloud sessions this session started, and scheduled tasks it used
    calls = read_jsonl(os.path.join(IDX, "calls.jsonl"))
    sessions = {}
    for c in calls:
        if c["tool"] == "mcp__Claude_Code_Remote__create_session":
            try:
                inp = json.loads(c.get("inp") or "{}")
            except Exception:
                inp = {}
            m = re.search(r'"id"\s*:\s*"(session_[A-Za-z0-9]+)"', c.get("res") or "")
            sid = m.group(1) if m else None
            if sid:
                sessions[sid] = {"id": sid, "title": inp.get("title"), "tags": inp.get("tags"), "created": c["ts"],
                                 "source_revision": inp.get("source_revision"), "outcome_branch": inp.get("outcome_branch"),
                                 "prompt_start": (inp.get("prompt") or "")[:600], "proof": f"{c['f']} line {c['ln']} ({c['id']})",
                                 "statuses": []}
    for c in calls:
        if c["tool"] in ("mcp__Claude_Code_Remote__get_session", "mcp__Claude_Code_Remote__list_sessions"):
            res = c.get("res") or ""
            for sid in sessions:
                if sid in res:
                    i = res.find(sid)
                    seg = res[i:i + 3000]
                    m = re.search(r'"session_status"\s*:\s*"([A-Z_]+)"', seg)
                    b = re.search(r'"status_bucket"\s*:\s*"([a-z_]+)"', seg)
                    u = re.search(r'"updated_at"\s*:\s*"([^"]+)"', seg)
                    if m:
                        sessions[sid]["statuses"].append({"at": c["ts"], "status": m.group(1), "bucket": b.group(1) if b else None,
                                                         "updated_at": u.group(1) if u else None, "proof": f"{c['f']} line {c.get('rln')} ({c['id']})"})
    for sid, s in sessions.items():
        tag = next((t for t in (s.get("tags") or []) if t.startswith("batch-")), None)
        bid = tag.split("-", 1)[1] if tag else None
        s["batch"] = bid
        if bid:
            s["commits"] = git("log", "--format=%h %cI %s", f"--grep={bid}", commit, check=False).strip().splitlines()[:40]
            sc = f"docs/signoff/work/scorecard-{bid}.md"
            s["scorecard"] = sc if os.path.exists(os.path.join(REPO, sc)) else None
    triggers = {}
    for c in calls:
        if c["tool"].startswith("mcp__Claude_Code_Remote__") and "trigger" in c["tool"]:
            try:
                inp = json.loads(c.get("inp") or "{}")
            except Exception:
                inp = {}
            tid = inp.get("trigger_id") or (re.search(r"trig_[A-Za-z0-9]+", c.get("res") or "") or [None])[0] if isinstance(re.search(r"trig_[A-Za-z0-9]+", c.get("res") or ""), re.Match) else inp.get("trigger_id")
            if not tid:
                m = re.search(r"trig_[A-Za-z0-9]+", c.get("res") or "")
                tid = m.group(0) if m else None
            if not tid:
                continue
            t = triggers.setdefault(tid, {"id": tid, "calls": 0, "first": c["ts"], "last": c["ts"], "names": [], "crons": [], "tools": collections.Counter()})
            t["calls"] += 1
            t["last"] = c["ts"]
            t["tools"][c["tool"].split("__")[-1]] += 1
            if inp.get("name") and inp["name"] not in t["names"]:
                t["names"].append(inp["name"])
            if inp.get("cron_expression") and inp["cron_expression"] not in t["crons"]:
                t["crons"].append(inp["cron_expression"])
    for t in triggers.values():
        t["tools"] = dict(t["tools"])
    out = {"taken_at": taken, "commit": commit, "head": head, "files": files, "pending": pending,
           "worktrees": wt_out, "branches": br_out, "sessions": list(sessions.values()), "scheduled_tasks": list(triggers.values())}
    write_json(os.path.join(WORK, "repo.json"), out)
    log(f"repo: {len(files)} committed proof files at {commit[:12]}; {len(pending)} not committed; {len(wt_out)} worktrees; {len(br_out)} branches; {len(sessions)} cloud sessions")


# ----------------------------------------------------------------------------------------
# Step: dsrt (the /tmp/dsrt-* fixtures, listed, never copied)
# ----------------------------------------------------------------------------------------
def fixture_makers():
    """Prefix -> where it is made, from the test files as they stood before the fix 2035fcb."""
    makers = collections.defaultdict(list)
    sources = []
    for rev, files in (("2035fcb^", ["src/lib/signoff/dsrt-core.test.ts", "src/lib/signoff/dsrt-checks.test.ts"]),
                       (BRANCH, ["scripts/signoff/checks/governance.ts", "scripts/signoff/lib/runner.ts", "scripts/signoff/dsrt.ts"])):
        for f in files:
            txt = git("show", f"{rev}:{f}", check=False)
            if not txt:
                continue
            sources.append(f"{rev}:{f}")
            lines = txt.split("\n")
            test_name = None
            for i, line in enumerate(lines, 1):
                m = re.search(r"\b(?:it|test|describe)(?:\.\w+)?\(\s*[\"'`](.{1,140}?)[\"'`]", line)
                if m:
                    test_name = m.group(1)
                for m in re.finditer(r"mkdtempSync\(path\.join\(os\.tmpdir\(\),\s*[\"'`](dsrt-[^\"'`$]*?)-?[\"'`]", line):
                    makers[m.group(1).rstrip("-")].append({"where": f"{f}:{i}", "rev": rev, "test": test_name})
                m = re.search(r"mkdtempSync\(path\.join\(os\.tmpdir\(\),\s*`dsrt-\$\{(\w+)\}-`", line)
                if m:
                    makers["dsrt-${" + m.group(1) + "}"].append({"where": f"{f}:{i}", "rev": rev, "test": test_name})
                if "mkdtempSync" in line and "dsrt-e1-${commit}" in line:
                    makers["dsrt-e1-<commit>"].append({"where": f"{f}:{i}", "rev": rev, "test": test_name})
    return makers, sources


def step_dsrt():
    rows = []
    for name in sorted(os.listdir(DSRT_GLOB_DIR)):
        if not name.startswith(DSRT_PREFIX):
            continue
        p = os.path.join(DSRT_GLOB_DIR, name)
        try:
            st = os.lstat(p)
        except OSError:
            continue
        if not stat.S_ISDIR(st.st_mode):
            continue
        size = alloc = n = 0
        newest = st.st_mtime
        for root, dirs, fs in os.walk(p):
            for fn in fs:
                try:
                    s2 = os.lstat(os.path.join(root, fn))
                except OSError:
                    continue
                size += s2.st_size
                alloc += s2.st_blocks * 512
                n += 1
                newest = max(newest, s2.st_mtime)
        prefix = re.sub(r"-[A-Za-z0-9]{6}$", "", name)
        rows.append({"name": name, "prefix": prefix, "files": n, "bytes": size, "disk_bytes": alloc,
                     "made": iso(dt.datetime.fromtimestamp(st.st_mtime, dt.timezone.utc)),
                     "newest_file": iso(dt.datetime.fromtimestamp(newest, dt.timezone.utc))})
    makers, sources = fixture_makers()

    def maker_for(prefix):
        if prefix in makers:
            return makers[prefix]
        if re.match(r"dsrt-e1-[0-9a-f]{7}$", prefix):
            return makers.get("dsrt-e1-<commit>") or makers.get("dsrt-${name}") or []
        if re.match(r"dsrt-work-[0-9a-f]{7}$", prefix):
            return makers.get("dsrt-work") or []
        for k in sorted(makers, key=len, reverse=True):
            if k.startswith("dsrt-${"):
                continue
            if prefix.startswith(k + "-"):
                return makers[k]
        return makers.get("dsrt-${name}") or []

    by = collections.OrderedDict()
    for r in rows:
        g = by.setdefault(r["prefix"], {"prefix": r["prefix"], "folders": 0, "files": 0, "bytes": 0, "disk_bytes": 0, "first": r["made"], "last": r["made"]})
        g["folders"] += 1
        g["files"] += r["files"]
        g["bytes"] += r["bytes"]
        g["disk_bytes"] += r["disk_bytes"]
        g["first"] = min(g["first"], r["made"])
        g["last"] = max(g["last"], r["made"])
    for g in by.values():
        g["made_by"] = maker_for(g["prefix"])
    out = {"listed_at": iso(), "folder": DSRT_GLOB_DIR, "count": len(rows), "bytes": sum(r["bytes"] for r in rows),
           "disk_bytes": sum(r["disk_bytes"] for r in rows), "by_prefix": list(by.values()), "folders": rows,
           "makers_read_from": sources,
           "note": "Fixtures that src/lib/signoff/dsrt-core.test.ts and dsrt-checks.test.ts left in the system's temporary folder before commit 2035fcb (10 November 13:33 UTC), which points TMPDIR at one root per test file and removes it after the run. Listed only; never copied or deleted."}
    write_json(os.path.join(OUT, "dsrt-fixtures.json"), out)
    days = collections.Counter(r["made"][:10] for r in rows)
    L = ["# Test fixtures left in /tmp", "",
         f"Listed on {out['listed_at']}. {out['count']} folders named `/tmp/dsrt-*`, {human(out['bytes'])} of file data",
         f"({human(out['disk_bytes'])} on disk). They were not copied and not deleted.", "",
         out["note"], "",
         "Per-folder rows (name, files, bytes, time made, newest file) are in `dsrt-fixtures.json`.", "",
         "## By day made (UTC)", "", "| Day | Folders |", "|---|---|"]
    for d in sorted(days):
        L.append(f"| {d} | {days[d]} |")
    L += ["", "## By name prefix", "",
          "The prefix is the folder name without the six random characters `mkdtemp` adds. \"Made by\" is the line that",
          "creates such a folder and the test it sits in, read from the test files as they were before the fix",
          "(`git show 2035fcb^:<file>`) and from the runner's own code.", "",
          "| Prefix | Folders | Files | Size | First made | Last made | Made by (file:line, test) |", "|---|---|---|---|---|---|---|"]
    for g in sorted(by.values(), key=lambda g: -g["folders"]):
        mk = "; ".join(f"`{m['where']}`" + (f" in \"{md_escape(m['test'][:70])}\"" if m.get("test") else "") for m in g["made_by"][:4]) or "not found in the test files"
        if len(g["made_by"]) > 4:
            mk += f"; and {len(g['made_by']) - 4} more lines"
        L.append(f"| `{g['prefix']}` | {g['folders']} | {g['files']} | {human(g['bytes'])} | {fmt_ts(g['first'])} | {fmt_ts(g['last'])} | {mk} |")
    write_text(os.path.join(OUT, "dsrt-fixtures.md"), "\n".join(L) + "\n")
    log(f"dsrt: {len(rows)} folders, {out['bytes'] / 1e9:.1f} GB")


# ----------------------------------------------------------------------------------------
# Step: manifest (manifest.json and MANIFEST.md)
# ----------------------------------------------------------------------------------------
SCRATCH_WS = [
    (r"^(ws3-|ws3$|fable-ws3)", "WS3 score"),
    (r"^(ws1-mopup|mopup)", "WS1 mop-up round"),
    (r"^(B\d\d-|b0\d|batch-sessions|briefs|checks|compile|w\d|f\d\d|fp\d|gate|mycheck|build|c\d|cx|after|before)", "WS1 ranges by family"),
    (r"^(review|fable-review|fable-rereview|central|approval)", "Central reviews and approvals"),
    (r"^(cysc|cal|creat|bioage|biograma|biomarcare|kdm|KDM|NUMBERS|abs|cite|cits|dl_|web|deliverables|critic)", "Biomarker evidence and biological age (October)"),
]


def scratch_ws(arc):
    if arc.startswith("tasks/"):
        return "Background command outputs"
    rel = arc.split("/", 1)[1] if "/" in arc else arc
    for rx, ws in SCRATCH_WS:
        if re.search(rx, rel):
            return ws
    return "Other scratch work"


def rollup_hash(items):
    h = hashlib.sha256()
    for path, sha in sorted(items):
        h.update(f"{sha}  {path}\n".encode())
    return h.hexdigest()


def own_files():
    out = []
    for fn in sorted(os.listdir(OUT)):
        p = os.path.join(OUT, fn)
        if fn.startswith(".") or not os.path.isfile(p) or fn in ("manifest.json", "MANIFEST.md"):
            continue
        out.append({"path": fn, "size": os.path.getsize(p), "sha256": sha256_file(p)})
    for sub in ("transcripts", "scratch"):
        for fn in ("SHA256SUMS", "parts.json"):
            p = os.path.join(OUT, sub, fn)
            if os.path.isfile(p):
                out.append({"path": f"{sub}/{fn}", "size": os.path.getsize(p), "sha256": sha256_file(p)})
    return out


def _load(path, default):
    try:
        return json.load(open(path))
    except Exception:
        return default


def step_manifest():
    repo = json.load(open(os.path.join(WORK, "repo.json")))
    tparts = _load(os.path.join(OUT, "transcripts", "parts.json"), {"parts": [], "members": []})
    sparts = _load(os.path.join(OUT, "scratch", "parts.json"), {"parts": [], "members": [], "excluded": [], "repository_copies": []})
    # the time of the snapshot the transcript archive was made from (never a new snapshot)
    snap = {"taken_at": tparts.get("snapshot_taken_at") or "unknown"}
    dsrt = _load(os.path.join(OUT, "dsrt-fixtures.json"), None)
    agents = {a["f"]: a for a in read_jsonl(os.path.join(IDX, "agents.jsonl"))}
    own = own_files()
    in_prog = [x for x in sparts.get("excluded", []) if x["reason"].startswith("in progress") or x["reason"].startswith("written in the last")]
    in_prog_wt = [w for w in repo["worktrees"] if w.get("in_progress")]
    man = {
        "made_at": iso(), "made_by": "make-evidence.py", "transcript_snapshot_taken_at": snap["taken_at"],
        "repository": {"path": REPO, "branch": BRANCH, "commit": repo["commit"], "taken_at": repo["taken_at"],
                       "files": repo["files"], "not_committed": repo["pending"]},
        "archives": {
            "transcripts": {"folder": "transcripts", "parts": tparts["parts"],
                            "proves": "Every command run and every output, in the main conversation and in every agent, workflow and tool-result file, as of the snapshot (scrubbed)."},
            "scratch": {"folder": "scratch", "parts": sparts["parts"], "read_at": sparts.get("read_started_at") or "2026-11-11T21:38:41Z",
                        "proves": "The scratch folder's reports, reviews, test logs, DSRT results and compiles, and the background commands' outputs, as of the snapshot (scrubbed)."},
        },
        "transcript_files": tparts.get("members", []),
        "scratch_files": sparts.get("members", []),
        "scratch_not_archived": sparts.get("excluded", []),
        "scratch_repository_copies": sparts.get("repository_copies", []),
        "record_files": own,
        "worktrees": repo["worktrees"], "branches": repo["branches"],
        "cloud_sessions": repo["sessions"], "scheduled_tasks": repo["scheduled_tasks"],
        "in_progress": {"scratch": in_prog, "worktrees": [{"path": w["path"], "branch": w["branch"], "head": w["head"]} for w in in_prog_wt]},
        "tmp_fixtures": {"listed_in": "dsrt-fixtures.md", "count": dsrt["count"] if dsrt else None, "bytes": dsrt["bytes"] if dsrt else None},
    }
    write_json(os.path.join(OUT, "manifest.json"), man)
    # ---- MANIFEST.md
    L = ["# Manifest of the evidence record", "",
         f"AI work product. Made by `make-evidence.py` on {man['made_at']}. Transcript snapshot: {snap['taken_at']}.",
         f"Repository: `{BRANCH}` at commit `{repo['commit'][:12]}`, read through git on {repo['taken_at']}.",
         f"Scratch folder: read from {sparts.get('read_started_at') or '21:38 UTC on 11 November 2026'} to {sparts.get('made_at')}.",
         "Every item has its size and sha256. Sizes use binary units (1 MB = 1024 x 1024 bytes). Files in the repository are",
         "listed by path, grouped by workstream and by the day they last changed. A folder with many files is listed once, with",
         "its file count and a combined hash (the sha256 of its sorted `sha256  path` lines); `manifest.json` lists every file.", ""]
    L += ["## 1. This record's own files", "", "| File | Size | sha256 | What it is |", "|---|---|---|---|"]
    what = {"README.md": "How to read the record, check a claim and unpack the archives",
            "TESTS-SUMMARY.md": "Every test and check run, in time order, with outcomes and proof; statements to the CEO traced",
            "tests.json": "The same, as data, with every command in full",
            "DELETIONS.md": "What was deleted in the session, what it held, what survives",
            "redactions.md": "Every redaction by file and kind (no values)", "redactions.json": "The same, as data",
            "dsrt-fixtures.md": "The /tmp/dsrt-* test fixtures, by prefix, with the test that makes them",
            "dsrt-fixtures.json": "The same, one row per folder", "make-evidence.py": "The script that rebuilds this record",
            "transcripts/SHA256SUMS": "Checksums of the transcript parts (sha256sum -c)",
            "transcripts/parts.json": "Every transcript file: its part, size and sha256 before and after scrubbing",
            "scratch/SHA256SUMS": "Checksums of the scratch parts (sha256sum -c)",
            "scratch/parts.json": "Every scratch file: its part, size and sha256; what was left out and why"}
    for f in own:
        L.append(f"| `{f['path']}` | {human(f['size'])} | `{f['sha256']}` | {what.get(f['path'], '')} |")
    for key, title, num in (("transcripts", "transcripts", "2a"), ("scratch", "scratch folder", "2b")):
        a = man["archives"][key]
        L += ["", f"## {num}. Archive: {title}", "", a["proves"], "",
              "| Part | Size | sha256 | Files | First file | Last file |", "|---|---|---|---|---|---|"]
        for p in a["parts"]:
            L.append(f"| `{a['folder']}/{p['name']}` | {human(p['size'])} | `{p['sha256']}` | {p['members']} | `{md_escape(str(p['first']))}` | `{md_escape(str(p['last']))}` |")
        if not a["parts"]:
            L.append("| (not built in this run) | | | | | |")
    L += ["", "### What the transcript parts hold", "", "| Kind | Files | Size at snapshot | First entry (UTC) | Last entry (UTC) |", "|---|---|---|---|---|"]
    kinds = collections.OrderedDict()
    for m in man["transcript_files"]:
        n = m["name"]
        k = ("main conversation" if n == "main.jsonl" else
             "workflow agents" if n.startswith("subagents/workflows/") and n.endswith(".jsonl") else
             "background agents" if n.startswith("subagents/") and n.endswith(".jsonl") else
             "agent metadata" if n.startswith("subagents/") else
             "workflow run records and scripts" if n.startswith("workflows/") else
             "tool results (full outputs)" if n.startswith("tool-results/") else "other")
        g = kinds.setdefault(k, {"n": 0, "bytes": 0, "first": None, "last": None})
        g["n"] += 1
        g["bytes"] += m["snapshot_bytes"]
        a = agents.get(n)
        if a and a.get("first_ts"):
            g["first"] = min(g["first"] or a["first_ts"], a["first_ts"])
            g["last"] = max(g["last"] or a["last_ts"], a["last_ts"])
    for k, g in kinds.items():
        L.append(f"| {k} | {g['n']} | {human(g['bytes'])} | {fmt_ts(g['first'])} | {fmt_ts(g['last'])} |")
    # repository by workstream and date
    L += ["", "## 3. Committed proof in the repository, by workstream and date", ""]
    order = []
    for rx, ws, _ in PROOF_RULES:
        if ws not in order:
            order.append(ws)
    by_ws = collections.OrderedDict()
    for f in repo["files"]:
        by_ws.setdefault(f["workstream"], []).append(f)
    for ws in order + [w for w in by_ws if w not in order]:
        fs = by_ws.get(ws)
        if not fs:
            continue
        L += [f"### {ws}", "", f"{len(fs)} files, {human(sum(x['size'] for x in fs))}.", "",
              "| Last changed | Path | Files | Size | sha256 | What it proves |", "|---|---|---|---|---|---|"]
        dircount = collections.Counter()
        for f in fs:
            parts = f["path"].split("/")
            for depth in range(1, len(parts)):
                dircount["/".join(parts[:depth]) + "/"] += 1
        groups = collections.OrderedDict()
        for f in fs:
            parts = f["path"].split("/")
            key = f["path"]
            for depth in range(len(parts) - 1, 0, -1):
                d = "/".join(parts[:depth]) + "/"
                if dircount[d] > 25:
                    key = d
                    break
            groups.setdefault(key, []).append(f)
        rows = []
        for key, items in groups.items():
            dates = sorted(x["date"] or "" for x in items)
            if len(items) == 1 and not key.endswith("/"):
                x = items[0]
                rows.append((x["date"] or "", f"| {(x['date'] or '')[:10]} | `{x['path']}` | 1 | {human(x['size'])} | `{x['sha256']}` | {x['proves']} |"))
            else:
                span = dates[0][:10] if dates[0][:10] == dates[-1][:10] else f"{dates[0][:10]} to {dates[-1][:10]}"
                rows.append((dates[-1], f"| {span} | `{key}` | {len(items)} | {human(sum(x['size'] for x in items))} | `{rollup_hash([(x['path'], x['sha256']) for x in items])}` (combined) | {items[0]['proves']} |"))
        for _, r in sorted(rows, key=lambda r: r[0]):
            L.append(r[1])
        L.append("")
    if repo["pending"]:
        L += ["Not committed when the record was made (in the main checkout):", ""] + [f"- `{p['state']}` `{p['path']}`" for p in repo["pending"][:200]] + [""]
    # scratch by workstream
    L += ["## 4. Proof in the scratch folder (inside the scratch archive), by workstream", "",
          "| Workstream | Folder | Files | Size | Dates | Combined sha256 |", "|---|---|---|---|---|---|"]
    sg = collections.OrderedDict()
    for m in man["scratch_files"]:
        if "symlink_to" in m:
            continue
        arc = m["arcname"]
        if arc.startswith("tasks/"):
            top = "tasks/"
        elif arc.count("/") >= 2:
            top = "/".join(arc.split("/")[:2]) + "/"
        else:
            top = "scratchpad/ (files at the top)"
        g = sg.setdefault((scratch_ws(arc), top), {"n": 0, "bytes": 0, "dates": [], "items": []})
        g["n"] += 1
        g["bytes"] += m["bytes"]
        g["dates"].append(m["mtime"])
        g["items"].append((arc, m["sha256_archived"]))
    for (ws, top), g in sorted(sg.items(), key=lambda kv: (kv[0][0], min(kv[1]["dates"]))):
        d = sorted(g["dates"])
        span = d[0][:10] if d[0][:10] == d[-1][:10] else f"{d[0][:10]} to {d[-1][:10]}"
        L.append(f"| {ws} | `{top}` | {g['n']} | {human(g['bytes'])} | {span} | `{rollup_hash(g['items'])}` |")
    links = sum(1 for m in man["scratch_files"] if "symlink_to" in m)
    if links:
        L += ["", f"{links} symbolic links are stored as links (mostly `node_modules` links to the repository's packages, and the tasks folder's links to agent transcripts, which are in the transcript archive)."]
    if man["scratch_repository_copies"]:
        L += ["", "Copies of the repository in the scratch folder, stored as differences from their commit:", "",
              "| Folder | Commit | Made (UTC) | Identical files, not stored | Changed files, stored | Added files, stored |", "|---|---|---|---|---|---|"]
        for c in man["scratch_repository_copies"]:
            L.append(f"| `{c['path']}` | `{c['commit'][:12]}` | {fmt_ts(c['made_at'])} | {c['files_identical_not_stored']} | {len(c['files_changed_stored'])} | {c['files_added_stored']} |")
    if man["scratch_not_archived"]:
        L += ["", "Left out of the scratch archive:", ""]
        for x in man["scratch_not_archived"]:
            L.append(f"- `{x['path']}`: {x['reason']}")
    # sessions
    L += ["", "## 5. Cloud sessions this session started", "",
          f"This session is `{CLOUD_SESSION}` on claude.ai. It started the sessions below; their own transcripts are on",
          "claude.ai, not here. What each did is read from the main transcript, the programme branch's commits and the batch",
          "scorecards.", "",
          "| Session | Title | Created (UTC) | Last status seen | What it did | Proof |", "|---|---|---|---|---|---|"]
    for s in repo["sessions"]:
        last = s["statuses"][-1] if s["statuses"] else None
        st = (f"{last['status']}" + (f" / {last['bucket']}" if last.get("bucket") else "") + f" at {fmt_ts(last['at'])}") if last else "never checked"
        did = f"Batch {s.get('batch')} of WS1 (ranges by family), results to `{s.get('outcome_branch')}`"
        if s.get("scorecard"):
            did += f"; scorecard `{s['scorecard']}`"
        if s.get("commits"):
            did += f"; {len(s['commits'])} commits on the branch name it, the latest: {md_escape(s['commits'][0][:120])}"
        L.append(f"| `{s['id']}` | {md_escape(s['title'])} | {fmt_ts(s['created'])} | {st} | {did} | {s['proof']} |")
    if repo["scheduled_tasks"]:
        L += ["", "Scheduled tasks this session used:", ""]
        for t in repo["scheduled_tasks"]:
            L.append(f"- `{t['id']}` ({', '.join(t['names']) or 'no name recorded'}): {t['calls']} calls from {fmt_ts(t['first'])} to {fmt_ts(t['last'])} ({', '.join(f'{k} {v}' for k, v in t['tools'].items())}); schedules set: {', '.join(t['crons']) or 'none recorded'}.")
    # worktrees and branches
    L += ["", "## 6. Worktrees and branches: work not merged into the programme branch", "",
          f"Compared with `{BRANCH}` at `{repo['commit'][:12]}`. A worktree in progress was not read (no status, no files).", "",
          "| Worktree | Branch | HEAD | In progress | Commits not merged | Uncommitted changes |", "|---|---|---|---|---|---|"]
    for w in repo["worktrees"]:
        um = w.get("unmerged_commits") or []
        uc = w.get("uncommitted") or []
        L.append(f"| `{w['path']}` | `{w['branch']}` | `{(w['head'] or '')[:12]}` | {'yes' if w['in_progress'] else 'no'} | {len(um)}{': ' + md_escape('; '.join(um[:3])[:300]) if um else ''} | {md_escape('; '.join(uc[:6])[:300]) if uc else 'none'} |")
    L += ["", "| Branch | HEAD | Last commit (UTC) | Created (reflog) | Commits not merged |", "|---|---|---|---|---|"]
    for b in repo["branches"]:
        um = b["unmerged_commits"]
        L.append(f"| `{b['branch']}` | `{b['head']}` | {fmt_ts(b['head_date'])} | {fmt_ts(b['created'])} | {len(um)}{': ' + md_escape('; '.join(um[:3])[:300]) if um else ''} |")
    L += ["", "## 7. In progress at the snapshot (not read, not archived)", ""]
    if not in_prog and not in_prog_wt:
        L.append("Nothing.")
    for x in in_prog:
        L.append(f"- `{x['path']}`: {x['reason']}")
    for w in in_prog_wt:
        L.append(f"- worktree `{w['path']}` (branch `{w['branch']}`, HEAD `{(w['head'] or '')[:12]}`)")
    L += ["", "## 8. Test fixtures in /tmp", "",
          f"{dsrt['count'] if dsrt else '?'} folders `/tmp/dsrt-*`, {human(dsrt['bytes']) if dsrt else '?'}: listed in `dsrt-fixtures.md`, not copied."]
    write_text(os.path.join(OUT, "MANIFEST.md"), "\n".join(L) + "\n")
    log(f"manifest: {len(repo['files'])} repository files, {len(tparts['parts'])} + {len(sparts['parts'])} archive parts")


# ----------------------------------------------------------------------------------------
# Step: readme
# ----------------------------------------------------------------------------------------
def step_readme():
    man = _load(os.path.join(OUT, "manifest.json"), {})
    tj = _load(os.path.join(OUT, "tests.json"), {"runs": [], "statements": [], "agents": []})
    red = _load(os.path.join(OUT, "redactions.json"), {"totals": {}})
    tp = man.get("archives", {}).get("transcripts", {}).get("parts", [])
    sp = man.get("archives", {}).get("scratch", {}).get("parts", [])
    stc = collections.Counter(s["status"] for s in tj["statements"])
    nt = [s for s in tj["statements"] if s["status"] == "not traced"]
    L = ["# EVA physician sign-off programme: the evidence record", "",
         "AI work product, prepared for the CEO's review. A licensed physician reviews and signs; nothing here is a sign-off.", "",
         "## What it is", "",
         "The proof of the tests and processes run in the Claude Code session that runs the programme",
         f"(`{CLOUD_SESSION}`), gathered before anything is deleted.",
         f"Transcripts as of {man.get('transcript_snapshot_taken_at')}; scratch folder read from {(man.get('archives', {}).get('scratch', {}) or {}).get('read_at') or 'the time in scratch/parts.json'};",
         f"repository at commit `{(man.get('repository', {}).get('commit') or '')[:12]}` ({man.get('repository', {}).get('taken_at')}). Work done after those times is not in this copy.",
         "It holds:", "",
         f"- `transcripts/`: every transcript of the session, scrubbed and compressed ({len(tp)} parts, {human(sum(p['size'] for p in tp))}). They hold every command run and its output.",
         f"- `scratch/`: the scratch folder's reports, reviews, test logs, DSRT results and compiles, and the background commands' outputs ({len(sp)} parts, {human(sum(p['size'] for p in sp))}).",
         f"- `TESTS-SUMMARY.md` and `tests.json`: {len(tj['runs'])} test and check runs in time order, {len(tj['agents'])} agents' reports and verdicts, and {len(tj['statements'])} statements of a result made to the CEO, each traced to its proof.",
         "- `DELETIONS.md`: what was deleted in the session, what it held and what survives.",
         "- `MANIFEST.md` and `manifest.json`: every piece of proof with its size and sha256, by workstream and date: the committed",
         "  records in the repository, the archive parts, the cloud sessions this session started, and the unmerged worktrees",
         "  and branches.",
         "- `dsrt-fixtures.md` and `dsrt-fixtures.json`: the test fixtures left in `/tmp` (listed, not copied).",
         "- `redactions.md`: every redaction made while packing, by file and kind.",
         "- `make-evidence.py`: the script that rebuilds all of this from the sources.", "",
         "## How to check a claim", "",
         "1. Find the claim in `TESTS-SUMMARY.md`. Section 1 lists each result stated to the CEO with its proof. Section 5 lists",
         "   every run by time, with the exact command, the folder, the commit and the outcome.",
         "2. Open the proof. It names a transcript file, a line and a tool-call id, for example",
         "   `main.jsonl line 12325, call toolu_01...`. Unpack the transcripts (below) and print that line:",
         "   `sed -n '12325p' 4e1a7523-c199-547a-904f-d87e53286958.jsonl | python3 -m json.tool`.",
         "   The call id appears twice: on the command, and a few lines later on its result.",
         "   `main.jsonl` is the file `4e1a7523-c199-547a-904f-d87e53286958.jsonl`; every other name is relative to the folder",
         "   `4e1a7523-c199-547a-904f-d87e53286958/`. A proof that names a background output (`tasks/<id>.output`) is in the",
         "   scratch archive under `tasks/`.",
         "3. Re-run the command at the commit: `git worktree add /tmp/check <commit>`, then `cd /tmp/check && npm ci`, then the exact",
         "   command from the entry. A command that wrote into a scratch folder needs that folder first; the scratch archive",
         "   holds what those folders held.", "",
         "## How to unpack the archives", "",
         "Each part is a complete `.tar.xz` file. It can be checked and unpacked on its own; together the parts hold everything.", "",
         "```sh",
         "(cd transcripts && sha256sum -c SHA256SUMS)",
         "mkdir -p unpacked/transcripts && for p in transcripts/*.tar.xz; do tar -xJf \"$p\" -C unpacked/transcripts; done",
         "(cd scratch && sha256sum -c SHA256SUMS)",
         "mkdir -p unpacked/scratch && for p in scratch/*.tar.xz; do tar -xJf \"$p\" -C unpacked/scratch; done",
         "```", "",
         "The transcripts unpack to `4e1a7523-c199-547a-904f-d87e53286958.jsonl` (the main conversation) and the folder",
         "`4e1a7523-c199-547a-904f-d87e53286958/` with `subagents/`, `subagents/workflows/`, `workflows/` and `tool-results/`.",
         "The scratch archive unpacks to `scratchpad/` and `tasks/`. A copy of the repository that an agent made with",
         "`git archive` is stored only where it differs from its commit: rebuild it with `git archive <commit> | tar -x -C <folder>`",
         "and unpack the stored files over it. MANIFEST.md, section 4, lists each copy and its commit.", "",
         "## What was changed while packing", "",
         f"The CEO's email address was replaced with `{CEO_TOKEN}`, and anything that looks like a secret with `{SECRET_TOKEN}`: "
         + (", ".join(f"{v} {k}" for k, v in sorted(red.get("totals", {}).items(), key=lambda kv: -kv[1])) or "none") + ".",
         "`redactions.md` lists each by file and kind. Nothing else was changed. Each file's sha256 before and after scrubbing",
         "is in `transcripts/parts.json` and `scratch/parts.json`.", "",
         "## What is not in the record", "",
         "- The session before 7 October 2026, 06:12 UTC. The session was created on 22 September 2026; the local transcript",
         "  starts at a compaction on 7 October, so the earlier weeks are only in that compaction's summary. They may be on",
         "  claude.ai.",
         "- The five batch sessions B06 to B10 ran as their own cloud sessions. Their transcripts are on claude.ai; their",
         "  committed results (scorecards, research, verify, judges, decisions) are in the repository and in MANIFEST.md.",
         "- Work still running at the snapshot (MANIFEST.md, section 7) was not read.",
         "- The `/tmp/dsrt-*` fixtures were listed, not copied. The scratch folder's tools and downloads (`venv/`, `src/`, `dl/`)",
         "  and installed packages (`node_modules/`) were left out.", "",
         "## How to refresh it", "",
         "Run `python3 -I make-evidence.py` again (about 30 minutes, most of it compression). It reads the sources and writes only",
         "into this folder; it runs no test suite and no acceptance-test runner. To rebuild one part, pass `--steps`, for",
         "example `--steps snapshot,index,tests`. It stops if the disk falls below 5 GB free. Before the final refresh, empty",
         "`IN_PROGRESS` and `IN_PROGRESS_WORKTREES` at the top of the script, so that finished work is read.", "",
         "## Totals at this run", "",
         f"- Test and check runs: {len(tj['runs'])}. Agents' reports: {len(tj['agents'])}.",
         f"- Statements of a result to the CEO: {len(tj['statements'])} (" + ", ".join(f"{v} {k}" for k, v in stc.most_common()) + f"). Not traced: {len(nt)}, listed in TESTS-SUMMARY.md section 2.",
         f"- Repository files listed: {len(man.get('repository', {}).get('files', []))}, at commit `{(man.get('repository', {}).get('commit') or '')[:12]}`.",
         f"- Made on {iso()}."]
    write_text(os.path.join(OUT, "README.md"), "\n".join(L) + "\n")
    log("readme written")
    if os.path.exists(os.path.join(WORK, "repo.json")):
        step_manifest()  # again, so the manifest holds README.md's final hash


# ----------------------------------------------------------------------------------------
# Step: verify (read every part back and scan it again)
# ----------------------------------------------------------------------------------------
def step_verify():
    """Check each part's size and sha256, read every member back, and scan the unpacked text again for the
    CEO's email and the secret patterns. Writes .work/verify.json and adds the result to redactions.md."""
    res = {"checked_at": iso(), "archives": {}}
    for sub in ("transcripts", "scratch"):
        folder = os.path.join(OUT, sub)
        pj = os.path.join(folder, "parts.json")
        if not os.path.exists(pj):
            continue
        parts = json.load(open(pj))["parts"]
        out = []
        for p in parts:
            path = os.path.join(folder, p["name"])
            size = os.path.getsize(path)
            sha = sha256_file(path)
            hits = collections.Counter()
            n = 0
            with tarfile.open(path, mode="r:xz") as t:
                for m in t:
                    n += 1
                    if not m.isfile():
                        continue
                    data = t.extractfile(m).read()
                    for kind, rx, grp, check in SECRET_RULES:
                        for mm in rx.finditer(data):
                            if grp and check and not looks_secret(mm.group(grp)):
                                continue
                            if grp and SECRET_TOKEN.encode() in mm.group(0):
                                continue
                            hits[kind] += 1
            out.append({"part": p["name"], "size": size, "under_limit": size <= PART_LIMIT, "sha256_ok": sha == p["sha256"],
                        "members_read": n, "members_written": p["members"], "remaining_matches": dict(hits)})
            log(f"  verified {sub}/{p['name']}: {size / 1e6:.1f} MB, sha256 {'ok' if sha == p['sha256'] else 'MISMATCH'}, {n} members, remaining {dict(hits) or 0}")
        res["archives"][sub] = out
    write_json(os.path.join(WORK, "verify.json"), res)
    write_redactions()


# ----------------------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------------------
STEPS = ["snapshot", "index", "transcripts", "scratch", "repo", "dsrt", "tests", "deletions", "verify", "manifest", "readme"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", default=",".join(STEPS))
    ap.add_argument("--keep-work", action="store_true", help="keep the .work folder (the parsed index)")
    a = ap.parse_args()
    steps = [s.strip() for s in a.steps.split(",") if s.strip()]
    ensure_dir(OUT)
    check_disk("start")
    for s in steps:
        if s not in STEPS:
            raise SystemExit("unknown step " + s)
        log("step", s)
        globals()["step_" + s]()
        check_disk("after " + s)
    if steps == STEPS and not a.keep_work:
        # .work holds the unscrubbed index of the transcripts: it must never be uploaded
        shutil.rmtree(WORK, ignore_errors=True)
        log("removed the working index (.work); pass --keep-work to keep it")


if __name__ == "__main__":
    main()
