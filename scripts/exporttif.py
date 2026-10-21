from common import export, load_project

image, output = load_project("build")

export("file-tiff-export", image, output + ".tif",
       compression="lzw")
