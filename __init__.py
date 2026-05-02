"""python2binary – Python-to-native-binary compiler library.

Typical usage
-------------
::

    from pathlib import Path
    from python2binary import Python2BinaryConfig, Python2BinaryPipeline
    from python2binary import PyzPackager, XxdConverter, CCompiler

    config = Python2BinaryConfig(
        project_dir=Path("./myapp"),
        entry_script="__main__.py",
        output_dir=Path("./build"),
        app_name="myapp",
    )

    pipeline = Python2BinaryPipeline(
        packager=PyzPackager(),
        converter=XxdConverter(),
        compiler=CCompiler(),
    )

    result = pipeline.run(config)
    if result.success:
        print(f"Binary: {result.binary_path}")
"""

from python2binary.infrastructure.compiler import CCompiler
from python2binary.infrastructure.converter import XxdConverter
from python2binary.infrastructure.packager import PyzPackager
from python2binary.interfaces.interfaces import ICompiler, IConverter, IPackager
from python2binary.pipeline import Python2BinaryPipeline
from python2binary.schemas.schemas import BuildResult, Python2BinaryConfig

__all__ = [
    # Config & result
    "Python2BinaryConfig",
    "BuildResult",
    # Pipeline
    "Python2BinaryPipeline",
    # Concrete implementations
    "PyzPackager",
    "XxdConverter",
    "CCompiler",
    # Interfaces (for custom implementations)
    "IPackager",
    "IConverter",
    "ICompiler",
]

__version__ = "0.1.0"
