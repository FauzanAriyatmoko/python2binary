from __future__ import annotations

import traceback
from pathlib import Path

from python2binary.interfaces.interfaces import ICompiler, IConverter, IPackager
from python2binary.schemas.schemas import BuildResult, Python2BinaryConfig


class Python2BinaryPipeline:
    """Orchestrates the three-stage python2binary build pipeline.

    Stages run in order:
        1. :class:`~interfaces.interfaces.IPackager`  – produce .pyz
        2. :class:`~interfaces.interfaces.IConverter` – hexdump .pyz → .h
        3. :class:`~interfaces.interfaces.ICompiler`  – generate C + compile binary

    Any stage failure short-circuits the pipeline and populates
    :attr:`~schemas.schemas.BuildResult.error` with a diagnostic message.
    """

    def __init__(
        self,
        packager: IPackager,
        converter: IConverter,
        compiler: ICompiler,
    ) -> None:
        self._packager = packager
        self._converter = converter
        self._compiler = compiler

    def run(self, config: Python2BinaryConfig) -> BuildResult:
        """Execute all stages for *config* and return the result.

        Args:
            config: Build configuration.

        Returns:
            A :class:`~schemas.schemas.BuildResult` describing the outcome.
        """
        result = BuildResult()

        # ------------------------------------------------------------------
        # Stage 1: Pack
        # ------------------------------------------------------------------
        try:
            print(f"[python2binary] Stage 1 – Packing '{config.project_dir}' → .pyz …")
            pyz_path = self._packager.pack(config)
            result.pyz_path = pyz_path
            result.stages_completed.append("pack")
            print(f"[python2binary]   ✓ {pyz_path}")
        except Exception as exc:
            result.error = f"[pack] {exc}\n{traceback.format_exc()}"
            return result

        # ------------------------------------------------------------------
        # Stage 2: Convert (xxd -i)
        # ------------------------------------------------------------------
        try:
            print(f"[python2binary] Stage 2 – Converting .pyz → C hex header …")
            hex_header_path = self._converter.convert(
                pyz_path, config.output_dir, config.app_name
            )
            result.hex_header_path = hex_header_path
            result.stages_completed.append("convert")
            print(f"[python2binary]   ✓ {hex_header_path}")
        except Exception as exc:
            result.error = f"[convert] {exc}\n{traceback.format_exc()}"
            return result

        # ------------------------------------------------------------------
        # Stage 3: Compile
        # ------------------------------------------------------------------
        try:
            print(f"[python2binary] Stage 3 – Generating C launcher + compiling …")
            c_path, binary_path = self._compiler.compile(hex_header_path, config)
            result.c_source_path = c_path
            result.binary_path = binary_path
            result.stages_completed.append("compile")
            print(f"[python2binary]   ✓ C source : {c_path}")
            print(f"[python2binary]   ✓ Binary   : {binary_path}")
        except Exception as exc:
            result.error = f"[compile] {exc}\n{traceback.format_exc()}"
            return result

        result.success = True
        return result
