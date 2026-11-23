#!/usr/bin/env python3
"""Ship the committed front page as this entry's image.

Reads entry.png from beside this file, checks it is a complete PNG
inside the competition limits (signature, IHDR size, every chunk CRC,
IEND last), then writes an exact copy to the output directory.
Standard library only; no network; no environment reads. Because the
output is a byte copy of the committed file, two runs always produce
identical bytes.
"""
import hashlib
import os
import struct
import sys
import zlib

LIMIT_BYTES = 1_048_576
LIMIT_SIDE = 1024
SIGNATURE = b"\x89PNG\r\n\x1a\n"
DEFAULT_OUTPUT = "/output"


def die(message):
    sys.stderr.write("main.py: " + message + "\n")
    sys.exit(1)


def walk_chunks(blob):
    """Yield (kind, body) for each chunk, checking framing and CRCs."""
    if len(blob) < 8 or blob[:8] != SIGNATURE:
        die("entry.png does not start with the PNG signature")
    if len(blob) > LIMIT_BYTES:
        die("entry.png is %d bytes, over the %d limit"
            % (len(blob), LIMIT_BYTES))
    offset = 8
    while True:
        header = blob[offset:offset + 8]
        if len(header) < 8:
            die("PNG ends inside a chunk header")
        size, kind = struct.unpack(">I4s", header)
        end = offset + 12 + size
        if end > len(blob):
            die("chunk %r runs past the end of entry.png" % kind)
        body = blob[offset + 8:offset + 8 + size]
        stored = struct.unpack(">I", blob[offset + 8 + size:end])[0]
        actual = zlib.crc32(kind + body) & 0xFFFFFFFF
        if stored != actual:
            die("chunk %r fails its CRC check" % kind)
        yield kind, body
        if kind == b"IEND":
            if size:
                die("IEND chunk must be empty")
            if end != len(blob):
                die("trailing bytes after the IEND chunk")
            return
        offset = end


def validate(blob):
    """Check the PNG structure and return (width, height, chunk count)."""
    width = height = 0
    have_data = have_end = False
    count = 0
    for kind, body in walk_chunks(blob):
        count += 1
        if count == 1:
            if kind != b"IHDR" or len(body) != 13:
                die("first chunk must be a 13-byte IHDR")
            width, height = struct.unpack(">II", body[:8])
            depth, colour = body[8], body[9]
            if depth != 8 or colour not in (2, 6):
                die("PNG must be 8-bit RGB or RGBA, got depth %d colour %d"
                    % (depth, colour))
            if not width or not height:
                die("PNG dimensions must be positive")
            if width > LIMIT_SIDE or height > LIMIT_SIDE:
                die("PNG is %dx%d, over the %dx%d limit"
                    % (width, height, LIMIT_SIDE, LIMIT_SIDE))
        elif kind == b"IDAT":
            have_data = True
        elif kind == b"IEND":
            have_end = True
    if not have_data:
        die("PNG carries no IDAT chunk")
    if not have_end:
        die("PNG carries no IEND chunk")
    return width, height, count


def output_dir():
    if len(sys.argv) > 1:
        return sys.argv[1]
    return DEFAULT_OUTPUT


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source_path = os.path.join(here, "entry.png")
    try:
        with open(source_path, "rb") as handle:
            blob = handle.read()
    except OSError:
        die("entry.png is not beside main.py")
    width, height, count = validate(blob)
    target_dir = output_dir()
    os.makedirs(target_dir, exist_ok=True)
    target_path = os.path.join(target_dir, "entry.png")
    with open(target_path, "wb") as handle:
        handle.write(blob)
    with open(target_path, "rb") as handle:
        written = handle.read()
    if hashlib.sha256(written).digest() != hashlib.sha256(blob).digest():
        die("written entry.png differs from the source bytes")
    print("entry.png: %d bytes, %dx%d, %d chunks, sha256 %s -> %s"
          % (len(blob), width, height, count,
             hashlib.sha256(blob).hexdigest()[:16], target_path))


if __name__ == "__main__":
    main()
