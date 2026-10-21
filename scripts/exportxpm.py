from common import export, load_project

image, output = load_project("build")

export("file-xpm-export", image, output + ".xpm",
       threshold=127)
