from common import export, load_project

image, output = load_project("build")

export("file-eps-export", image, output + ".eps",
       width=19.2,
       height=10.8,
       x_offset=0.0,
       y_offset=0.0,
       level=True)
