# Git history audit

The source archive contains a linear local `main` history of 9 commits:

1. `712640dbb58f50762192de96a72e3e70b6e3904a` — `feat: initialize production-oriented expense tracker`
2. `b79deee954bf36d430d92dc595806937b7994d09` — `fix: make test discovery deterministic`
3. `e379eb8080b67b466c23b4f2064b9bc27866ce75` — `fix: harden money serialization and idempotent writes`
4. `d217e291dea842daab2f57793abcfd9d832af7a4` — `fix: compile frontend TypeScript for browser runtime`
5. `aa77a10c40891bca3edf6ccbb2fccd40ef32eacb` — `fix: enable frontend production build output`
6. `11329591a425823823e03d902242b519772a20cc` — `feat: add audit trail and production hardening`
7. `5c0e87da72a8779ce74e9da20f75580c2af9e24c` — `feat: enforce request fingerprints and database invariants`
8. `6113ef34de20c90b4a66ab09059350f63a79ed2a` — `chore: add production verification and GitHub handoff tooling`
9. `80b7fb7bd323f1b0d15d369fdac149a8c1e4a898` — `chore: add GitHub push handoff script`

The final source tree in the archive contains 43 tracked files. Generated caches and `backend/expense_tracker.db` are present in the archive but are not part of the final tracked tree.

The GitHub repository was initially empty, so the first sync was created as a new GitHub commit tree. The original local commit objects were not transferred at that point.

Exact original commit SHA preservation is not available through the currently exposed GitHub write contract used in this session because the commit operation accepts message, tree and parent SHA but does not expose the original author/committer timestamps and identities required to reproduce the original Git commit IDs.

Therefore the current `main` history intentionally starts from the synchronized repository state rather than claiming byte-for-byte Git-history preservation. The source-history metadata above is retained for future migration work.
