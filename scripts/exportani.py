from common import export, load_project, square

image, output = load_project("build")

square(image, 256)

export("file-ani-export", image, output + ".ani",
       cursor_name="butterfly",
       author_name="gimp-scripts",
       default_delay=8)
