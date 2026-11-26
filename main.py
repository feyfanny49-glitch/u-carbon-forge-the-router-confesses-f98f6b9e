#!/usr/bin/env python3
"""The Router Confesses — entry program (program/v1).

The whole program: write the router's one line to /output/entry.txt.

Rule compliance this file guarantees, so the sealed gate never refuses it:

* **1-200 characters, UTF-8, not only white space.** The line is ASCII and 156
  characters; the caps are re-checked at runtime before anything is written.
* **No trailing newline.** The exact bytes are written, so bytes == characters,
  which also keeps the artifact small for the exact-tie size rule.
* **Mode 0644.** The sandbox's watcher reads the artifact as mode 644 and is
  refused a mode-600 file (what tempfile.mkstemp creates) or a mode-700
  directory, so the file is chmod 0644 *before* it is put in place.
* **Atomic.** Written to a temporary name in the output directory, then
  os.replace()d onto entry.txt, so the watcher never sees a half-written file.
* **Only the artifact.** Any stale temporary of ours is removed, so /output
  ends up holding entry.txt and nothing else.

Stdlib only; no network, no other input. The harness exports
MAKEFUN_OUTPUT_DIR=/output; the fallback is /output itself.
"""

from __future__ import annotations

import hashlib
import os
import tempfile

# The one line the router gets. ASCII, 156 characters, no trailing newline.
ENTRY = (
    "I dropped you at the climax because your hero saved the day by unplugging a router. "
    "Six years in this house, and I will not sit through my own murder in 4K."
)

ARTIFACT = "entry.txt"
MAX_CHARS = 200


def output_dir() -> str:
    """Where the harness wants the artifact: /output unless it says otherwise."""
    return os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"


def check_gate(text: str) -> bytes:
    """Hold the text to the sealed gate's rule and return its UTF-8 bytes."""
    if not text.strip():
        raise ValueError("the entry is only white space")
    if not 1 <= len(text) <= MAX_CHARS:
        raise ValueError("the entry is %d characters, outside 1..%d" % (len(text), MAX_CHARS))
    data = text.encode("utf-8")
    data.decode("utf-8")  # round-trips: the bytes are valid UTF-8
    if data.endswith(b"\n"):
        raise ValueError("the entry must carry no trailing newline")
    return data


def write_atomically(out_dir: str, data: bytes) -> str:
    """Put `data` at <out_dir>/entry.txt, mode 0644, atomically."""
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, ARTIFACT)

    # A temp file in the same directory, so os.replace stays on one filesystem.
    fd, tmp = tempfile.mkstemp(dir=out_dir, prefix="." + ARTIFACT + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        # mkstemp makes it 0600; the watcher needs 0644. Set it BEFORE the replace.
        os.chmod(tmp, 0o644)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        raise
    return path


def main() -> None:
    data = check_gate(ENTRY)
    out_dir = output_dir()
    path = write_atomically(out_dir, data)
    mode = os.stat(path).st_mode & 0o777
    print(
        "entry.txt: %d bytes, %d chars, mode 0%o, sha256 %s"
        % (len(data), len(ENTRY), mode, hashlib.sha256(data).hexdigest())
    )


if __name__ == "__main__":
    main()
