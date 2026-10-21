from common import export, load_project

image, output = load_project("build")

image.scale(1024, 576)

export("file-fli-export", image, output + ".fli")
