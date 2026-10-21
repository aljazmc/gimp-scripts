from common import export, load_project, square

image, output = load_project("build")

square(image, 256)

export("file-gih-export", image, output + ".gih",
       spacing=25,
       description="Cyberpunk Butterfly",
       cell_width=256,
       cell_height=256,
       num_cells=1)
