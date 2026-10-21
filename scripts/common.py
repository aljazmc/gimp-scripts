import importlib
import os
import sys

import gi

gi.require_version("Gimp", "3.0")

from gi.repository import GObject, Gimp, Gio

scripts_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(scripts_dir)


def load_project(target, flatten=True):
    """Build the image of the project named by the PROJECT environment
    variable and return it with the output path (without extension) inside
    the root-level target directory.

    A project scripts/<theme>-<name>/ must provide <name>.py with a <name>()
    function returning a Gimp.Image, e.g.
    scripts/cyberpunk-butterfly00/butterfly00.py:butterfly00().

    Unless flatten is False (formats keeping layers), the image is flattened
    so exporters don't turn layers into pages, frames or icons.
    """
    project = os.environ.get("PROJECT")
    if not project:
        sys.exit("usage: PROJECT=<project> gimp-console-3.0 -i "
                 "--batch-interpreter=python-fu-eval -b - --quit < <script>")

    project_dir = os.path.join(scripts_dir, project)
    if not os.path.isdir(project_dir):
        sys.exit(f"project not found: {project_dir}")

    name = project.rsplit("-", 1)[-1]
    sys.path.insert(0, project_dir)
    image = getattr(importlib.import_module(name), name)()
    if flatten:
        image.flatten()

    target_dir = os.path.join(root_dir, target)
    os.makedirs(target_dir, exist_ok=True)

    return image, os.path.join(target_dir, project)


def square(image, size):
    """Crop the image to a centered square and scale it to size x size."""
    side = min(image.get_width(), image.get_height())
    image.crop(side, side,
               (image.get_width() - side) // 2,
               (image.get_height() - side) // 2)
    image.scale(size, size)


def int32_array(values):
    value = GObject.Value(Gimp.Int32Array)
    Gimp.value_set_int32_array(value, values)
    return value.get_boxed()


def export(procedure, image, filepath, **settings):
    """Run a file export (or save) procedure non-interactively.

    Keyword arguments are procedure settings, with "_" standing for "-",
    e.g. include_exif=True sets "include-exif". Lists become int32 arrays.
    """
    proc = Gimp.get_pdb().lookup_procedure(procedure)
    config = proc.create_config()
    config.set_property("run-mode", Gimp.RunMode.NONINTERACTIVE)
    config.set_property("image", image)
    config.set_property("file", Gio.File.new_for_path(filepath))
    for key, value in settings.items():
        if isinstance(value, list):
            value = int32_array(value)
        config.set_property(key.replace("_", "-"), value)

    result = proc.run(config)
    if result.index(0) != Gimp.PDBStatusType.SUCCESS:
        sys.exit(f"{procedure} failed for {filepath}: {result.index(0)}")

    image.delete()
