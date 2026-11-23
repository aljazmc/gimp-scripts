"""Every export script writes a valid file of its format, checked by what is
inside it: the format's signature and the size the README promises (the full
image, icons cropped to a square, the small formats scaled down), the layers
in the layered formats, and the characters of the text formats.
Run: python3 -m unittest discover tests/py

All the export scripts run in one GIMP session on a temporary copy of
scripts/, as project.sh runs them, so nothing is written into the
repository. They take about a minute a project. Needs gimp-console-3.0 on the
PATH and Pillow; skipped without them.
"""
import re
import shutil
import struct
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import gimp

# sizes other than the full image, from the README and the export scripts
ICON = (256, 256)
SIZES = {"ani": ICON, "cur": ICON, "gbr": ICON, "gih": ICON, "ico": ICON, "pat": ICON,
         "xmc": ICON, "icns": (1024, 1024), "fli": (1024, 576), "h": (256, 144),
         "html": (192, 108), "txt": (80, 45)}
LAYERED = ("psd", "ora", "xcf")

# runs every export script with fresh globals, as if it were alone
PROBE = '''
import glob, traceback
names = sorted(glob.glob(os.path.join(os.environ["PROBE_SCRIPTS"], "export*.py")))
names.append(os.path.join(os.environ["PROBE_SCRIPTS"], "savexcf.py"))
layers = [layer.get_name() for layer in build(flatten=False).get_layers()]
errors = {}
for name in names:
    format = os.path.basename(name)[len("export"):-3] if "export" in name else "xcf"
    try:
        with open(name) as f:
            exec(compile(f.read(), name, "exec"), {"__name__": "__main__"})
    except BaseException as error:
        errors[format] = "".join(traceback.format_exception(error))[-1500:]
emit({"errors": errors, "layers": layers})
'''


def formats():
    """The FORMATS of project.sh, and xcf."""
    text = (gimp.ROOT / "project.sh").read_text()
    listed = re.search(r"^FORMATS=\((.*?)^\)", text, re.MULTILINE | re.DOTALL).group(1)
    return listed.split() + ["xcf"]


class Checks:
    """One method per format: check_<format>(path, size, layers) raises on a
    bad file. size is what the file must measure, layers the image's layers."""

    def __init__(self, test):
        self.t = test

    # --- what Pillow reads -------------------------------------------------

    def pillow(self, path, size, kind, mode=None):
        """Open the file with Pillow, check it and return its layer names."""
        from PIL import Image
        with Image.open(path) as image:
            self.t.assertEqual(image.format, kind)
            self.t.assertEqual(image.size, size)
            if mode:
                self.t.assertEqual(image.mode, mode)
            image.load()  # the pixels decode too
            return [layer[0] for layer in image.layers] if kind == "PSD" else []

    def check_png(self, path, size, layers):
        self.pillow(path, size, "PNG")

    def check_jpg(self, path, size, layers):
        self.pillow(path, size, "JPEG")

    def check_webp(self, path, size, layers):
        self.pillow(path, size, "WEBP")

    def check_gif(self, path, size, layers):
        self.pillow(path, size, "GIF")

    def check_bmp(self, path, size, layers):
        self.pillow(path, size, "BMP")

    def check_tif(self, path, size, layers):
        self.pillow(path, size, "TIFF")

    def check_tga(self, path, size, layers):
        self.pillow(path, size, "TGA")

    def check_pcx(self, path, size, layers):
        self.pillow(path, size, "PCX")

    def check_ras(self, path, size, layers):
        self.pillow(path, size, "SUN")

    def check_sgi(self, path, size, layers):
        self.pillow(path, size, "SGI")

    def check_qoi(self, path, size, layers):
        self.pillow(path, size, "QOI")

    def check_dds(self, path, size, layers):
        self.pillow(path, size, "DDS")

    def check_fits(self, path, size, layers):
        self.pillow(path, size, "FITS", "L")  # the export makes it grayscale

    def check_pbm(self, path, size, layers):
        self.pillow(path, size, "PPM", "1")

    def check_pgm(self, path, size, layers):
        self.pillow(path, size, "PPM", "L")

    def check_ppm(self, path, size, layers):
        self.pillow(path, size, "PPM", "RGB")

    def check_pnm(self, path, size, layers):
        self.pillow(path, size, "PPM")

    def check_xbm(self, path, size, layers):
        self.pillow(path, size, "XBM", "1")

    def check_fli(self, path, size, layers):
        self.pillow(path, size, "FLI")

    def check_gbr(self, path, size, layers):
        self.pillow(path, size, "GBR")

    def check_ico(self, path, size, layers):
        self.pillow(path, size, "ICO")

    def check_icns(self, path, size, layers):
        self.pillow(path, size, "ICNS")

    def postscript(self, path, size, header):
        data = path.read_bytes()
        self.t.assertTrue(data.startswith(header), f"starts with {header!r}")
        box = re.search(rb"%%BoundingBox: (\d+) (\d+) (\d+) (\d+)", data[:4000])
        self.t.assertIsNotNone(box, "a bounding box")
        x0, y0, x1, y1 = map(int, box.groups())
        # the page keeps the image's proportions
        self.t.assertAlmostEqual((x1 - x0) / (y1 - y0), size[0] / size[1], delta=0.01)

    def check_eps(self, path, size, layers):
        self.postscript(path, size, b"%!PS-Adobe-3.0 EPSF")

    def check_ps(self, path, size, layers):
        self.postscript(path, size, b"%!PS-Adobe-3.0")

    def check_pdf(self, path, size, layers):
        data = path.read_bytes()
        self.t.assertTrue(data.startswith(b"%PDF-"))
        self.t.assertTrue(data.rstrip().endswith(b"%%EOF"), "a complete PDF")

    # --- layered -----------------------------------------------------------

    def check_psd(self, path, size, layers):
        self.t.assertEqual(self.pillow(path, size, "PSD"), list(reversed(layers)),
                           "the layers, bottom first")

    def check_ora(self, path, size, layers):
        with zipfile.ZipFile(path) as archive:
            self.t.assertEqual(archive.read("mimetype"), b"image/openraster")
            stack = ET.fromstring(archive.read("stack.xml"))
            self.t.assertEqual((int(stack.get("w")), int(stack.get("h"))), size)
            self.t.assertEqual([e.get("name") for e in stack.iter("layer")], layers)
            for name in ("mergedimage.png", "Thumbnails/thumbnail.png"):
                self.t.assertIn(name, archive.namelist())

    def check_xcf(self, path, size, layers):
        data = path.read_bytes()
        self.t.assertTrue(data.startswith(b"gimp xcf "))
        self.t.assertEqual(struct.unpack(">II", data[14:22]), size)
        for name in layers:
            self.t.assertIn(name.encode() + b"\0", data, f"the layer {name}")

    # --- signatures and headers --------------------------------------------

    def check_avif(self, path, size, layers):
        self.t.assertEqual(path.read_bytes()[4:12], b"ftypavif")

    def check_heif(self, path, size, layers):
        self.t.assertIn(path.read_bytes()[4:12], (b"ftypheic", b"ftypheix", b"ftypmif1"))

    def check_jxl(self, path, size, layers):
        data = path.read_bytes()
        self.t.assertTrue(data.startswith(b"\xff\x0a") or data[4:8] == b"JXL ", "a JPEG XL signature")

    def check_exr(self, path, size, layers):
        self.t.assertEqual(path.read_bytes()[:4], b"\x76\x2f\x31\x01")

    def check_hdr(self, path, size, layers):
        head = path.read_bytes()[:200]
        self.t.assertTrue(head.startswith(b"#?RADIANCE"))
        self.t.assertIn(b"\n-Y %d +X %d\n" % (size[1], size[0]), head)

    def check_pfm(self, path, size, layers):
        self.t.assertTrue(path.read_bytes().startswith(b"PF\n%d %d\n" % size))

    def check_pam(self, path, size, layers):
        head = path.read_bytes()[:300]
        self.t.assertTrue(head.startswith(b"P7\n"))
        self.t.assertIn(b"WIDTH %d\nHEIGHT %d\n" % size, head)

    def check_ff(self, path, size, layers):
        data = path.read_bytes()
        self.t.assertEqual(data[:8], b"farbfeld")
        self.t.assertEqual(struct.unpack(">II", data[8:16]), size)
        self.t.assertEqual(len(data), 16 + size[0] * size[1] * 8)

    def check_data(self, path, size, layers):
        # raw RGB bytes, nothing else
        self.t.assertEqual(path.stat().st_size, size[0] * size[1] * 3)

    def check_dcm(self, path, size, layers):
        data = path.read_bytes()
        self.t.assertEqual(data[128:132], b"DICM")

    def check_cel(self, path, size, layers):
        data = path.read_bytes()
        self.t.assertEqual(data[:4], b"KiSS")
        self.t.assertEqual(struct.unpack("<HH", data[8:12]), size)

    def check_pix(self, path, size, layers):
        self.t.assertEqual(struct.unpack(">HH", path.read_bytes()[:4]), size)

    def check_xwd(self, path, size, layers):
        header = struct.unpack(">7I", path.read_bytes()[:28])
        self.t.assertEqual(header[1], 7, "XWD version 7")
        self.t.assertEqual(header[4:6], size)

    def check_xpm(self, path, size, layers):
        text = path.read_text(errors="replace")[:500]
        self.t.assertTrue(text.startswith("/* XPM */"))
        values = re.search(r'"(\d+) (\d+) \d+ \d+"', text)
        self.t.assertEqual(tuple(map(int, values.groups())), size)

    def check_pat(self, path, size, layers):
        header, version, width, height, depth = struct.unpack(">5I", path.read_bytes()[:20])
        self.t.assertEqual(version, 1)
        self.t.assertEqual((width, height), size)

    def check_gih(self, path, size, layers):
        head = path.read_bytes()[:400].decode("latin-1")
        self.t.assertIn("cellwidth:%d cellheight:%d" % size, head)

    def check_cur(self, path, size, layers):
        reserved, kind, count, width, height = struct.unpack("<HHHBB", path.read_bytes()[:8])
        self.t.assertEqual((reserved, kind), (0, 2), "a cursor")
        self.t.assertGreaterEqual(count, 1)
        # 0 stands for 256 in the directory
        self.t.assertEqual((width or 256, height or 256), size)

    def check_ani(self, path, size, layers):
        data = path.read_bytes()
        self.t.assertEqual((data[:4], data[8:12]), (b"RIFF", b"ACON"))
        self.t.assertIn(b"anih", data[:200])
        icon = data.find(b"icon")
        self.t.assertGreater(icon, 0, "an icon frame")
        self.check_cur_bytes(data[icon + 8:], size)

    def check_cur_bytes(self, data, size):
        reserved, kind, count, width, height = struct.unpack("<HHHBB", data[:8])
        self.t.assertEqual((width or 256, height or 256), size)

    def check_xmc(self, path, size, layers):
        data = path.read_bytes()
        self.t.assertEqual(data[:4], b"Xcur")
        # the table of contents: (type, subtype, position) of each chunk
        header, version, count = struct.unpack("<III", data[4:16])
        images = []
        for index in range(count):
            kind, subtype, position = struct.unpack("<III", data[16 + 12 * index:28 + 12 * index])
            if kind == 0xFFFD0002:  # an image chunk
                width, height = struct.unpack("<II", data[position + 16:position + 24])
                images.append((width, height))
        self.t.assertIn(size, images, "an image of the size")

    def check_h(self, path, size, layers):
        text = path.read_text()
        self.t.assertIn("static unsigned int width = %d;" % size[0], text)
        self.t.assertIn("static unsigned int height = %d;" % size[1], text)
        self.t.assertIn("#define HEADER_PIXEL", text)

    def check_html(self, path, size, layers):
        text = path.read_text()
        self.t.assertTrue(text.startswith("<!DOCTYPE html>"))
        pre = text[text.index("<pre>") + 5:text.index("</pre>")]
        rows = [row for row in pre.split("\n") if row.strip()]
        self.t.assertEqual(len(rows), size[1], "a row of characters for each row of pixels")
        self.t.assertEqual(text.count("<span"), size[0] * size[1], "a character for each pixel")

    def check_txt(self, path, size, layers):
        rows = path.read_text().splitlines()
        self.t.assertEqual(len(rows), size[1], "rows of ASCII art")
        self.t.assertEqual({len(row) for row in rows}, {size[0]}, "characters a row")
        self.t.assertGreater(len(set("".join(rows))), 3, "more than a few characters: a picture")


def output(tmp, project, format):
    folder = "xcf" if format == "xcf" else "build"
    return Path(tmp, folder, f"{project}.{format}")


@unittest.skipIf(gimp.skip_reason() or not gimp.pillow(),
                 gimp.skip_reason() or "needs Pillow")
class ExportTest(unittest.TestCase):

    def test_every_format_has_a_check(self):
        missing = [f for f in formats() if not hasattr(Checks, "check_" + f)]
        self.assertEqual(missing, [], "formats without a check in test_exports.py")

    def test_exports_are_valid(self):
        checks = Checks(self)
        for project in gimp.projects():
            with tempfile.TemporaryDirectory() as tmp:
                scripts = Path(tmp, "scripts")
                shutil.copytree(gimp.SCRIPTS, scripts, ignore=shutil.ignore_patterns("__pycache__"))
                probed = Path(tmp, "probe")
                probed.mkdir()
                result = gimp.probe(project, PROBE, tmp=probed, scripts=scripts)
                full = None
                for format in formats():
                    with self.subTest(project=project, format=format):
                        self.assertNotIn(format, result["errors"], result["errors"].get(format))
                        path = output(tmp, project, format)
                        self.assertTrue(path.is_file(), f"no {path.name}")
                        self.assertGreater(path.stat().st_size, 0, f"{path.name} is empty")
                        if full is None:
                            from PIL import Image
                            with Image.open(output(tmp, project, "png")) as png:
                                full = png.size
                        getattr(checks, "check_" + format)(path, SIZES.get(format, full),
                                                           result["layers"])


if __name__ == "__main__":
    unittest.main()
