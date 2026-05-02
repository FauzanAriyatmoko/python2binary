"""python2binary – Python-to-binary CLI entry point.

Usage
-----
    python main.py --project <dir> --entry <script> --output <dir> [--name <name>]

Example
-------
    python main.py --project /tmp/my_app --entry __main__.py --output /tmp/build --name my_app
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from python2binary.infrastructure.compiler import CCompiler
from python2binary.infrastructure.converter import XxdConverter
from python2binary.infrastructure.packager import PyzPackager
from python2binary.pipeline import Python2BinaryPipeline
from python2binary.schemas.schemas import Python2BinaryConfig


def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python2binary",
        description=(
            "Bundle a Python project into a self-contained native binary.\n\n"
            "Pipeline:\n"
            "  1. Pack project .py files into a .pyz zipapp\n"
            "  2. xxd -i  → C hex-array header\n"
            "  3. gcc     → native binary (embeds .pyz, executes via python3)"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--project", "-p",
        required=True,
        metavar="DIR",
        help="Root directory of the Python project to package.",
    )
    p.add_argument(
        "--entry", "-e",
        required=True,
        metavar="SCRIPT",
        help=(
            "Entry-point script relative to --project "
            "(e.g. '__main__.py' or 'app/main.py')."
        ),
    )
    p.add_argument(
        "--output", "-o",
        required=True,
        metavar="DIR",
        help="Output directory for all build artefacts.",
    )
    p.add_argument(
        "--name", "-n",
        metavar="NAME",
        default=None,
        help=(
            "Base name for output files. "
            "Defaults to the project directory's basename."
        ),
    )
    return p


def main(argv: list[str] | None = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    project_dir = Path(args.project)
    app_name = args.name or project_dir.name

    config = Python2BinaryConfig(
        project_dir=project_dir,
        entry_script=args.entry,
        output_dir=Path(args.output),
        app_name=app_name,
    )

    pipeline = Python2BinaryPipeline(
        packager=PyzPackager(),
        converter=XxdConverter(),
        compiler=CCompiler(),
    )

    result = pipeline.run(config)

    if result.success:
        print("\n[python2binary] Build successful!")
        print(f"  .pyz     : {result.pyz_path}")
        print(f"  .h       : {result.hex_header_path}")
        print(f"  .c       : {result.c_source_path}")
        print(f"  binary   : {result.binary_path}")
        return 0
    else:
        print(f"\n[python2binary] Build FAILED at stage(s): {result.stages_completed}", file=sys.stderr)
        print(result.error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
