"""Tests for scripts/common.py. It imports GIMP's introspection bindings
(gi with Gimp 3.0), which work without a running GIMP; the test uses a
stand-in image. Run: python3 -m unittest discover tests"""
import importlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
common = importlib.import_module("common")


class FakeImage:
    """Records crop() and scale() like a Gimp.Image."""

    def __init__(self, width, height):
        self.width, self.height = width, height
        self.calls = []

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def crop(self, width, height, x, y):
        self.calls.append(("crop", width, height, x, y))
        self.width, self.height = width, height

    def scale(self, width, height):
        self.calls.append(("scale", width, height))
        self.width, self.height = width, height


class SquareTest(unittest.TestCase):

    def test_crops_the_center_and_scales(self):
        cases = {
            "landscape": ((1920, 1080), ("crop", 1080, 1080, 420, 0)),
            "portrait": ((600, 1000), ("crop", 600, 600, 0, 200)),
        }
        for case, (size, crop) in cases.items():
            with self.subTest(case):
                image = FakeImage(*size)
                common.square(image, 256)
                self.assertEqual(image.calls, [crop, ("scale", 256, 256)])


if __name__ == "__main__":
    unittest.main()
