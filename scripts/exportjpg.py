from common import export, load_project

image, output = load_project("build")

export("file-jpeg-export", image, output + ".jpg",
       quality=0.9,
       optimize=True,
       progressive=True)
