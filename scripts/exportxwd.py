from common import export, load_project

image, output = load_project("build")

export("file-xwd-export", image, output + ".xwd")
