from common import export, load_project

image, output = load_project("build")

export("file-xbm-export", image, output + ".xbm",
       prefix="butterfly")
