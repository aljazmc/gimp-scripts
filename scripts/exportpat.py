from common import export, load_project, square

image, output = load_project("build")

square(image, 256)

export("file-pat-export", image, output + ".pat",
       description="Cyberpunk Butterfly")
