from common import export, load_project

image, output = load_project("build")

export("file-tga-export", image, output + ".tga",
       rle=True,
       origin="top-left")
