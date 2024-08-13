"""Metadata for envwrap - 🚀 Override function defaults with environment variables.

MIT License

Copyright © 2024 Parker Wahle

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""  # noqa: E501, B950

from __future__ import annotations

import logging

try:
    from importlib.metadata import PackageMetadata
    from importlib.metadata import PackageNotFoundError
    from importlib.metadata import metadata as __load
except ImportError:  # pragma: no cover
    from importlib_metadata import PackageMetadata  # type: ignore
    from importlib_metadata import PackageNotFoundError  # type: ignore
    from importlib_metadata import metadata as __load  # type: ignore


logger = logging.getLogger(__package__)
try:
    metadata: PackageMetadata = __load(__package__)
    __uri__ = metadata["home-page"]
    __title__ = metadata["name"]
    __summary__ = metadata["summary"]
    __license__ = metadata["license"]
    __version__ = metadata["version"]
    __author__ = metadata["author"]
    __maintainer__ = metadata["maintainer"]
    __contact__ = metadata["maintainer"]
except PackageNotFoundError:  # pragma: no cover
    logger.error(f"Could not load package metadata for {__package__}. Is it installed?")
    logger.debug("Falling back to static metadata.")
    __uri__ = ""
    __title__ = "envwrap"
    __summary__ = "🚀 Override function defaults with environment variables"
    __license__ = "MIT"
    __version__ = "0.0.0"
    __author__ = "Parker Wahle"
    __maintainer__ = "Parker Wahle"
    __contact__ = "Parker Wahle"
__copyright__ = "Copyright 2024"


__all__ = (
    "__copyright__",
    "__uri__",
    "__title__",
    "__summary__",
    "__license__",
    "__version__",
    "__author__",
    "__maintainer__",
    "__contact__",
)
