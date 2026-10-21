from common import export, load_project

image, output = load_project("build")

export("file-jpegxl-export", image, output + ".jxl",
       lossless=False,
       compression=1.0,
       save_bit_depth=8)
