import os
import logging
import pygame as pg

root_dir = os.path.dirname(__file__)
data_dir = os.path.join(root_dir, "res")

def load_image(name, colorkey=None, scale=1):
    full_name = os.path.join(data_dir, name)
    image = pg.image.load(full_name)
    size = image.get_size()
    size = (int(size[0] * scale), int(size[1] * scale))
    image = pg.transform.scale(image, size)
    image = image.convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((2, 2))
        image.set_colorkey(colorkey, pg.RLEACCEL)
    return image


def load_sound(name):
    if not pg.mixer:
        return None
    file = os.path.join(data_dir, name)
    try:
        sound = pg.mixer.Sound(file)
        return sound
    except pg.error:
        logging.warning(f"Warning, unable to load, {file}")
    return None
