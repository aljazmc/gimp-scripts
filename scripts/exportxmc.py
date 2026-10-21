from common import export, load_project, square

image, output = load_project("build")

square(image, 256)

export("file-xmc-export", image, output + ".xmc",
       size="size-256px")
