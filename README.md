# gimp-scripts

Python scripts that paint raster images in GIMP 3 through its
`gi.repository.Gimp` API, and a shell script that exports them with GIMP
to PNG, JPEG, Photoshop, icons, brushes and about forty other formats.
Each image is a self-contained project in `scripts/` with AI-generated
code.

## Requirements

- GIMP 3, with `gimp-console-3.0` on the `PATH` (set `GIMP` at the top of
  `project.sh` for another name)

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

For example:

```sh
./project.sh cyberpunk-butterfly00 png
```

Outputs go to `build/<project>.<format>`, and `xcf` outputs to
`xcf/<project>.xcf`. Existing outputs are skipped, so clean them to
rebuild. The script can be run from any directory. Without arguments, it
prints the usage with every format and the first ten projects.

### Formats

`ani avif bmp cel cur data dcm dds eps exr ff fits fli gbr gif gih h hdr
heif html icns ico jpg jxl ora pam pat pbm pcx pdf pfm pgm pix png pnm
ppm ps psd qoi ras sgi tga tif txt webp xbm xmc xpm xwd xcf`

- Most formats get the full image, flattened into one layer so that
  exporters don't turn layers into pages, frames or icons.
- `xcf`, `psd` and `ora` keep the layers, to open and edit the image
  later.
- Icons, cursors, brushes and patterns (`ani cur gbr gih icns ico pat
  xmc`) are cropped to a centered square and scaled to 256×256.
- Some formats are scaled down to a sensible size: `fli` to 1024×576,
  `h` (a C header) to 256×144, `html` (colored characters) to 192×108 and
  `txt` (ASCII art) to 160×90, which makes 80×45 characters.

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
  interface, fonts and data (`-i -d -f`), and never hands the batch over
  to a running GIMP (`-n`).
- `scripts/common.py` imports the project, calls its function and
  flattens the image unless the format keeps layers. Its `export()` looks
  up a file procedure in the PDB, sets its options and runs it.
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

`cyberpunk-butterfly00` is a 1920×1080 neon butterfly over a synthwave
grid and a striped sun. It is the raster version of the drawing in
[inkscape-scripts](https://github.com/aljazmc/inkscape-scripts), with the
same coordinates: paths are stroked onto their own layers, and the glow is
a blurred copy of each layer, blended underneath.

Themes such as `cyberpunk`, `steampunk`, `nature` and historical eras are
work in progress and kept out of the repository by `.gitignore` until they
are ready.

## Tests

```sh
bash tests/test_project.sh             # project.sh
python3 -m unittest discover tests     # the Python scripts
```

The tests need only bash and Python's standard library, and none of them
runs the application or writes outputs. `tests/test_project.sh` checks
that `project.sh` rejects bad arguments with its usage and exit code 1.
`tests/test_common.py` checks that `square()` crops the center of an
image and scales it, with a stand-in for `Gimp.Image`. It needs GIMP's
Python bindings (`gi` with Gimp 3.0), but not a running GIMP.

To lint the code with [ShellCheck](https://www.shellcheck.net/) and
[Ruff](https://docs.astral.sh/ruff/):

```sh
shellcheck project.sh tests/*.sh
ruff check .
```

## Gallery

`cyberpunk-butterfly00`, exported with `./project.sh cyberpunk-butterfly00 png`:

![cyberpunk-butterfly00](gallery/cyberpunk-butterfly00.png)

## License

The scripts are licensed under the MIT license, see [LICENSE](LICENSE).
The files in `gallery/` were made with them and are under the same
license.

The scripts drive software that is not part of this repository and has
licenses of its own:

- [GIMP](https://www.gimp.org/about/COPYING) is free software under the
  GNU General Public License, version 3 or later. The `libgimp` library
  that plug-ins and these scripts call is licensed under the GNU Lesser
  General Public License, version 3 or later, so scripts that use it may
  have any license. Whatever you make with GIMP is yours, and the GPL
  does not apply to it.
- [GEGL](https://gegl.org/), GIMP's image processing engine, is licensed
  under the GNU LGPL, version 3 or later.
