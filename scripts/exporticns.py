from common import export, load_project, square

image, output = load_project("build")

square(image, 1024)

export("file-icns-export", image, output + ".icns")
