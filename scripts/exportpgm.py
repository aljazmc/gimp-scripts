from common import export, load_project

image, output = load_project("build")

export("file-pgm-export", image, output + ".pgm",
       raw="raw-output")
