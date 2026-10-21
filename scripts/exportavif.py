from common import export, load_project

image, output = load_project("build")

export("file-heif-av1-export", image, output + ".avif",
       quality=90,
       save_bit_depth=8,
       include_exif=False)
