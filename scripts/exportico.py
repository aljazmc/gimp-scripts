from common import export, load_project, square

image, output = load_project("build")

square(image, 256)

export("file-ico-export", image, output + ".ico")
