# Removals of 12 November 2026, third set

Recorded at 2026-11-12 21:27 UTC. Reason: disk on the work machine fell to 3.7 GB while agents ran.

Two folders of raw test output were packed losslessly with xz. Each archive was checked before anything was removed:
- its file count and its total bytes match the folder's;
- a full test extract succeeded.

Then only the large raw files were removed. The small files that people read (scripts, comparisons, logs) stay in place on the work machine. Each of those matches its archived copy by sha256.

## WS3-53-sweep.tar.xz: scratchpad/ws3-wave2/WS3-53/sweep

This is the classification and score sweep of package WS3-53 (D-39, results from other laboratories), at commits 387a859 (base) and 6fc376f (package).
- 13 files, 732,104,977 bytes.
- Removed: the five raw .jsonl outputs, sweep-base, sweep-current, sweep3000-base, sweep3000-current and trial-current (731 MB).
- Kept in place: zz-sweep.test.ts, compare.py, compare-3000.txt, personas-table.txt and the four logs.
- Each file's sha256, size and path is in WS3-53-sweep.files.txt.

## integration-capture.tar.xz: scratchpad/ws3-wave2/integration/capture

This holds the persona captures of the integration rehearsal on branch ws3-int: one before d97516e, and after 387a859, 4b07833, 9ae210c, da9643b and dd2a486.
- 26 files, 399,855,917 bytes.
- Removed: the seven capture-*.json files, about 56 MB each.
- Kept in place: cases.json, build-cases.ts, compare.py, cascade-audit.py, every compare-*.md and *.details.json file, and the audits.
- Each file's sha256, size and path is in integration-capture.files.txt.

Neither archive holds an email address or any person's data. The cases are built by test code; no database was read.

To restore, run `tar -xJf <archive> -C <folder>`.
