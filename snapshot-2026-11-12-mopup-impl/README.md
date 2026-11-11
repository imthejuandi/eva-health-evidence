# Mop-up tooling: proof of the builder test and the mocked dry run (12 November 2026)

The mop-up tooling (branch mopup, commit 4dc4f76 in eva-health) was tested in scratch copies of the repository. This folder keeps the proof before the copies are removed to free disk space:

- `mopup-impl-outputs.tar.xz`: every output of the implementer's scratch folder (builder runs and checks, the seven dry-run attempts' logs and results, probes, patches, tests), without the repository copies.
- `clones/`: for each repository copy that is removed, its base commit and branches, its git status, its tracked changes as a binary diff (`*.diff`) and its untracked files (`*.untracked.tar.xz`). A copy can be rebuilt by checking out the base commit, applying the diff and unpacking the untracked files.
- `SHA256SUMS`: checksums of every file here.

The copy reused by the final dry runs (attempt 4, with attempts 5 to 7 kept on its branches) stays on the working machine and goes into the end-of-programme snapshot.
