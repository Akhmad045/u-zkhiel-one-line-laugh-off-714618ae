#!/usr/bin/env python3
"""One-Line Laugh-Off — write one funny line to /output/entry.txt.

The joke: a meditation attempt derailed by an inner voice that will
not shut up — and worse, will only speak in a nature-documentary
accent, narrating the meditator like wildlife. One concrete image, one
turn, nothing left to trim.

Stdlib only, deterministic, no network, no randomness.
"""
import hashlib
import os
import sys

ENTRY = ("I tried to meditate, but my inner voice kept narrating "
         "in a nature-documentary accent.")

MAX_CHARS = 200


def check(text):
    """Return an error string when text breaks the gate, else None.

    Gate: 1 to 200 characters, not only whitespace, exactly one line —
    a single joke with no setup notes and no explanation.
    """
    if not isinstance(text, str):
        return "entry must be text"
    if len(text) == 0:
        return "entry is empty (gate needs 1-200 characters)"
    if len(text) > MAX_CHARS:
        return "entry is %d characters, over the 200-character gate" % len(text)
    if text.strip() == "":
        return "entry is only whitespace"
    if text.endswith("\n"):
        return "entry ends with a newline"
    if text != text.strip():
        return "entry has leading or trailing whitespace"
    if "\r" in text:
        return "entry must not contain a carriage return"
    if "\n" in text:
        return "entry must be exactly one line, got %d" % (text.count("\n") + 1)
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in text):
        return "entry contains a control character"
    return None


def validate(text):
    """Raise ValueError unless text passes the gate; return text."""
    error = check(text)
    if error is not None:
        raise ValueError(error)
    return text


def self_test():
    """Exercise check() against the gate's rejection and boundary cases."""
    reject = [
        ("", "empty"),
        ("   ", "whitespace-only"),
        ("x" * 201, "201 chars (over the 200 gate)"),
        ("one\ntwo", "two lines"),
        ("one\ntwo\nthree", "three lines"),
        (" hello", "leading whitespace"),
        ("hello ", "trailing whitespace"),
        ("hello\n", "trailing newline"),
        ("hello\rworld", "carriage return"),
        ("hel\x00lo", "control character"),
    ]
    for text, label in reject:
        error = check(text)
        if error is None:
            raise SystemExit("self-test FAIL: %s was accepted" % label)
        print("self-test ok: rejected %s: %s" % (label, error))
    for text, label in [
        ("a", "minimal one-char entry"),
        ("z" * 200, "200-char boundary"),
    ]:
        error = check(text)
        if error is not None:
            raise SystemExit("self-test FAIL: %s rejected: %s" % (label, error))
        print("self-test ok: %s accepted" % label)
    error = check(ENTRY)
    if error is not None:
        raise SystemExit("self-test FAIL: entry rejected: %s" % error)
    print("self-test ok: entry accepted (%d chars, %d bytes)"
          % (len(ENTRY), len(ENTRY.encode("utf-8"))))
    print("self-test: all cases passed")
    return 0


def main(argv):
    if len(argv) > 1 and argv[1] == "--self-test":
        return self_test()
    if len(argv) > 1:
        print("usage: main.py [--self-test]", file=sys.stderr)
        return 2
    text = validate(ENTRY)
    data = text.encode("utf-8")
    out_path = os.environ.get("ENTRY_OUTPUT", "/output/entry.txt")
    parent = os.path.dirname(out_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(out_path, "wb") as fh:
        fh.write(data)  # no trailing newline: the file is exactly the entry
    with open(out_path, "rb") as fh:
        roundtrip = fh.read()
    if roundtrip != data:
        raise SystemExit("round-trip mismatch: file does not match entry")
    print("wrote %s: %d chars, sha256 %s"
          % (out_path, len(text), hashlib.sha256(data).hexdigest()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
