# gimp-scripts

[![lint](https://github.com/aljazmc/gimp-scripts/actions/workflows/lint.yml/badge.svg)](https://github.com/aljazmc/gimp-scripts/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![GIMP 3](https://img.shields.io/badge/GIMP-3-5c5543?logo=gimp&logoColor=white)](https://www.gimp.org/)
[![Python 3](https://img.shields.io/badge/Python-3-3776ab?logo=python&logoColor=white)](https://developer.gimp.org/api/3.0/libgimp/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![ShellCheck](https://img.shields.io/badge/ShellCheck-checked-4eaa25?logo=gnubash&logoColor=white)](https://www.shellcheck.net/)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-fe5196?logo=conventionalcommits&logoColor=white)](https://www.conventionalcommits.org/)

Raster images painted as code. Python scripts paint with layers, paths,
gradients, selections and GEGL filters in GIMP 3 through its
`gi.repository.Gimp` API, and a shell script exports the result with GIMP to
PNG, JPEG, Photoshop, icons, brushes and more, 50 formats in all.

![cyberpunk-butterfly00: a neon butterfly over a synthwave grid and a striped sun](gallery/cyberpunk-butterfly00.png)

## Features

- **Images from code.** A project returns a layered `Gimp.Image`, painted
  with the same tools a person would use in GIMP.
- **50 outputs.** 49 export formats, from PNG, JPEG and WebP to Photoshop,
  OpenRaster, icons, cursors, brushes, ASCII art and a C header, plus
  GIMP's own `xcf`.
- **Sensible defaults per format.** Layers are flattened where an exporter
  would otherwise turn them into pages or frames, kept in `xcf`, `psd` and
  `ora`, and icons and brushes are cropped and scaled to 256×256.
- **Headless and safe.** GIMP runs without a user interface and never hands
  the batch over to a running GIMP.
- **One subject in three tools.** The butterfly is also an SVG drawing in
  [inkscape-scripts](https://github.com/aljazmc/inkscape-scripts) and an
  animated 3D scene in
  [blender-scripts](https://github.com/aljazmc/blender-scripts), with the
  same coordinates.

## Quick start

```sh
git clone https://github.com/aljazmc/gimp-scripts.git
cd gimp-scripts
./project.sh cyberpunk-butterfly00 png
```

The image is written to `build/cyberpunk-butterfly00.png`.

## Requirements

| Requirement | Notes |
| --- | --- |
| GIMP 3 | `gimp-console-3.0` on the `PATH`; set `GIMP` at the top of `project.sh` for another name |

GIMP brings its Python plug-in support, so nothing else needs to be
installed.

## Usage

```sh
./project.sh <project> <format>        # build one format
./project.sh <project> all             # build every format
./project.sh all <format>              # build every project
./project.sh <project> <format> clean  # remove one output
./project.sh <project> clean           # remove all outputs of a project
./project.sh clean                     # remove build/ and xcf/
```

Outputs go to `build/<project>.<format>`, and `xcf` outputs to
`xcf/<project>.xcf`. Existing outputs are skipped, so clean them to
rebuild. The script can be run from any directory. Without arguments, it
prints the usage with every format and the first ten projects.

### Formats

| Kind | Formats |
| --- | --- |
| Images | `png` `jpg` `webp` `avif` `heif` `jxl` `qoi` `gif` `bmp` `tif` `tga` `pcx` `ras` `sgi` `xwd` `pix` `ff` `dds` `exr` `hdr` `pfm` `fits` `dcm` |
| Bitmaps and maps | `pbm` `pgm` `ppm` `pnm` `pam` `xbm` `xpm` |
| Documents | `pdf` `ps` `eps` |
| Layered | `psd` `ora` `xcf` |
| Icons, cursors, brushes, patterns | `ico` `icns` `cur` `ani` `xmc` `gbr` `gih` `pat` |
| Animation and other | `fli` `cel` `data` `h` `html` `txt` |

- Most formats get the full image, flattened into one layer so that
  exporters don't turn layers into pages, frames or icons.
- `xcf`, `psd` and `ora` keep the layers, to open and edit the image later.
- Icons, cursors, brushes and patterns (`ani cur gbr gih icns ico pat xmc`)
  are cropped to a centered square and scaled to 256×256, `icns` to
  1024×1024, the largest macOS icon.
- Some formats are scaled down to a sensible size: `fli` to 1024×576, `h`
  (a C header) to 256×144, `html` (colored characters) to 192×108 and `txt`
  (ASCII art) to 160×90, which makes 80×45 characters.

## How it works

```
project.sh ──> gimp-console-3.0 -i --batch-interpreter=python-fu-eval
                                    │ < scripts/export<format>.py
                                    ▼
                             scripts/common.py
                                    │ load_project()
                                    ▼
      scripts/<project>/<name>.py: <name>() -> Gimp.Image
                                    │ export()
                                    ▼
             file-<format>-export procedure, run non-interactively
```

- `project.sh` checks the arguments and pipes `scripts/export<format>.py`
  (or `scripts/savexcf.py`) into GIMP's Python batch interpreter, with
  `PROJECT=<project>` and `PYTHONPATH=scripts`. GIMP starts without a user
  interface, fonts and data (`-i -d -f`), and never hands the batch over to
  a running GIMP (`-n`).
- `scripts/common.py` imports the project, calls its function and flattens
  the image unless the format keeps layers. Its `export()` looks up a file
  procedure in the PDB, sets its options and runs it.
- Each `scripts/export<format>.py` names the procedure and its options for
  one format, such as JPEG quality or WebP compression.

## Projects

A project is a folder `scripts/<theme>-<name>/` holding `<name>.py` with a
function `<name>()` that returns a `Gimp.Image`, painted with layers,
paths, gradients, selections and GEGL filters:

```
scripts/cyberpunk-butterfly00/
└── butterfly00.py   # butterfly00() returns the layered image
```

The last part of the folder name is the module and function name, so it
must be a valid Python name. A project needs nothing outside its folder.

`cyberpunk-butterfly00` is a 1920×1080 neon butterfly over a synthwave grid
and a striped sun. It is the raster version of the drawing in
[inkscape-scripts](https://github.com/aljazmc/inkscape-scripts), with the
same coordinates: paths are stroked onto their own layers, and the glow is
a blurred copy of each layer, blended underneath. The image above was
exported with `./project.sh cyberpunk-butterfly00 png`.

Themes such as `cyberpunk`, `steampunk`, `nature` and historical eras are
work in progress and kept out of the repository by `.gitignore` until they
are ready.

## Tests

```sh
for test in tests/sh/test_*.sh; do bash "$test"; done   # project.sh
python3 -m unittest discover tests/py                   # the scripts and the images
```

The tests are split by language: `tests/sh/` tests `project.sh` with bash,
`tests/py/` tests the Python scripts and the images they paint. None of them
writes outputs into the repository.

The tests of `project.sh` run it in a temporary sandbox, with a few fake
projects and export scripts and a stand-in for `gimp-console-3.0` (see
`tests/sh/lib.sh`), so they paint nothing and never touch `build/` or
`xcf/`:

- `tests/sh/test_project.sh` checks that `project.sh` rejects bad arguments
  with its usage and exit code 1.
- `tests/sh/test_formats.sh` checks that the formats of `project.sh`, the
  exporters in `scripts/` and this README agree: every format has an
  exporter that writes its own file, every exporter is listed, the Formats
  table names every format, the count of formats is right, and only `xcf`,
  `psd` and `ora` keep the layers.
- `tests/sh/test_outputs.sh` checks the names of the outputs, as described
  under Usage, through the `clean` commands.
- `tests/sh/test_run.sh` checks that `project.sh` runs the console GIMP
  with the batch options, the export script on stdin, the project in
  `PROJECT` and `scripts/` on the `PYTHONPATH`, for one project and for
  `all`, from any directory; that it skips existing outputs, reports a
  failed export with exit code 1 and stops when GIMP is missing.

The Python tests run on plain Python. `tests/py/test_common.py` needs GIMP's
Python bindings; the others run their probes inside `gimp-console-3.0`, as
`project.sh` runs an export script, check the results with Pillow, and are
skipped without them (see `tests/py/gimp.py`):

- `tests/py/test_common.py` checks that `square()` crops the center of an
  image and scales it, with a stand-in for `Gimp.Image`.
- `tests/py/test_image.py` inspects the image before it is flattened: RGB at
  8 bits a channel, and layers with names of their own (not GIMP's
  defaults), visible, not see-through, on the canvas and not empty.
- `tests/py/test_render.py` flattens the image at a quarter of its size and
  checks the pixels: the canvas covered, neither black nor washed out, with
  contrast; that hiding any layer visibly changes the picture; that a
  second run paints the same picture, apart from the one level of random
  dithering GIMP adds to gradients; and that the picture in `gallery/`
  still matches the project.
- `tests/py/test_exports.py` runs every export script in one GIMP session on
  a temporary copy of `scripts/` and checks each file by what is inside it:
  the format's signature and the size this README promises (the full image,
  icons cropped to a square, `fli`, `h`, `html` and `txt` scaled down), the
  layers of `psd`, `ora` and `xcf` by name, and the rows and characters of
  the `html` and `txt` pictures. Every format needs a check of its own, so a
  new format can't go untested. It takes about a minute and a half a
  project.

Lint the code with [ShellCheck](https://www.shellcheck.net/) and
[Ruff](https://docs.astral.sh/ruff/):

```sh
shellcheck project.sh tests/sh/*.sh
ruff check .
```

GitHub Actions runs both on every push and pull request, see
[.github/workflows/lint.yml](.github/workflows/lint.yml).

## License

The scripts are licensed under the [MIT License](LICENSE). The files in
`gallery/` were made with them and are under the same license.

The scripts drive software that is not part of this repository and has
licenses of its own:

- [GIMP](https://www.gimp.org/about/COPYING) is free software under the GNU
  General Public License, version 3 or later. The `libgimp` library that
  plug-ins and these scripts call is licensed under the GNU Lesser General
  Public License, version 3 or later, so scripts that use it may have any
  license. Whatever you make with GIMP is yours, and the GPL does not apply
  to it.
- [GEGL](https://gegl.org/), GIMP's image processing engine, is licensed
  under the GNU LGPL, version 3 or later.
