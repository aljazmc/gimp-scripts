from common import export, load_project

image, output = load_project("build")

export("file-ppm-export", image, output + ".ppm",
       raw="raw-output")
