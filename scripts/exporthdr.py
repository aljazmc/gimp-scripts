from common import export, load_project

image, output = load_project("build")

export("file-rgbe-export", image, output + ".hdr")
