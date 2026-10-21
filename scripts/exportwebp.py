from common import export, load_project

image, output = load_project("build")

export("file-webp-export", image, output + ".webp",
       lossless=False,
       quality=90.0)
