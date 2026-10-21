from common import export, load_project

image, output = load_project("build")

export("file-pbm-export", image, output + ".pbm",
       raw="raw-output")
