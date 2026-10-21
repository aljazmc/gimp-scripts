from common import export, load_project

image, output = load_project("build", flatten=False)

export("file-psd-export", image, output + ".psd")
