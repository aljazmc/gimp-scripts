from common import export, load_project

image, output = load_project("build")

export("file-exr-export", image, output + ".exr")
