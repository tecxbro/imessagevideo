# Film exclusion fingerprints

Use Python 3.10 or newer with Pillow 9.1 or newer and FFmpeg on PATH.

The Observer generates the exclusion files in the private workspace:

```sh
python3 fingerprint.py fingerprint "$RESERVED_FILM" --output exclusion-01.json
```

Share the JSON alone. It contains an exact SHA-256 and a time series of quantized perceptual hashes. It contains no source name, URL, embedded metadata, thumbnails, or audio. Each exclusion file can contain one fingerprint object or an array of fingerprint objects.

Dataset checks each staged candidate before registering it:

```sh
python3 fingerprint.py check "$CANDIDATE" --exclusions exclusions.json
```

Repeat `--exclusions` to use multiple files. Exit 0 means clear against the supplied exclusions. Exit 1 means excluded by an exact hash or aligned visual match. Exit 2 means intake could not check the film or the exclusion file. Only exit 0 clears the candidate. JSON on stdout reports the outcome and hashes. A visual match also reports sample coverage, the fraction of aligned samples that match, and the mean perceptual distance.

The visual pass samples four frames a second. It compares low-frequency luminance, edge and contrast hashes across whole and centered views. A time alignment with at least 70% coverage of the longer film and 84% of the shorter film must pass the distance thresholds. The exact digest also detects copies shorter than two seconds. Crops, overlays and edits beyond the tested cases can reduce matching coverage or change the hashes. Static or near-identical footage can be ambiguous.

## Reproduce the checks

```sh
python3 test_fingerprint.py
```

The test generates its own neutral films. It exercises exact hash matches, resize plus frame-rate change and re-encoding, crop plus padding and an overlay, and an added intro with a trimmed tail. It exercises a reversed export, a rotated export and a different film with the same visual layout as clear candidates. It also checks the exclusion array format, fail-closed JSON parsing and absence of source filenames from CLI output.
