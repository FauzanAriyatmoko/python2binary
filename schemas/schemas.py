from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Python2BinaryConfig:
    """Configuration for a single python2binary build."""

    project_dir: Path
    """Root directory of the Python project to package."""

    entry_script: str
    """Relative path to the entry-point script inside project_dir (e.g. '__main__.py')."""

    output_dir: Path
    """Directory where all build artefacts will be written."""

    app_name: str
    """Base name used for all output files (e.g. 'hello' → hello.pyz, hello.h, hello)."""

    def __post_init__(self) -> None:
        self.project_dir = Path(self.project_dir).resolve()
        self.output_dir = Path(self.output_dir).resolve()


@dataclass
class BuildResult:
    """Holds the outcome of a full python2binary pipeline run."""

    pyz_path: Path | None = None
    """Path to the generated .pyz zipapp archive."""

    hex_header_path: Path | None = None
    """Path to the generated C hex-array header (.h)."""

    c_source_path: Path | None = None
    """Path to the generated C launcher source file."""

    binary_path: Path | None = None
    """Path to the compiled native binary."""

    success: bool = False
    """True if all stages completed without error."""

    error: str = ""
    """Human-readable error message when success is False."""

    stages_completed: list[str] = field(default_factory=list)
    """Names of pipeline stages that finished successfully."""
