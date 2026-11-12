# Removed on 12 November 2026 to keep disk above 5 GB (no proof lost)

## scratchpad/venv (562 MB)
A Python 3.11.17 virtual environment made on 30 October 2026; MANIFEST.md lists it as tools or downloads, not proof. Its packages, to rebuild it:

```
autograd==1.9.1
autograd-gamma==0.5.0
cloudpickle==3.1.2
contourpy==1.3.3
cycler==0.12.1
fonttools==4.68.0
formulaic==1.2.2
interface_meta==2.0.1
joblib==1.6.0
kiwisolver==1.5.1
lifelines==0.30.3
matplotlib==3.11.2
narwhals==2.28.0
numpy==2.4.6
packaging==26.3
pandas==2.3.3
patsy==1.0.3
pillow==13.0.0
pyparsing==3.3.3
pyreadr==0.5.7
python-dateutil==3.0.0
pytz==2026.6
scikit-learn==1.9.1
scipy==1.17.1
six==1.17.0
statsmodels==0.15.0
threadpoolctl==3.7.0
typing_extensions==4.16.0
tzdata==2026.6
wrapt==2.5.2
```

## scratchpad/gov-review/refusal-clone (426 MB)
A clean clone used by the governance reviewer: HEAD detached at 29346867f96c6d864213bd5c76ca14a62ead7cce, git status empty, no stash, no untracked files; every local branch points to a commit that the eva-health repository holds:

- gov 47059923bbc5f4ace5cd279deed40d95a8236b34

The reviewer's outputs beside it (refusal-out, cache-rerun, round2, online) are kept.

## scratchpad/mopup-impl/dry-run/attempt4/clone (549 MB) and clone-run0 (401 MB)
The mocked dry run's reused clone (155 branches, every dry run's steps kept as dry-run/keep/* branches) and the first run's clone. Kept here, in clones/: for each, its HEAD, its refs, its git status, its tracked changes as a binary diff, its untracked files (tar.xz), and a git bundle of every local branch's commits that are not on the clone's remote-tracking branches (155 of 155 heads and 1 of 1; both verify against the eva-health repository, which holds their prerequisites). A clone can be rebuilt with: git clone <eva-health>; git fetch <bundle> 'refs/heads/*:refs/heads/*'; check out the HEAD; apply the diff; unpack the untracked files. The dry-run outputs beside it (attempt4/run*, attempt5 to attempt21) are kept.

## scratchpad/ws3-wave2/decide-WS3-09/snap (392 MB)
A file copy of the repository tree that the WS3-09 decider compared against (not a git repository). Kept whole as decide-WS3-09-snap.tar.xz (17.7 MB). The decider's other files (c30, diffs.json, strict.ts) are kept.

## scratchpad/ws3-wave2/review-WS3-39-frozen: before-tree, after-tree, old-6c611b7, old-origin-main (1.2 GB)
The frozen D4 reviewer's copies, made with git archive of b3cafa4, 118f61e, 6c611b7 and origin/main (c472974): every file carries its commit's time. The only files written later, kept in that folder's kept-from-trees/: after-tree/zz-review/dash.ts and fake-gates.ts, old-6c611b7/zz-review/dash.ts, and old-6c611b7/scripts/signoff/checks/data.ts (the 118f61e runner file placed on the old app to probe the old gate). The reviewer's results (review.json, runs/ with 184 runs, the .out files) are kept.
