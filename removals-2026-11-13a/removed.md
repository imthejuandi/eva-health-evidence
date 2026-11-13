# Removals of 13 November 2026, first set

Recorded before removal. Reason: disk on the work machine reached the 4.5 GB floor while agents ran.

Fourteen raw test outputs from finished reviews were each compressed with xz:
- 727 MB raw, 12 MB compressed.
- Each archive was checked by decompressing it and comparing its sha256 with the original's.
- The compressed copies are in `files/`, at their scratch paths.
- The compressed copies also stay on the work machine beside where the raw files were; only the raw files were removed.
- `files.txt` gives each original's sha256, size and path.

What they are:
- **WS3-13:** the persona captures before and after the critical-tier package, with the flag unset, false and 0 (six files).
- **WS3-38's review:** the unit fuzz before and after.
- **WS3-43/41's pre-review and confirmation:** the stored-rows sweep (stored-600.jsonl).
- **The integration rehearsal:** the WS3-42 trial capture at d55ef1a.
- **The closure pre-check and the WS3-12 frozen-file review:** the function dumps at 07bf274, 6112b5e and 6c611b7.

None holds an email address or any person's data. The cases are built by test code; no database was read.

To restore, run `xz -dk <file>.xz`.
