"""Runs code inside GIMP for the tests, which themselves run on plain Python:
a probe runs in gimp-console-3.0 as project.sh runs an export script, measures
the image and writes the measurements as JSON, and the test checks them.

Inside GIMP, a probe has these helpers: build() paints the project's image,
png() writes a flattened copy of an image as PNG, and emit() hands the
results back. Its files go into the temporary folder TMP, so nothing is
written into the repository. Not a test itself.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
GIMP = shutil.which("gimp-console-3.0")

PRELUDE = '''
import json, os, sys
sys.path.insert(0, os.environ["PROBE_SCRIPTS"])
import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp, Gio
import common

TMP = os.environ["PROBE_TMP"]


def build(flatten=False):
    """The project's image, painted afresh."""
    image, _ = common.load_project(TMP, flatten=flatten)
    return image


def png(image, name, width=None, height=None):
    """Write a flattened copy of the image as TMP/<name>.png, scaled down to
    width x height if given, and return its path."""
    copy = image.duplicate()
    copy.flatten()
    if width:
        copy.scale(width, height)
    path = os.path.join(TMP, name + ".png")
    common.export("file-png-export", copy, path, compression=1, format="rgba8")
    return path


def emit(result):
    with open(os.path.join(TMP, "result.json"), "w") as f:
        json.dump(result, f)
'''


def projects():
    """The projects: folders of scripts/ holding <name>.py, where <name> is
    the part of the folder name after its last hyphen."""
    return sorted(folder.name for folder in SCRIPTS.iterdir()
                  if folder.is_dir()
                  and (folder / (folder.name.rsplit("-", 1)[-1] + ".py")).is_file())


def probe(project, code, tmp=None, scripts=SCRIPTS, timeout=1800):
    """Run the probe code in GIMP for a project and return what it emitted.
    Files the probe writes stay in tmp, if given, for the test to read."""
    own = tmp is None
    tmp = tmp or tempfile.mkdtemp()
    try:
        result = subprocess.run(
            [GIMP, "-i", "-d", "-f", "-s", "-n", "-c",
             "--batch-interpreter=python-fu-eval", "-b", "-", "--quit"],
            input=PRELUDE + "\n" + code, capture_output=True, text=True,
            timeout=timeout, cwd=ROOT,
            env={**os.environ, "PROJECT": project, "PROBE_TMP": str(tmp),
                 "PROBE_SCRIPTS": str(scripts), "PYTHONDONTWRITEBYTECODE": "1"},
        )
        path = Path(tmp, "result.json")
        if result.returncode != 0 or not path.exists():
            raise AssertionError(f"GIMP failed on {project} (exit {result.returncode}):\n"
                                 + (result.stdout + result.stderr)[-3000:])
        return json.loads(path.read_text())
    finally:
        if own:
            shutil.rmtree(tmp, ignore_errors=True)


def skip_reason():
    if not GIMP:
        return "needs gimp-console-3.0 on the PATH"
    if not projects():
        return "no projects"
    return None


def pillow():
    try:
        import PIL  # noqa: F401
        return True
    except ImportError:
        return False


if __name__ == "__main__":
    sys.exit("a helper for the tests, not a test")
