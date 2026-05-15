#!/usr/bin/env python3
"""
Trim a video to the first N seconds (default: 4).

Usage:
    python scripts/trim_video.py [input_path] [--seconds 4]

Replaces the input file in place after writing a .bak backup.
Requires ffmpeg on PATH.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "static" / "videos" / "other-equila.mp4"


def run_ffmpeg_trim(src: Path, dst: Path, seconds: float) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg not found on PATH. Install ffmpeg and try again.")

    cmd = [
        ffmpeg,
        "-y",
        "-i",
        str(src),
        "-t",
        str(seconds),
        "-c",
        "copy",
        "-avoid_negative_ts",
        "make_zero",
        str(dst),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        # Stream copy can fail on some cuts; re-encode fallback
        cmd_reencode = [
            ffmpeg,
            "-y",
            "-i",
            str(src),
            "-t",
            str(seconds),
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "23",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-movflags",
            "+faststart",
            str(dst),
        ]
        result = subprocess.run(cmd_reencode, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(
                f"ffmpeg failed:\n{result.stderr or result.stdout}"
            )


def trim_video(input_path: Path, seconds: float = 4.0, backup: bool = True) -> Path:
    input_path = input_path.resolve()
    if not input_path.is_file():
        raise FileNotFoundError(input_path)

    temp_out = input_path.with_name(input_path.stem + ".trim.tmp" + input_path.suffix)
    backup_path = input_path.with_name(input_path.stem + ".bak" + input_path.suffix)

    try:
        run_ffmpeg_trim(input_path, temp_out, seconds)

        if backup:
            if backup_path.exists():
                backup_path.unlink()
            input_path.replace(backup_path)

        temp_out.replace(input_path)
        return input_path
    except Exception:
        if temp_out.exists():
            temp_out.unlink()
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Trim video to first N seconds.")
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"Input video (default: {DEFAULT_INPUT})",
    )
    parser.add_argument(
        "--seconds",
        "-t",
        type=float,
        default=4.0,
        help="Duration to keep from the start (default: 4)",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Do not keep a .bak copy of the original file",
    )
    args = parser.parse_args()

    out = trim_video(args.input, seconds=args.seconds, backup=not args.no_backup)
    print(f"Trimmed to {args.seconds}s: {out}")
    if not args.no_backup:
        print(f"Backup: {out.with_suffix(out.suffix + '.bak')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
