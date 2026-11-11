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
