from common import export, load_project, square

image, output = load_project("build")

square(image, 256)

export("file-gbr-export", image, output + ".gbr",
       spacing=25,
       description="Cyberpunk Butterfly")
