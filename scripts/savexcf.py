from common import export, load_project

image, output = load_project("xcf", flatten=False)

export("gimp-xcf-save", image, output + ".xcf")
