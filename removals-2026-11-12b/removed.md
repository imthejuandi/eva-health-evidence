# Removals of 12 November 2026, second set

Recorded at 2026-11-12 18:06 UTC, before removal. Reason: disk on the work machine fell to 4.3 GB while agents ran.

## The frozen-file reviewer's tree copies (scratchpad/ws3-wave2/review-WS3-12-frozen)

Four copies of the source tree made with `git archive`, one per commit. The reviewer wrote no file inside them: each was compared file by file with its commit (git blob ids), with 0 files added and 0 changed (29 files of each commit are absent from the copy, as in every git archive copy here). Its probes, runs, mutants and sha256 records sit beside the copies and are kept in place.

| Copy | Commit | Size | Where the commit lives |
|---|---|---|---|
| tree-6112b5e | 6112b5e (WS3-11 and WS3-12, first version) | 404M | local branches ws3-c and ws3-g only: kept in bundles/local-branches.bundle |
| tree-6c611b7 | 6c611b7 | 404M | the pushed working branch |
| r2/tree-07bf274 | 07bf274 (WS3-11 and WS3-12, fix round) | 412M | local branches ws3-c and ws3-g only: kept in bundles/local-branches.bundle |
| r2/tree-c21e69f | c21e69f | 412M | the pushed working branch |

Any copy can be made again with `git archive <commit> | tar -x -C <folder>` from the repository, or from the bundle for the two local-only commits (`git clone bundles/local-branches.bundle`).

## bundles/

- `local-branches.bundle`: every local branch of the work repository, minus what the remote already holds (32 heads; verified with `git bundle verify`). It also keeps the unpushed package branches (ws3-c to ws3-h, ws3-int) off the work machine.
- `local-heads.txt`: each local branch and its commit at the time of the bundle.

## Added at 20:32 UTC: the same reviewer's mutation tree (review-WS3-12-frozen/tree-mut, 404 MB)

A copy of the source tree at 6112b5e that the frozen-file reviewer used to plant mutants on 12 November between 00:54 and 01:35 UTC. Compared file by file with 6112b5e (git blob ids): 0 files added and 0 changed, because the reviewer restored each mutant after its run. Its mutant definitions and their results sit beside it (mutants/, mutants-vitest/, mutants.out, mutants-compare.out) and are kept in place. 6112b5e lives on local branches ws3-c and ws3-g and is in branches/local-branches.bundle of this repository.
