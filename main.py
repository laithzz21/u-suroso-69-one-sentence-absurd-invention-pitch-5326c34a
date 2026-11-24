#!/usr/bin/env python3
"""Entry for make.fun bounty: one-sentence absurd invention pitch.

Writes the one-sentence pitch for a ridiculous invention that fixes a
tiny everyday annoyance to the output directory (``/output/entry.txt``
by default, or ``$MAKEFUN_OUTPUT`` when set).

Python 3.13, stdlib only, deterministic: no network, clock, or randomness.
"""

import os

ENTRY = (
    "A toaster that ejects burnt toast with a tiny parachute and a "
    "pre-written apology note addressed to your smoke alarm, which "
    "has suffered enough."
)


def validate(text: str) -> None:
    """The entry must be exactly one sentence of 1-220 characters.

    One sentence means: a single line, no stray whitespace, ending in a
    single full stop, with no other sentence terminators (``.``, ``?``,
    ``!``) anywhere inside the text.
    """
    if not 1 <= len(text) <= 220:
        raise ValueError(f"entry must be 1-220 characters, got {len(text)}")
    if text != text.strip():
        raise ValueError("entry must not start or end with whitespace")
    if len(text.splitlines()) != 1:
        raise ValueError("entry must be a single line")
    if "\t" in text or "\r" in text:
        raise ValueError("entry must not contain tabs or carriage returns")
    if not text.endswith("."):
        raise ValueError("entry must end with a full stop (one sentence)")
    body = text[:-1]
    if any(ch in body for ch in ".?!"):
        raise ValueError("entry must be exactly one sentence")
    if "  " in text:
        raise ValueError("entry must not contain double spaces")


def resolve_out_path() -> str:
    """Resolve the output file path.

    ``$MAKEFUN_OUTPUT`` may point at a directory (``entry.txt`` is written
    inside it) or directly at a file (used as-is); the default is
    ``/output/entry.txt``, falling back to ``./output/entry.txt``.
    """
    requested = os.environ.get("MAKEFUN_OUTPUT") or "/output/entry.txt"
    if requested.endswith(".txt"):
        # Probe the parent directory so an unwritable direct file path
        # falls back early instead of failing at write time.
        parent = os.path.dirname(requested) or "."
        try:
            os.makedirs(parent, exist_ok=True)
            probe = os.path.join(parent, ".write_probe")
            with open(probe, "w", encoding="utf-8") as f:
                f.write("ok")
            os.remove(probe)
        except OSError:
            return os.path.join(os.getcwd(), "output", "entry.txt")
        return requested
    try:
        os.makedirs(requested, exist_ok=True)
        probe = os.path.join(requested, ".write_probe")
        with open(probe, "w", encoding="utf-8") as f:
            f.write("ok")
        os.remove(probe)
        return os.path.join(requested, "entry.txt")
    except OSError:
        return os.path.join(os.getcwd(), "output", "entry.txt")


def write_entry(path: str) -> None:
    """Write ENTRY to ``path``, creating its parent directory first."""
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(ENTRY)


def verify_entry(path: str) -> None:
    """Verify the written file by reading it back, byte for byte."""
    with open(path, "r", encoding="utf-8") as f:
        written = f.read()
    if written != ENTRY:
        raise RuntimeError("verification failed: written entry does not match")
    if len(written) != len(ENTRY) or len(written) > 220:
        raise RuntimeError("verification failed: written length mismatch")


def main() -> int:
    validate(ENTRY)
    path = resolve_out_path()
    try:
        write_entry(path)
    except OSError:
        # Fall back to a local output directory if the primary path
        # is not writable (e.g. no permission to create /output).
        path = os.path.join(os.getcwd(), "output", "entry.txt")
        write_entry(path)
    verify_entry(path)
    print(f"Wrote {len(ENTRY)}-character entry to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
