from common import export, load_project

image, output = load_project("build")

export("file-cel-export", image, output + ".cel")
