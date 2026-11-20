# iMessage capture intake

Use Git, Python 3.11+, FFmpeg and FFprobe on PATH, and the Pillow version in
`requirements.txt`. Run the proof from a checkout of the Dataset branch.

```sh
python3 -m pip install -r datasets/imessage/requirements.txt
python3 datasets/imessage/prove.py
```

The proof runs the pinned Observer gate with an additional generated exclusion,
rejects its resized re-encode, admits a different authorized fixture, tests a
retry and multipart storage, and restores every registered capture from
committed files in a fresh sparse worktree. It also rejects missing rights,
a mismatched media hash, an incorrect PTS, an absent or stale approval, a
malformed exclusion manifest, and a corrupt archive part. Scratch outputs
are removed when the command exits.

## Submit and review a capture

1. Keep the complete original local. Probe its video and identify a continuous
   analysis window with the starting state, action, and ending hold visible.

   ```sh
   python3 datasets/imessage/intake.py probe /path/to/candidate.mov --frames 24 180
   ```

2. Make a JSON record using the [offline payment test record](../../review/imv-v3/dataset/payment-test.json)
   as a field example. Use `native` for device captures, `sandbox` for
   provider-confirmed test recordings, and `fixture` for authored test inputs.
   `range` uses **inclusive, zero-based decoded frame indices** and those
   frames’ exact presentation timestamps in `clock.time_base` ticks. Multiply
   ticks by that rational time base for seconds. Use this mapping for VFR
   captures as well. `average_fps` is descriptive. The intake archives the
   full original bytes. The range tells UI and Motion where to inspect.
3. Have a Dataset maintainer independently confirm the capture origin, exact
   device/OS/build, interaction and timestamps, and the holder's permission
   for private Git archive storage and team analysis. Before granting approval,
   inspect the entire file for third-party assets, personal data and payment
   details. Keep confidential source evidence in authorized private storage
   and cite a safe reference. Use this to compute the canonical record hash.

   ```sh
   python3 datasets/imessage/intake.py record-sha256 /path/to/capture.json
   ```

   The maintainer commits `approvals/<id>.json` on the trusted checkout with
   `record_sha256`, `reviewer`, `source_evidence` and `rights_evidence`.
   [Example committed grant](approvals/payment-test.json).
   The tool reads approvals from Git `HEAD`. This is the trust boundary for
   provenance assertions that a decoder cannot establish. The approval
   binds the scope and declared facts to the reviewed file bytes.
4. Run registration, then commit the generated manifest and archive or parts
   under `registry/<id>/`. A separate scratch registry can be selected with
   `--registry PATH`.

   ```sh
   git fetch --no-tags origin f926ed417a128845a7912cc23edb632561f26cdd
   python3 datasets/imessage/intake.py register /path/to/candidate.mov /path/to/capture.json
   ```

The gate reads the tool and three-reference exclusion manifest from the
pinned Observer Git object and verifies both SHA-256s. The proof fetches
the pin when needed, and intake and restore work offline once it is present.
Exit 0 means registered, exit 1 means excluded, and exit 2 means blocked.
An excluded result exposes only its match method. Observer’s detector
compares full films using sampled visual alignment. Its coverage thresholds
limit what it can establish about short excerpts, so verify the origin of
the complete original during review. An additional local exclusion file
can be added with `--extra-exclusions`; the pinned list always applies.
The receipt retains the additional list's digest for audit.

## Restore and hand off

```sh
python3 datasets/imessage/intake.py restore payment-test --out /tmp/imv-payment-test
```

Choose a fresh output directory. Restore verifies the whole ZIP, each part,
the committed approval, record hash, original clip hash, decoded clock and
landmarks. It reruns the pinned baseline gate before publishing the restored
directory. The manifest contains the capture record and precise landmark PTS
values. Archives over 24 MiB are split into sequential, hashed binary parts
using the repository's size convention. An exact registration retry preserves
the existing entry.

Give UI and Motion the capture manifest, media hash, time window and the
frames marking onset and settlement. See [capture status](CAPTURES.md) for the
native and provider evidence still needed, and [verification](VERIFICATION.md)
for the local proof and workflow status.
