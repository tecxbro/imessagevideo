"""Restore the original dataset ZIP from the files in this checkout."""
import csv
import hashlib
import os
import tempfile
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "imessage-video-dataset-pack.zip"
EXPECTED_SHA256 = "dce4f0dcb5ad4ad36d370dad98035c17a97b3cce311242b55449ab4d850473f1"


def file_digest(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    if OUTPUT.exists():
        if file_digest(OUTPUT) == EXPECTED_SHA256:
            print(OUTPUT)
            return
        raise SystemExit(f"A different file already exists at {OUTPUT}")
    with tempfile.NamedTemporaryFile(dir=ROOT, suffix=".zip", delete=False) as handle:
        temporary = Path(handle.name)
    try:
        with (ROOT / "tools/zip-members.tsv").open(newline="") as manifest, ZipFile(temporary, "w") as archive:
            for row in csv.DictReader(manifest, delimiter="\t"):
                name = row["path"]
                data = (ROOT / name).read_bytes()
                if hashlib.sha256(data).hexdigest() != row["sha256"]:
                    raise SystemExit(f"Checksum mismatch for {name}")
                stamp = datetime.fromisoformat(row["timestamp"]).timetuple()[:6]
                member = ZipInfo(name, stamp)
                member.create_system = 3
                member.external_attr = 0o100644 << 16
                archive.writestr(member, data, compress_type=int(row["compression"]), compresslevel=6)
        if file_digest(temporary) != EXPECTED_SHA256:
            raise SystemExit("The archive differs from the original ZIP.")
        os.replace(temporary, OUTPUT)
        print(OUTPUT)
    finally:
        if temporary.exists():
            temporary.unlink()


if __name__ == "__main__":
    main()
