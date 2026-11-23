# Final streamed ZIP audit

Prepared tool: `verification/audit_delivery_zip.py`. No final delivery ZIP has been audited yet. Root supplies it after final capture, audio, review, skill and packaging gates.

```sh
python3 verification/audit_delivery_zip.py \
  --archive imessage-recreations-delivery.zip \
  --stage delivery-package-final \
  --out verification/packaging-audit/final-zip-audit.json
```

`--stage` is optional. It adds a read-only hash/coverage comparison with the existing stage. It creates no second extracted tree. The report must stay outside the ZIP and sealed stage.

The audit checks every ZIP entry's safe portable name, root prefix and regular-file mode; duplicate/case/Unicode collisions and symlinks are rejected. Every payload is streamed for CRC32, decoded size and SHA256. Exact outer checksum coverage excludes only `imessage-recreations/checksums.json`; nested skill checksum files remain required hashed entries.

The installable skill ZIP is held compressed in bounded memory (maximum64MiB), then each member is streamed. Its own root checksums must exactly cover its payloads. The expanded skill folder's checksums are verified separately, and every relative file/hash must match the installable skill ZIP, including their checksum manifest. Font/video filename extensions, binary signatures and embedded font/video data URIs are rejected inside both skill forms. The outer delivery can contain its intentionally declared font/media assets.

Report fields include `passed`, the complete archive SHA256, per-entry CRC/SHA and counts, exact coverage differences, expanded/nested skill results, optional stage differences, and explicit errors. Exit status is nonzero on failure. No file is extracted; only checksum manifests and the small compressed skill ZIP are retained in memory. Skill uncompressed size is bounded at256MiB. This is integrity/portability validation, not a source-fidelity or legal-content classifier for arbitrary opaque formats.

Syntax checks and17 synthetic fixture tests passed; see `zip-audit-tool-tests.json` and `verification/test_audit_delivery_zip.py`. These cover CRC corruption, SHA mismatch, missing/unhashed files, the nested-checksum exemption regression, traversal, symlink metadata, duplicate/case-colliding names, renamed font/video payloads, embedded font data, skill mismatch and stage drift.
