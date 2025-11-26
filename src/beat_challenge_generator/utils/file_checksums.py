import os
import hashlib
from pathlib import Path
from typing import Tuple

CHUNK_SIZE = 8192

def file_checksum_and_size(path: Path) -> Tuple[str, int]:
    """Return (sha256_hex, size_bytes) for a file."""
    h = hashlib.sha256()
    total = 0
    with path.open("rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            h.update(chunk)
            total += len(chunk)
    return h.hexdigest(), total


def directory_checksum_and_size(dirpath: Path) -> Tuple[str, int]:
    """
    Deterministic checksum for a directory:
    - Walk files sorted by relative path
    - For each file include: relative_path + NUL + file_sha256 + NUL + file_size
    - Hash the concatenation with sha256
    Also returns the total size (sum of file sizes).
    """
    entries = []
    total = 0
    for root, _, files in os.walk(dirpath):
        for fn in files:
            full = Path(root) / fn
            rel = full.relative_to(dirpath).as_posix()
            chksum, size = file_checksum_and_size(full)
            entries.append((rel, chksum, size))
            total += size
    entries.sort(key=lambda t: t[0])
    h = hashlib.sha256()
    for rel, chksum, size in entries:
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(chksum.encode("ascii"))
        h.update(b"\0")
        h.update(str(size).encode("ascii"))
        h.update(b"\0")
    return h.hexdigest(), total
