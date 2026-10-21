from common import export, load_project

image, output = load_project("build")

image.scale(192, 108)

export("file-colorxhtml-export", image, output + ".html",
       characters="butterfly",
       font_size=6)
