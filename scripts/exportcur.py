from common import export, load_project, square

image, output = load_project("build")

square(image, 256)

export("file-cur-export", image, output + ".cur",
       hot_spot_x=[128],
       hot_spot_y=[128])
