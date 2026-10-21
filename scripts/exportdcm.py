from common import export, load_project

image, output = load_project("build")

export("file-dicom-export", image, output + ".dcm")
