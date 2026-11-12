# EVA sign-off programme: evidence record

This private repository holds the raw proof behind the summaries in the eva-health repository, under
`docs/signoff/evidence/`. It exists so that every test result, review and decision stated during the programme
can be checked against what was actually run.

It will hold:

- the session transcripts, compressed in parts of at most 45 MB, each with a SHA-256 checksum: every command
  that was run and its full output, and every agent's brief and report;
- a manifest that lists every file of proof, its checksum and what it proves;
- the list of redactions: the CEO's email address and anything that looked like a secret were replaced before
  upload, and each replacement is listed by file and kind, never by value.

How to check a claim: find it in `docs/signoff/evidence/TESTS-SUMMARY.md` in eva-health, open the proof it points
to here, and re-run the command at the commit it names.

This is AI work product. The orchestrator acted as EVA's CMO; a licensed physician reviews and countersigns.
Nothing here is a clinical sign-off.

## Snapshots

- `snapshot-2026-11-11/`: transcripts up to 11 November 2026 21:01 UTC, the scratch folder read 21:38 to 21:47 UTC, and the eva-health repository at commit e5b42ff. Start with its `README.md` and `TESTS-SUMMARY.md`; `DELETIONS.md` says what was deleted earlier in the session and what survives; `transcripts/` and `scratch/` hold the archive parts with their checksums (`sha256sum -c SHA256SUMS`). A later snapshot will cover the rest of the programme.
- `snapshot-2026-11-12-mopup-impl/`: made at 22:44 UTC on 11 November 2026, before the scratch copies of the mop-up builder test and mocked dry run were removed: every output of that work, and for each removed copy its base commit, status, binary diff and untracked files. Its `SHA256SUMS` lists every file.

- `removals-2026-11-12/`: the records of scratch copies removed on 12 November 2026 to keep the disk above 5 GB, each uploaded before its removal (a Python environment's package list, two clean or bundled repository clones, a compressed tree copy, and the files a reviewer wrote inside its tree copies); `docs/signoff/evidence/DELETIONS.md` in eva-health lists them.
- `removals-2026-11-12b/`: the second removals of 12 November 2026: a bundle of every local branch not on the remote, and the record of the frozen-file reviewer's four tree copies, removed after this upload.
- `removals-2026-11-12c/`: the third removals of 12 November 2026: lossless archives of two folders of raw test output (the WS3-53 sweep and the integration rehearsal's persona captures), with each file's sha256, before the raw files were removed.

Dates. From about 21:00 UTC on 11 November 2026 the orchestrator's working notes ran ahead of the clock, so the second snapshot's folder name, its README title and its commit message (7f74572) say 12 November although it was made on 11 November; the commit times are right. The names are kept so that references hold. The records in eva-health were corrected the same day; `docs/signoff/evidence/README.md` there lists what was corrected and what was kept.
- `branches/`: a bundle of every unpushed local branch, refreshed while work is in flight, so the package branches survive the loss of the work machine.
