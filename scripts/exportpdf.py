from common import export, load_project

image, output = load_project("build")

export("file-pdf-export", image, output + ".pdf",
       vectorize=True,
       layers_as_pages=False)
