# GitHub migration and verification

The user explicitly selected private `tecxbro/imessagevideo` and authorized
replacing its current contents with the complete production library.

1. Inspected repository visibility, write access, default branch and tracked
   contents. The original main commit was `8e07ea3f6bd26f3753b0f289456d1e419f72992a`
   and contained only README.md.
2. Published `backup/pre-library-2026-11-10` at that exact commit before replacing
   files. The original README and history remain recoverable.
3. Restored all twelve complete private backup archives and all seventy-eight
   parts. Each part and whole archive matched the recorded SHA256. ZIP CRCs and
   direct internal payload hashes passed; all 14,161 extracted entries are present.
4. Added a local-first skill, portable registry, full-code/video viewer, Mac setup,
   new-session handoff, searchable inventory and exact contents/gap audit.
5. GitHub LFS rejected the first large object because the account exceeded its
   LFS budget. A draft Release was tried; draft-tag lookup and old gh flag
   incompatibility were diagnosed. The asset-upload endpoint then returned
   HTTP 401 Bad credentials. No token/billing/visibility change was made. No asset
   succeeded, and empty draft 440168960 was deleted. Historical prototypes remain
   under migration-source; they are not setup dependencies.
6. Switched to ordinary Git. All 78 original parts (at most 24 MiB each) and both
   small frozen snapshots are tracked alongside readable source/media/assets.
   Twelve whole ZIPs and two oversized Daniel scene copies are losslessly
   reconstructed by the offline sync helper, with exact whole/payload hashes.
   STORAGE.json lists every derived file; none requires Drive, LFS or Releases.
7. Published bounded batches on `import/complete-library`, keeping main intact
   while uploads and validation proceed. The completed main tree replaces the
   old contents using a normal fast-forwardable commit; no history force-push is
   needed. The backup branch remains the original recovery point.
8. Validation: fourteen offline reconstruction fixture checks pass; real normal
   sync and separate read-only verification pass for 12 archives, 78 parts, 2 snapshots
   and 14,161 extracted entries. Thirty stored result movies, six originals and
   full scenes match their registry sizes/hashes. The 38 director/toolkit tests
   pass. Viewer source hashes, script syntax, DOM references and 132 local links
   pass, with zero automatic external HTML media/script links.
9. An exhaustive streaming-SHA inventory lists every retained payload file and
   all exact code/video/analysis locations. Generated indexes use metadata-only
   self entries to avoid a recursive checksum cycle. Git internals, credentials,
   installed dependencies and caches are explicit exclusions. Archived original
   cache bytes remain preserved inside the original tracked archive parts.

The repository is the source for a local Mac clone; this cloud session did not
operate the user's Mac. Run the documented offline sync after cloning, then open
catalog/index.html. Rendering dependencies are separate from offline inspection.
No new full thirty-film render or interactive Mac/browser playback pass is
claimed. The original reference differences and Figma limits remain documented.

## Final branch promotion

A one-commit clean-history main candidate referenced the same complete tree as
the uploaded import branch. Its Git push failed with HTTP 500/disconnect; the
exact server-side cause was not established. Readback confirmed main had not
changed. The candidate and uploaded import tree both matched
`cb23d86d114942bbb134d447b2e98aea75760f5a`.

After proving the original main was an ancestor of the uploaded import head,
GitHub's normal reference API promoted main to
`cfddb9a155c6b163dd2489b9b3ecf5ca0bb8757a`, using expected old head
`8e07ea3f6bd26f3753b0f289456d1e419f72992a` and force=false. The API confirmed
success. No production data had to be retransmitted. A following small metadata
commit records this outcome and regenerates the file inventory; production
payloads and the already tested restoration code remain unchanged.
