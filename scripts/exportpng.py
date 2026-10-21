from common import export, load_project

image, output = load_project("build")

export("file-png-export", image, output + ".png",
       compression=9,
       format="rgba8")
