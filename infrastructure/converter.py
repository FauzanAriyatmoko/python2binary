from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

from python2binary.interfaces.interfaces import IConverter


class XxdConverter(IConverter):
    """Converts a .pyz archive to a C hex-array header using ``xxd -i``.

    The variable names produced by xxd are normalised to
    ``pyz_data`` and ``pyz_data_len`` so that the generated C launcher
    can reference them with fixed identifiers regardless of the input filename.
    """

    def convert(self, pyz_path: Path, output_dir: Path, app_name: str) -> Path:
        """Run ``xxd -i`` on *pyz_path* and write a normalised .h to *output_dir*.

        Args:
            pyz_path:   Path to the .pyz archive.
            output_dir: Destination directory for the .h file.
            app_name:   Used as the base name of the output file.

        Returns:
            Absolute path to the generated header file.

        Raises:
            RuntimeError: If ``xxd`` is not on PATH or conversion fails.
        """
        if shutil.which("xxd") is None:
            raise RuntimeError(
                "'xxd' was not found on PATH. "
                "Install it (e.g. 'apt-get install xxd') and retry."
            )

        if not pyz_path.is_file():
            raise FileNotFoundError(f"pyz_path does not exist: {pyz_path}")

        output_dir.mkdir(parents=True, exist_ok=True)
        header_path = output_dir / f"{app_name}.h"

        result = subprocess.run(
            ["xxd", "-i", str(pyz_path)],
            capture_output=True,
            text=True,
            check=True,
        )

        raw = result.stdout

        # xxd uses the filename (with path separators replaced by _) as the
        # variable name.  We normalise both the array and the length variable.
        normalised = self._normalise_identifiers(raw)

        header_path.write_text(normalised, encoding="utf-8")
        return header_path

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _normalise_identifiers(xxd_output: str) -> str:
        """Replace xxd-generated identifiers with fixed names.

        xxd produces something like::

            unsigned char some_path_file_pyz[] = { ... };
            unsigned int some_path_file_pyz_len = 1234;

        We replace these with ``pyz_data`` and ``pyz_data_len``.
        """
        # Match the array declaration line
        output = re.sub(
            r"unsigned char\s+\w+\[\]",
            "unsigned char pyz_data[]",
            xxd_output,
        )
        # Match the length declaration line
        output = re.sub(
            r"unsigned int\s+\w+_len",
            "unsigned int pyz_data_len",
            output,
        )
        return output
