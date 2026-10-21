from common import export, load_project

image, output = load_project("build")

export("file-gif-export", image, output + ".gif",
       interlace=False)
