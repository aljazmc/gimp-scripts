from common import export, load_project

image, output = load_project("build")

export("file-pcx-export", image, output + ".pcx")
