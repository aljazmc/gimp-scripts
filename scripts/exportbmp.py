from common import export, load_project

image, output = load_project("build")

export("file-bmp-export", image, output + ".bmp",
       use_rle=False,
       rgb_format="rgb-888")
