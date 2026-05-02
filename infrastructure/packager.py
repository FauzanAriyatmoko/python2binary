from __future__ import annotations

import io
import zipfile
from pathlib import Path

from python2binary.interfaces.interfaces import IPackager
from python2binary.schemas.schemas import Python2BinaryConfig


class PyzPackager(IPackager):
    """Bundles a Python project directory into a .pyz zipapp archive.

    Only .py files are included; no dependency resolution is performed.
    The archive is made executable by prepending the standard zipapp shebang.
    """

    _SHEBANG = b"#!/usr/bin/env python3\n"

    def pack(self, config: Python2BinaryConfig) -> Path:
        """Walk *config.project_dir*, zip all .py files, write <app_name>.pyz.

        The zip entry ``__main__.py`` is used by Python as the entry point when
        the archive is run with ``python3 <archive>.pyz``.  If the user's
        entry script is already named ``__main__.py`` it is used as-is;
        otherwise a thin ``__main__.py`` shim is generated using
        ``runpy.run_module()``, which is zip-aware and does not try to
        open files as filesystem paths.

        Args:
            config: Build configuration.

        Returns:
            Absolute path to the generated .pyz file.

        Raises:
            FileNotFoundError: If project_dir or entry_script do not exist.
            RuntimeError: On any zip-building failure.
        """
        project_dir = config.project_dir
        entry_script = config.entry_script

        if not project_dir.is_dir():
            raise FileNotFoundError(f"project_dir does not exist: {project_dir}")

        entry_path = project_dir / entry_script
        if not entry_path.exists():
            raise FileNotFoundError(
                f"entry_script '{entry_script}' not found in {project_dir}"
            )

        config.output_dir.mkdir(parents=True, exist_ok=True)
        pyz_path = config.output_dir / f"{config.app_name}.pyz"

        # Collect all .py files relative to project_dir
        py_files: list[Path] = sorted(project_dir.rglob("*.py"))

        # Build raw zip in memory then prepend shebang
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for py_file in py_files:
                arcname = py_file.relative_to(project_dir)
                zf.write(py_file, arcname)

            # If the entry is not __main__.py, inject a shim so Python runs it.
            #
            # CRITICAL: use runpy.run_module(), NOT open() / exec().
            # The .pyz is a zip archive; Python's zipimport handles module
            # imports from it correctly.  Doing open('/tmp/foo.pyz/calon.py')
            # fails with NotADirectoryError because the .pyz is a file, not
            # a directory — you cannot treat paths inside it like filesystem
            # paths.
            if entry_script != "__main__.py":
                module_name = Path(entry_script).stem
                shim = (
                    "import runpy\n"
                    f"runpy.run_module({module_name!r}, run_name='__main__', alter_sys=True)\n"
                )
                if "__main__.py" not in [f.name for f in py_files]:
                    zf.writestr("__main__.py", shim)

        zip_data = buf.getvalue()

        with pyz_path.open("wb") as f:
            f.write(self._SHEBANG)
            f.write(zip_data)

        pyz_path.chmod(0o755)
        return pyz_path
