from common import export, load_project

image, output = load_project("build")

export("file-raw-export", image, output + ".data",
       planar_configuration="contiguous")
