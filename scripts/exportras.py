from common import export, load_project

image, output = load_project("build")

export("file-sunras-export", image, output + ".ras",
       rle="rle")
