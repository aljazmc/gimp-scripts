from common import export, load_project

image, output = load_project("build")

export("file-pnm-export", image, output + ".pnm",
       raw="raw-output")
