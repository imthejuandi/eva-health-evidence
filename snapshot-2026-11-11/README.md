# EVA physician sign-off programme: the evidence record

AI work product, prepared for the CEO's review. A licensed physician reviews and signs; nothing here is a sign-off.

## What it is

The proof of the tests and processes run in the Claude Code session that runs the programme
(`session_016mEXZE6RheLMXSZTgYDUrW`), gathered before anything is deleted.
Transcripts as of 2026-11-11T21:01:49Z; scratch folder read from 2026-11-11T21:38:41Z;
repository at commit `e5b42ff13608` (2026-11-11T22:11:30Z). Work done after those times is not in this copy.
It holds:

- `transcripts/`: every transcript of the session, scrubbed and compressed (6 parts, 213.4 MB). They hold every command run and its output.
- `scratch/`: the scratch folder's reports, reviews, test logs, DSRT results and compiles, and the background commands' outputs (2 parts, 76.6 MB).
- `TESTS-SUMMARY.md` and `tests.json`: 4844 test and check runs in time order, 761 agents' reports and verdicts, and 295 statements of a result made to the CEO, each traced to its proof.
- `DELETIONS.md`: what was deleted in the session, what it held and what survives.
- `MANIFEST.md` and `manifest.json`: every piece of proof with its size and sha256, by workstream and date: the committed
  records in the repository, the archive parts, the cloud sessions this session started, and the unmerged worktrees
  and branches.
- `dsrt-fixtures.md` and `dsrt-fixtures.json`: the test fixtures left in `/tmp` (listed, not copied).
- `redactions.md`: every redaction made while packing, by file and kind.
- `make-evidence.py`: the script that rebuilds all of this from the sources.

## How to check a claim

1. Find the claim in `TESTS-SUMMARY.md`. Section 1 lists each result stated to the CEO with its proof. Section 5 lists
   every run by time, with the exact command, the folder, the commit and the outcome.
2. Open the proof. It names a transcript file, a line and a tool-call id, for example
   `main.jsonl line 12325, call toolu_01...`. Unpack the transcripts (below) and print that line:
   `sed -n '12325p' 4e1a7523-c199-547a-904f-d87e53286958.jsonl | python3 -m json.tool`.
   The call id appears twice: on the command, and a few lines later on its result.
   `main.jsonl` is the file `4e1a7523-c199-547a-904f-d87e53286958.jsonl`; every other name is relative to the folder
   `4e1a7523-c199-547a-904f-d87e53286958/`. A proof that names a background output (`tasks/<id>.output`) is in the
   scratch archive under `tasks/`.
3. Re-run the command at the commit: `git worktree add /tmp/check <commit>`, then `cd /tmp/check && npm ci`, then the exact
   command from the entry. A command that wrote into a scratch folder needs that folder first; the scratch archive
   holds what those folders held.

## How to unpack the archives

Each part is a complete `.tar.xz` file. It can be checked and unpacked on its own; together the parts hold everything.

```sh
(cd transcripts && sha256sum -c SHA256SUMS)
mkdir -p unpacked/transcripts && for p in transcripts/*.tar.xz; do tar -xJf "$p" -C unpacked/transcripts; done
(cd scratch && sha256sum -c SHA256SUMS)
mkdir -p unpacked/scratch && for p in scratch/*.tar.xz; do tar -xJf "$p" -C unpacked/scratch; done
```

The transcripts unpack to `4e1a7523-c199-547a-904f-d87e53286958.jsonl` (the main conversation) and the folder
`4e1a7523-c199-547a-904f-d87e53286958/` with `subagents/`, `subagents/workflows/`, `workflows/` and `tool-results/`.
The scratch archive unpacks to `scratchpad/` and `tasks/`. A copy of the repository that an agent made with
`git archive` is stored only where it differs from its commit: rebuild it with `git archive <commit> | tar -x -C <folder>`
and unpack the stored files over it. MANIFEST.md, section 4, lists each copy and its commit.

## What was changed while packing

The CEO's email address was replaced with `[CEO email]`, and anything that looks like a secret with `[redacted secret]`: 553 CEO email, 5 JWT, 2 Google API key.
`redactions.md` lists each by file and kind. Nothing else was changed. Each file's sha256 before and after scrubbing
is in `transcripts/parts.json` and `scratch/parts.json`.

## What is not in the record

- The session before 7 October 2026, 06:12 UTC. The session was created on 22 September 2026; the local transcript
  starts at a compaction on 7 October, so the earlier weeks are only in that compaction's summary. They may be on
  claude.ai.
- The five batch sessions B06 to B10 ran as their own cloud sessions. Their transcripts are on claude.ai; their
  committed results (scorecards, research, verify, judges, decisions) are in the repository and in MANIFEST.md.
- Work still running at the snapshot (MANIFEST.md, section 7) was not read.
- The `/tmp/dsrt-*` fixtures were listed, not copied. The scratch folder's tools and downloads (`venv/`, `src/`, `dl/`)
  and installed packages (`node_modules/`) were left out.

## How to refresh it

Run `python3 -I make-evidence.py` again (about 30 minutes, most of it compression). It reads the sources and writes only
into this folder; it runs no test suite and no acceptance-test runner. To rebuild one part, pass `--steps`, for
example `--steps snapshot,index,tests`. It stops if the disk falls below 5 GB free. Before the final refresh, empty
`IN_PROGRESS` and `IN_PROGRESS_WORKTREES` at the top of the script, so that finished work is read.

## Totals at this run

- Test and check runs: 4844. Agents' reports: 761.
- Statements of a result to the CEO: 295 (133 no numbers; nearest earlier run, 113 traced, 40 traced by name, 3 not traced, 3 traced across 2 items, 2 traced across 4 items, 1 partly traced). Not traced: 3, listed in TESTS-SUMMARY.md section 2.
- Repository files listed: 5311, at commit `e5b42ff13608`.
- Made on 2026-11-11T22:11:37Z.
