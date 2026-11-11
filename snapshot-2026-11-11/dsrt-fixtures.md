# Test fixtures left in /tmp

Listed on 2026-11-11T21:48:35Z. 13740 folders named `/tmp/dsrt-*`, 11.5 GB of file data
(11.7 GB on disk). They were not copied and not deleted.

Fixtures that src/lib/signoff/dsrt-core.test.ts and dsrt-checks.test.ts left in the system's temporary folder before commit 2035fcb (10 November 13:33 UTC), which points TMPDIR at one root per test file and removes it after the run. Listed only; never copied or deleted.

Per-folder rows (name, files, bytes, time made, newest file) are in `dsrt-fixtures.json`.

## By day made (UTC)

| Day | Folders |
|---|---|
| 2026-11-06 | 52 |
| 2026-11-07 | 616 |
| 2026-11-08 | 1802 |
| 2026-11-09 | 2129 |
| 2026-11-10 | 9141 |

## By name prefix

The prefix is the folder name without the six random characters `mkdtemp` adds. "Made by" is the line that
creates such a folder and the test it sits in, read from the test files as they were before the fix
(`git show 2035fcb^:<file>`) and from the runner's own code.

| Prefix | Folders | Files | Size | First made | Last made | Made by (file:line, test) |
|---|---|---|---|---|---|---|
| `dsrt-g1-copy` | 3720 | 33040 | 7.5 GB | 2026-11-08 16:48 | 2026-11-10 15:00 | `src/lib/signoff/dsrt-core.test.ts:1774` in "checks fixer diffs against the ownership map" |
| `dsrt-work` | 2634 | 1436 | 912.5 KB | 2026-11-06 04:31 | 2026-11-10 15:00 | `src/lib/signoff/dsrt-core.test.ts:260` in "D6 is blocked until the reconciliation directory exists"; `src/lib/signoff/dsrt-core.test.ts:267` in "D6 is blocked until the reconciliation directory exists"; `src/lib/signoff/dsrt-core.test.ts:590` in "fails through the check a forward migration that writes another critic"; `src/lib/signoff/dsrt-core.test.ts:682` in "fails through the check a forward migration that writes a quoted criti"; and 9 more lines |
| `dsrt-seed` | 2460 | 8417 | 11.5 MB | 2026-11-06 04:31 | 2026-11-10 15:00 | `src/lib/signoff/dsrt-core.test.ts:194`; `src/lib/signoff/dsrt-core.test.ts:426` in "data (D5 one source of truth)" |
| `dsrt-g1-work` | 847 | 2789 | 23.9 MB | 2026-11-08 16:48 | 2026-11-10 15:00 | `src/lib/signoff/dsrt-core.test.ts:1774` in "checks fixer diffs against the ownership map" |
| `dsrt-g1-seed` | 605 | 5905 | 1.4 GB | 2026-11-08 16:48 | 2026-11-10 15:00 | `src/lib/signoff/dsrt-core.test.ts:1774` in "checks fixer diffs against the ownership map" |
| `dsrt-g1` | 457 | 2189 | 2.6 MB | 2026-11-07 15:17 | 2026-11-10 15:00 | `src/lib/signoff/dsrt-core.test.ts:1774` in "checks fixer diffs against the ownership map" |
| `dsrt-root` | 431 | 260 | 30.2 KB | 2026-11-06 04:31 | 2026-11-10 14:59 | `src/lib/signoff/dsrt-core.test.ts:214` in "reports the checks of missing modules as blocked and is deterministic"; `src/lib/signoff/dsrt-core.test.ts:1288` in "reads the compile" |
| `dsrt-e1-relink` | 392 | 3920 | 548.7 MB | 2026-11-08 16:48 | 2026-11-10 14:59 | `src/lib/signoff/dsrt-checks.test.ts:524` in "holds every split of each file to a record linked to it under the spli" |
| `dsrt-retire` | 238 | 952 | 72.6 MB | 2026-11-07 15:17 | 2026-11-10 14:59 | `src/lib/signoff/dsrt-core.test.ts:736` in "retires a production-only marker only with every row removed and an ex" |
| `dsrt-b5` | 182 | 182 | 22.8 KB | 2026-11-08 04:01 | 2026-11-10 14:59 | `src/lib/signoff/dsrt-checks.test.ts:166` in "B5" |
| `dsrt-work-0bebb15` | 144 | 1130 | 138.5 MB | 2026-11-08 16:48 | 2026-11-10 14:59 | `src/lib/signoff/dsrt-core.test.ts:260` in "D6 is blocked until the reconciliation directory exists"; `src/lib/signoff/dsrt-core.test.ts:267` in "D6 is blocked until the reconciliation directory exists"; `src/lib/signoff/dsrt-core.test.ts:590` in "fails through the check a forward migration that writes another critic"; `src/lib/signoff/dsrt-core.test.ts:682` in "fails through the check a forward migration that writes a quoted criti"; and 9 more lines |
| `dsrt-work-15f04bb` | 144 | 1130 | 157.9 MB | 2026-11-08 16:48 | 2026-11-10 14:59 | `src/lib/signoff/dsrt-core.test.ts:260` in "D6 is blocked until the reconciliation directory exists"; `src/lib/signoff/dsrt-core.test.ts:267` in "D6 is blocked until the reconciliation directory exists"; `src/lib/signoff/dsrt-core.test.ts:590` in "fails through the check a forward migration that writes another critic"; `src/lib/signoff/dsrt-core.test.ts:682` in "fails through the check a forward migration that writes a quoted criti"; and 9 more lines |
| `dsrt-e1` | 130 | 390 | 406.5 KB | 2026-11-08 16:48 | 2026-11-10 14:59 | `src/lib/signoff/dsrt-checks.test.ts:325` in "E1 asks the number of the records its specification names" |
| `dsrt-e1-15f04bb` | 130 | 980 | 136.9 MB | 2026-11-08 16:48 | 2026-11-10 14:59 | `src/lib/signoff/dsrt-checks.test.ts:483` in "holds every split of each file to a record linked to it under the spli" |
| `dsrt-e1-cf7c4c8` | 130 | 980 | 137.4 MB | 2026-11-08 16:48 | 2026-11-10 14:59 | `src/lib/signoff/dsrt-checks.test.ts:483` in "holds every split of each file to a record linked to it under the spli" |
| `dsrt-e1-splits` | 130 | 260 | 135.2 KB | 2026-11-08 16:48 | 2026-11-10 14:59 | `src/lib/signoff/dsrt-checks.test.ts:429` in "holds every split of each file to a record linked to it under the spli" |
| `dsrt-g1-seed-set` | 122 | 976 | 291.1 MB | 2026-11-08 16:48 | 2026-11-10 15:00 | `src/lib/signoff/dsrt-core.test.ts:1774` in "checks fixer diffs against the ownership map" |
| `dsrt-g1-lenses` | 120 | 702 | 2.5 MB | 2026-11-08 16:48 | 2026-11-10 15:00 | `src/lib/signoff/dsrt-core.test.ts:1774` in "checks fixer diffs against the ownership map" |
| `dsrt-g1-seed-later` | 120 | 960 | 286.4 MB | 2026-11-08 16:48 | 2026-11-10 15:00 | `src/lib/signoff/dsrt-core.test.ts:1774` in "checks fixer diffs against the ownership map" |
| `dsrt-g2-noprod` | 120 | 5280 | 64.2 MB | 2026-11-08 16:48 | 2026-11-10 15:00 | `src/lib/signoff/dsrt-core.test.ts:2021` in "G1: the compile is idempotent and the judge prompts are frozen; G2: ad" |
| `dsrt-e1-sex-states` | 107 | 214 | 149.9 KB | 2026-11-09 23:43 | 2026-11-10 14:59 | `src/lib/signoff/dsrt-checks.test.ts:464` in "holds every split of each file to a record linked to it under the spli" |
| `dsrt-p3-wiring` | 104 | 826 | 101.8 KB | 2026-11-09 23:47 | 2026-11-10 14:59 | `src/lib/signoff/dsrt-checks.test.ts:246` in "P3 names every app path that classifies a stored or reported result wi" |
| `dsrt-g1-b01-set` | 89 | 712 | 270.5 MB | 2026-11-08 16:48 | 2026-11-10 15:00 | `src/lib/signoff/dsrt-core.test.ts:1774` in "checks fixer diffs against the ownership map" |
| `dsrt-g1-b01-r4-today` | 71 | 568 | 215.5 MB | 2026-11-09 23:41 | 2026-11-10 15:00 | `src/lib/signoff/dsrt-core.test.ts:1774` in "checks fixer diffs against the ownership map" |
| `dsrt-g1-r4-today` | 70 | 560 | 212.5 MB | 2026-11-09 23:40 | 2026-11-10 15:00 | `src/lib/signoff/dsrt-core.test.ts:1774` in "checks fixer diffs against the ownership map" |
| `dsrt-checks` | 25 | 163 | 7.2 KB | 2026-11-07 12:17 | 2026-11-07 16:40 | `src/lib/signoff/dsrt-core.test.ts:2021` in "G1: the compile is idempotent and the judge prompts are frozen; G2: ad" |
| `dsrt-g1-r3-today` | 18 | 144 | 53.2 MB | 2026-11-08 16:48 | 2026-11-09 23:22 | `src/lib/signoff/dsrt-core.test.ts:1774` in "checks fixer diffs against the ownership map" |
