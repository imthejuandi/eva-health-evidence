# Removals of 12 November 2026, fourth set

Recorded at 2026-11-12 22:27 UTC, before removal. Reason: disk on the work machine stays near 4.6 GB while agents run, and the mop-up alias work no longer needs this clone.

## clones/mopup-alias_dry-run-clone: scratchpad/ws3-wave2/mopup-alias/dry-run-clone (573 MB)

This is the one scratch clone the mop-up's mocked dry run reuses (docs/signoff/work/mopup/dry-run/run.cjs --root). It was cloned from the mopup-alias worktree. It holds every dry run of the alias work, at 911e3cc, cfb93c8, e2bf169 without the map, 3c317c5 and 8a8a274: each state is kept on a branch of the clone, `dry-run/keep/<out folder>-<step>`.

What was recorded:
- `.head.txt`: HEAD, 6d067a4, the last dry run's rebuild commit, on 8a8a274.
- `.refs.txt`: all 145 refs with their commits.
- `.status.txt`: the working tree's 17 entries, 3 tracked files changed and 14 untracked, from run 2's last stage.
- `.diff`: the binary diff of the tracked changes against HEAD.
- `.untracked.tar.xz`: the 14 untracked files.
- `.bundle`: `git bundle create --all --not 3c317c5`, verified against the work repository.
  - 131 refs are in the bundle.
  - The other 14 point at ancestors of 3c317c5, which the work repository holds; they are kept by its remote and by `branches/local-branches.bundle`.
  - Every one of the 145 refs was checked: 0 missing.

Why the bundle starts at 3c317c5: the work repository is a shallow clone. Its boundary commit 64acdac has no parent locally, so a bundle of the whole history cannot be made. Every dry-run branch starts from an ancestor of 3c317c5.

Nothing else is unique to the clone: no stash, and the only ignored path is the node_modules link.

The dry runs' reports and outputs are kept in place, outside the clone: dry-run-*, fix-round/ and fix-round-2/ under scratchpad/ws3-wave2/mopup-alias/.

To restore: clone the work repository, run `git fetch <bundle> 'refs/*:refs/restored/*'`, check out 6d067a4, then apply the diff and untar the untracked files.
