from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from python2binary.schemas.schemas import BuildResult, Python2BinaryConfig


class IPackager(ABC):
    """Stage 1 – Bundle the Python project into a .pyz zipapp archive."""

    @abstractmethod
    def pack(self, config: Python2BinaryConfig) -> Path:
        """Pack the project and return the path to the produced .pyz file.

        Args:
            config: Full build configuration.

        Returns:
            Absolute path to the generated .pyz file.

        Raises:
            RuntimeError: If packing fails.
        """


class IConverter(ABC):
    """Stage 2 – Convert a .pyz file to a C hex-array header via xxd -i."""

    @abstractmethod
    def convert(self, pyz_path: Path, output_dir: Path, app_name: str) -> Path:
        """Run xxd -i on *pyz_path* and write a .h header to *output_dir*.

        Args:
            pyz_path:   Path to the source .pyz archive.
            output_dir: Directory where the .h file will be written.
            app_name:   Base name used for the output file and C identifiers.

        Returns:
            Absolute path to the generated .h header file.

        Raises:
            RuntimeError: If xxd is unavailable or conversion fails.
        """


class ICompiler(ABC):
    """Stage 3 – Generate a C launcher and compile it to a native binary."""

    @abstractmethod
    def compile(self, hex_header_path: Path, config: Python2BinaryConfig) -> tuple[Path, Path]:
        """Generate a C source file, compile it, and return both paths.

        Args:
            hex_header_path: Path to the .h file produced by IConverter.
            config:          Full build configuration.

        Returns:
            A tuple of (c_source_path, binary_path).

        Raises:
            RuntimeError: If code generation or compilation fails.
        """