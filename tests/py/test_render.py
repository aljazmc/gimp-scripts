"""Every project paints a picture worth looking at, flattened by GIMP at a
quarter of its size: the canvas covered, neither black nor washed out, with
contrast, every layer adding something you can see, the same picture on every
run (apart from the dithering of gradients), and the gallery picture of the project up to date.
Run: python3 -m unittest discover tests/py

Needs gimp-console-3.0 on the PATH and Pillow; skipped without them.
"""
import shutil
import tempfile
import unittest
from pathlib import Path

import gimp

SCALE = 4  # render at a quarter of the size
# share of fully transparent pixels: above, the canvas has holes
TRANSPARENT_MAX = 0.01
# mean luminance (0..255): below is black, above is washed out
DARK, BRIGHT = 5, 230
# standard deviation of luminance: below is a flat, featureless picture
CONTRAST_MIN = 10
# share of pixels that visibly change (by more than 16 of 255) when a layer is
# hidden: below, it adds nothing
LAYER_MIN = 0.001
# mean difference from the picture in gallery/: above, the gallery is stale
GALLERY_MAX = 2.0
# largest difference between two runs: gradients are dithered with random
# noise of one level against banding, anything more is a real change
RERUN_MAX = 2

PROBE = f'''
image = build(flatten=False)
width, height = image.get_width() // {SCALE}, image.get_height() // {SCALE}
result = {{"size": [image.get_width(), image.get_height()],
          "full": png(image, "full", width, height), "layers": {{}}}}
for layer in image.get_layers():
    layer.set_visible(False)
    result["layers"][layer.get_name()] = png(image, "without-" + str(len(result["layers"])),
                                             width, height)
    layer.set_visible(True)
emit(result)
'''


def load(path):
    from PIL import Image
    with Image.open(path) as image:
        return image.convert("RGBA")


def luminance(image):
    from PIL import ImageStat
    return ImageStat.Stat(image.convert("L"))


def difference(a, b):
    from PIL import ImageChops
    return ImageChops.difference(a.convert("RGB"), b.convert("RGB")).convert("L")


def changed(a, b):
    d = difference(a, b)
    return sum(d.histogram()[17:]) / (d.width * d.height)


@unittest.skipIf(gimp.skip_reason() or not gimp.pillow(),
                 gimp.skip_reason() or "needs Pillow")
class RenderTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.renders = {}
        for project in gimp.projects():
            folder = Path(cls.tmp, project)
            folder.mkdir()
            result = gimp.probe(project, PROBE, tmp=folder)
            result["image"] = load(result["full"])
            cls.renders[project] = result

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def each(self):
        for project, render in self.renders.items():
            yield project, render

    def test_covers_the_canvas(self):
        for project, render in self.each():
            with self.subTest(project=project):
                image = render["image"]
                transparent = image.getchannel("A").histogram()[0] / (image.width * image.height)
                self.assertLessEqual(transparent, TRANSPARENT_MAX,
                                     f"{transparent:.1%} of the canvas is transparent")

    def test_is_exposed_and_has_contrast(self):
        for project, render in self.each():
            with self.subTest(project=project):
                stat = luminance(render["image"])
                self.assertGreater(stat.mean[0], DARK, "the picture is black")
                self.assertLess(stat.mean[0], BRIGHT, "the picture is washed out")
                self.assertGreater(stat.stddev[0], CONTRAST_MIN, "the picture is flat")

    def test_every_layer_shows(self):
        # a layer that changes nothing is covered, see-through or empty
        for project, render in self.each():
            with self.subTest(project=project):
                for name, path in render["layers"].items():
                    share = changed(render["image"], load(path))
                    self.assertGreater(share, LAYER_MIN,
                                       f"hiding the layer {name} changes {share:.2%} of the picture")

    def test_paints_the_same_picture_every_time(self):
        for project, render in self.each():
            with self.subTest(project=project):
                with tempfile.TemporaryDirectory() as tmp:
                    again = load(gimp.probe(project, PROBE.split("for layer")[0] + "emit(result)\n",
                                            tmp=tmp)["full"])
                    histogram = difference(render["image"], again).histogram()
                    largest = max(level for level, count in enumerate(histogram) if count)
                    self.assertLessEqual(largest, RERUN_MAX,
                                         f"a second run painted another picture (off by {largest})")

    def test_the_gallery_is_up_to_date(self):
        for project, render in self.each():
            with self.subTest(project=project):
                for path in sorted((gimp.ROOT / "gallery").glob(f"{project}.*")):
                    shown = load(path).resize(render["image"].size)
                    mean = luminance(difference(render["image"], shown)).mean[0]
                    self.assertLess(mean, GALLERY_MAX, f"{path.name} no longer matches the painting")


if __name__ == "__main__":
    unittest.main()
