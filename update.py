#!/usr/bin/env python3

import re
import logging
import partial
import tarfile
import platform
import tempfile
from pathlib import Path

LOGGER = logging.getLogger("update")
logging.basicConfig(level=logging.DEBUG)

partial.keepalive()

# Find the zipped RTT sources inside the JLink installation
if platform.system() == "Darwin":
    apps = Path("/Applications")
elif platform.system() == "Linux":
    apps = Path("/opt")

tgz = next((apps / "SEGGER/JLink/Samples/RTT/").glob("*.tgz"))
# Extract that version number from the zip file name
tag = re.search(r"V(\d+)(\d{2})", tgz.stem)
tag = f"V{tag[1]}.{tag[2]}"
LOGGER.info(f"{tgz} => {tag}")

# untar the RTT sources to a temporary directory
with tempfile.TemporaryDirectory() as tmpdir:
    with tarfile.open(tgz, "r:gz") as tar:
        tar.extractall(tmpdir, filter="data")

    # print the extracted files
    tmpdir = Path(tmpdir)
    for file in tmpdir.glob("**/*"):
        LOGGER.debug(file.relative_to(tmpdir))

    # copy the RTT sources to the partial repository
    patterns = ["**/*.[chS]", "**/*.md"]
    files = partial.copy_files(tmpdir / tgz.stem, patterns)

# Commit the sources
partial.commit(files, tag)
