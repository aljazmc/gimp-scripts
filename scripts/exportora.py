from common import export, load_project

image, output = load_project("build", flatten=False)

export("file-openraster-export", image, output + ".ora")
