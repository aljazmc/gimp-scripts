from common import export, load_project

image, output = load_project("build")

image.convert_grayscale()

export("file-fits-export", image, output + ".fits")
