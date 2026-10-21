from common import export, load_project

image, output = load_project("build")

image.scale(160, 90)

export("file-aa-export", image, output + ".txt",
       file_type=0)
