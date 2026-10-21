from common import export, load_project

image, output = load_project("build")

export("file-dds-export", image, output + ".dds",
       compression_format="bc3",
       mipmaps="generate")
