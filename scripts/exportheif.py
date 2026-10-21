from common import export, load_project

image, output = load_project("build")

export("file-heif-export", image, output + ".heif",
       quality=90,
       save_bit_depth=8)
