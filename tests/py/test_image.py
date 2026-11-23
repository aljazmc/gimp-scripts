"""Every project paints a sound GIMP image, inspected inside GIMP before it is
flattened: RGB at 8 bits a channel, layers with names of their own that are
visible, not see-through, on the canvas and not empty. Run: python3 -m unittest discover tests/py

Needs gimp-console-3.0 on the PATH; skipped without it.
"""
import unittest

import gimp

PROBE = '''
image = build(flatten=False)


def walk(items):
    for item in items:
        yield item
        if item.is_group():
            yield from walk(item.get_children())


layers = []
for layer in walk(image.get_layers()):
    _, x, y = layer.get_offsets()
    alpha = None
    if not layer.is_group() and layer.has_alpha():
        histogram = layer.histogram(Gimp.HistogramChannel.ALPHA, 0.0, 1.0)
        alpha = histogram[1]  # mean alpha, 0..255
    value = None
    if not layer.is_group():
        histogram = layer.histogram(Gimp.HistogramChannel.VALUE, 0.0, 1.0)
        value = histogram[2]  # standard deviation of the value
    layers.append({
        "name": layer.get_name(),
        "group": layer.is_group(),
        "visible": layer.get_visible(),
        "opacity": layer.get_opacity(),
        "bounds": [x, y, layer.get_width(), layer.get_height()],
        "alpha": alpha,
        "value_std": value,
    })

emit({
    "size": [image.get_width(), image.get_height()],
    "base": image.get_base_type().value_nick,
    "precision": image.get_precision().value_nick,
    "layers": layers,
})
'''


@unittest.skipIf(gimp.skip_reason(), gimp.skip_reason())
class ImageTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.images = {project: gimp.probe(project, PROBE) for project in gimp.projects()}

    def each(self):
        for project, image in self.images.items():
            yield project, image

    def test_rgb_at_8_bits(self):
        # what the 8-bit formats (png, jpg, gif, ico...) expect, without dithering
        for project, image in self.each():
            with self.subTest(project=project):
                self.assertEqual(image["base"], "rgb")
                self.assertIn(image["precision"], ("u8-non-linear", "u8-perceptual", "u8-gamma"),
                              "8 bits a channel")

    def test_size(self):
        for project, image in self.each():
            with self.subTest(project=project):
                width, height = image["size"]
                self.assertGreater(width, 0)
                self.assertGreater(height, 0)

    def test_layers_have_names_of_their_own(self):
        # psd, ora and xcf keep the layers by name
        for project, image in self.each():
            with self.subTest(project=project):
                names = [layer["name"] for layer in image["layers"]]
                self.assertTrue(names, "no layers")
                self.assertEqual(len(names), len(set(names)), f"layer names repeat: {names}")
                generic = [n for n in names if n.lower().startswith(("layer", "new layer", "background"))]
                self.assertEqual(generic, [], "layers left with GIMP's default names")

    def test_layers_are_visible(self):
        # a hidden or fully see-through layer is dropped by the flattened exports
        for project, image in self.each():
            with self.subTest(project=project):
                for layer in image["layers"]:
                    self.assertTrue(layer["visible"], f"{layer['name']} is hidden")
                    self.assertGreater(layer["opacity"], 0, f"{layer['name']} has opacity 0")

    def test_layers_lie_on_the_canvas(self):
        for project, image in self.each():
            with self.subTest(project=project):
                width, height = image["size"]
                for layer in image["layers"]:
                    x, y, w, h = layer["bounds"]
                    self.assertTrue(x < width and y < height and x + w > 0 and y + h > 0,
                                    f"{layer['name']} lies outside the canvas at {layer['bounds']}")

    def test_layers_are_not_empty(self):
        for project, image in self.each():
            with self.subTest(project=project):
                for layer in image["layers"]:
                    if layer["group"]:
                        continue
                    if layer["alpha"] is not None:
                        self.assertGreater(layer["alpha"], 0.0001,
                                           f"{layer['name']} is fully transparent")
                    else:
                        # an opaque layer of one flat color is a leftover fill
                        self.assertGreater(layer["value_std"], 0,
                                           f"{layer['name']} is one flat color")


if __name__ == "__main__":
    unittest.main()
