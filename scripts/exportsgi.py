from common import export, load_project

image, output = load_project("build")

export("file-sgi-export", image, output + ".sgi",
       compression="rle")
