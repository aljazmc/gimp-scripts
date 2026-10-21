from common import export, load_project

image, output = load_project("build")

export("file-pix-export", image, output + ".pix")
