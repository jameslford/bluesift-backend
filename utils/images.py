from PIL import Image

colors = {'red': (255,0,0),
          'green': (0,255,0),
          'blue': (0,0,255),
          'yellow': (255,255,0),
          'orange': (255,127,0),
          'white': (255,255,255),
          'black': (0,0,0),
          'gray': (127,127,127),
          'pink': (255,127,127),
          'purple': (127,0,255),}


def resize_image(image: Image.Image, desired_size) -> Image.Image:
    width, height = image.size
    if width == desired_size and height <= desired_size:
        return image
    w_ratio = desired_size/width
    height_adjust = int(round(height * w_ratio))
    image = image.resize((desired_size, height_adjust), Image.LANCZOS)
    if image.size[1] > desired_size:
        image = image.crop((
            0,
            0,
            desired_size,
            desired_size
            ))
    return image

def remove_background():
    im: Image.Image = Image.open('test/centered.jpg')
    print(im.height)
    im.show()
