import gi

gi.require_version("Gimp", "3.0")
gi.require_version("Gegl", "0.4")

from gi.repository import Gegl, Gimp

WIDTH = 1920
HEIGHT = 1080
HORIZON = 680
CENTER_X = WIDTH // 2
CENTER_Y = 430


def new_image(width, height):
    image = Gimp.Image.new(width, height, Gimp.ImageBaseType.RGB)
    Gimp.context_set_antialias(True)
    Gimp.context_set_feather(False)
    Gimp.context_set_stroke_method(Gimp.StrokeMethod.LINE)
    return image


def add_layer(image, name, mode=Gimp.LayerMode.NORMAL, opacity=100.0):
    layer = Gimp.Layer.new(image, name, image.get_width(), image.get_height(),
                           Gimp.ImageType.RGBA_IMAGE, opacity, mode)
    image.insert_layer(layer, None, 0)
    return layer


def set_colors(foreground, background):
    Gimp.context_set_foreground(Gegl.Color.new(foreground))
    Gimp.context_set_background(Gegl.Color.new(background))


def gradient_fill(layer, foreground, background, start, end,
                  gradient_type=Gimp.GradientType.LINEAR):
    set_colors(foreground, background)
    Gimp.context_set_gradient_fg_bg_rgb()
    layer.edit_gradient_fill(gradient_type, 0.0, False, 1, 0.0, True,
                             start[0], start[1], end[0], end[1])


def add_path(image, name, strokes, closed=True):
    """Each stroke is a start point followed by cubic segments given as
    (control1, control2, end) point triples."""
    path = Gimp.Path.new(image, name)
    image.insert_path(path, None, 0)
    for start, *segments in strokes:
        stroke = path.bezier_stroke_new_moveto(*start)
        for control1, control2, end in segments:
            path.bezier_stroke_cubicto(stroke, *control1, *control2, *end)
        if closed:
            path.stroke_close(stroke)
    return path


def stroke_path(layer, path, color, width):
    Gimp.context_set_foreground(Gegl.Color.new(color))
    Gimp.context_set_line_width(width)
    layer.edit_stroke_item(path)


def mirror(points):
    return [(2 * CENTER_X - x, y) for x, y in points]


def blur(layer, radius):
    blur_filter = Gimp.DrawableFilter.new(layer, "gegl:gaussian-blur", "")
    config = blur_filter.get_config()
    config.set_property("std-dev-x", radius)
    config.set_property("std-dev-y", radius)
    layer.merge_filter(blur_filter)


def add_glow(image, layer, radius, opacity=100.0):
    glow = layer.copy()
    image.insert_layer(glow, None, image.get_item_position(layer) + 1)
    glow.set_name(layer.get_name() + " glow")
    glow.set_mode(Gimp.LayerMode.ADDITION)
    glow.set_opacity(opacity)
    blur(glow, radius)
    return glow


def add_sky(image):
    sky = add_layer(image, "Sky")
    gradient_fill(sky, "#05010f", "#3b0a5c", (0, 0), (0, HORIZON))
    image.select_rectangle(Gimp.ChannelOps.REPLACE, 0, HORIZON,
                           WIDTH, HEIGHT - HORIZON)
    gradient_fill(sky, "#12002a", "#020008", (0, HORIZON), (0, HEIGHT))
    Gimp.Selection.none(image)
    return sky


def add_sun(image):
    sun = add_layer(image, "Sun")
    radius = 300
    image.select_ellipse(Gimp.ChannelOps.REPLACE, CENTER_X - radius,
                         HORIZON - radius - 60, 2 * radius, 2 * radius)
    image.select_rectangle(Gimp.ChannelOps.INTERSECT, 0, 0, WIDTH, HORIZON)
    for i in range(7):
        gap = 4 + 3 * i
        top = HORIZON - 40 - i * 34
        image.select_rectangle(Gimp.ChannelOps.SUBTRACT, 0, top, WIDTH, gap)
    gradient_fill(sun, "#ffd319", "#ff2975", (0, HORIZON - 2 * radius),
                  (0, HORIZON))
    Gimp.Selection.none(image)
    add_glow(image, sun, 40.0, 70.0)
    return sun


def add_grid(image):
    grid = add_layer(image, "Grid")
    image.select_rectangle(Gimp.ChannelOps.REPLACE, 0, HORIZON,
                           WIDTH, HEIGHT - HORIZON)
    lines = []
    for i in range(-14, 15):
        lines.append(((CENTER_X + i * 40, HORIZON),
                      ((CENTER_X + i * 40, HORIZON),
                       (CENTER_X + i * 260, HEIGHT),
                       (CENTER_X + i * 260, HEIGHT))))
    depth = 6.0
    while depth < HEIGHT - HORIZON:
        y = HORIZON + depth
        lines.append(((0, y), ((0, y), (WIDTH, y), (WIDTH, y))))
        depth *= 1.45
    path = add_path(image, "Grid", lines, closed=False)
    stroke_path(grid, path, "#ff00ff", 2.0)
    Gimp.Selection.none(image)
    add_glow(image, grid, 6.0)
    return grid


def wing_outlines():
    upper = [(CENTER_X - 12, CENTER_Y - 20),
             ((CENTER_X - 120, CENTER_Y - 260), (CENTER_X - 420, CENTER_Y - 330),
              (CENTER_X - 470, CENTER_Y - 230)),
             ((CENTER_X - 520, CENTER_Y - 120), (CENTER_X - 330, CENTER_Y + 20),
              (CENTER_X - 12, CENTER_Y + 10))]
    lower = [(CENTER_X - 12, CENTER_Y + 20),
             ((CENTER_X - 260, CENTER_Y + 30), (CENTER_X - 400, CENTER_Y + 170),
              (CENTER_X - 330, CENTER_Y + 260)),
             ((CENTER_X - 260, CENTER_Y + 340), (CENTER_X - 90, CENTER_Y + 230),
              (CENTER_X - 12, CENTER_Y + 60))]
    return [upper, lower]


def mirror_stroke(stroke):
    start, *segments = stroke
    return [mirror([start])[0]] + [tuple(mirror(segment)) for segment in segments]


def add_wings(image):
    wings = add_layer(image, "Wings")
    left = wing_outlines()
    strokes = left + [mirror_stroke(stroke) for stroke in left]
    path = add_path(image, "Wings", strokes)

    image.select_item(Gimp.ChannelOps.REPLACE, path)
    gradient_fill(wings, "#00f0ff", "#7a00ff", (CENTER_X, CENTER_Y),
                  (CENTER_X + 480, CENTER_Y), Gimp.GradientType.RADIAL)
    for x, y, size in ((-330, -190, 90), (-200, -90, 60), (-250, 170, 70)):
        for sx in (CENTER_X + x - size // 2, CENTER_X - x - size // 2):
            image.select_ellipse(Gimp.ChannelOps.REPLACE, sx,
                                 CENTER_Y + y - size // 2, size, size)
            image.select_item(Gimp.ChannelOps.INTERSECT, path)
            gradient_fill(wings, "#ff2975", "#ffd319",
                          (sx + size // 2, CENTER_Y + y),
                          (sx + size, CENTER_Y + y), Gimp.GradientType.RADIAL)
    Gimp.Selection.none(image)

    stroke_path(wings, path, "#e0ffff", 5.0)
    veins = []
    for start, (_, _, tip), _ in left:
        veins.append((start, (start, tip, tip)))
    veins = veins + [mirror_stroke(vein) for vein in veins]
    stroke_path(wings, add_path(image, "Veins", veins, closed=False),
                "#e0ffff", 2.0)

    wings.set_opacity(92.0)
    add_glow(image, wings, 25.0)
    return wings


def add_body(image):
    body = add_layer(image, "Body")
    image.select_ellipse(Gimp.ChannelOps.REPLACE, CENTER_X - 16,
                         CENTER_Y - 90, 32, 260)
    gradient_fill(body, "#ffffff", "#ff2975", (CENTER_X, CENTER_Y - 90),
                  (CENTER_X, CENTER_Y + 170))
    image.select_ellipse(Gimp.ChannelOps.REPLACE, CENTER_X - 24,
                         CENTER_Y - 130, 48, 48)
    gradient_fill(body, "#ffffff", "#ff2975", (CENTER_X, CENTER_Y - 110),
                  (CENTER_X, CENTER_Y - 82), Gimp.GradientType.RADIAL)
    Gimp.Selection.none(image)

    antenna = [(CENTER_X - 8, CENTER_Y - 125),
               ((CENTER_X - 30, CENTER_Y - 200), (CENTER_X - 90, CENTER_Y - 250),
                (CENTER_X - 130, CENTER_Y - 250))]
    antennae = add_path(image, "Antennae",
                        [antenna, mirror_stroke(antenna)], closed=False)
    stroke_path(body, antennae, "#ff2975", 4.0)
    add_glow(image, body, 12.0)
    return body


def butterfly00():
    image = new_image(WIDTH, HEIGHT)
    add_sky(image)
    add_sun(image)
    add_grid(image)
    add_wings(image)
    add_body(image)
    return image
