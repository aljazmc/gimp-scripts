from common import export, load_project

image, output = load_project("build")

image.scale(256, 144)

export("file-header-export", image, output + ".h")
