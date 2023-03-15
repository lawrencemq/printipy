from typing import List

from PIL import Image, ImageFont, ImageDraw
import os
import random


def select_from(_min: int, _max: int, _vals: List[int], space: int) -> int:
    test = random.randint(_min, _max)
    max_count = 5
    for x in range(0, max_count):
        if not any([abs(x - test) <= space for x in _vals]):
            return test
        test = random.randint(_min, _max)
    return test


def transform_pic(_filename: str, font_name: str):
    img = Image.open(os.path.join(main_dir, _filename))
    img = img.resize((500, 700))
    small_filename = _filename[0:-4] + "_small.png"
    img.save(os.path.join(main_dir, small_filename))

    img = Image.open(os.path.join(main_dir, _filename))
    I1 = ImageDraw.Draw(img)
    selected_x = []
    selected_y = []
    for x in range(0, random.randint(2, 7) + 3):
        font = ImageFont.truetype(font_name, random.randint(30, 110))
        x_coord = select_from(0, 2300, selected_x, 200)
        selected_x.append(x_coord)
        y_coord = select_from(0, 3400, selected_y, 200)
        selected_y.append(y_coord)
        _r = random.randint(0, 250)
        _g = random.randint(0, 250)
        _b = random.randint(0, 250)
        I1.text((x_coord, y_coord), "PROOF - Macabre Greetings", font=font, fill=(_r, _g, _b))

    # Display edited image
    img = img.resize((1375, 1925))
    # Save the edited image
    large_filename = _filename[0:-4] + "_large_watermark.png"
    img.save(os.path.join(main_dir, large_filename))


def generate_in_situ(_filename: str, background_top: Image, background_bottom: Image):
    img = Image.open(os.path.join(main_dir, _filename))  # load card front
    # this would be the time to transform/skew this image if we're placing it on a table at an angle.
    combined = Image.new('RGBA',
                         (background_bottom.width, background_bottom.height))  # open a new image with alpha channel
    combined.paste(background_bottom, (0, 0))
    combined.paste(img, (4210, 1940))
    combined.paste(background_top, (0, 0),
                   mask=background_top)  # this is the only layer that we care about alpha masking
    combined = combined.resize((round(combined.width / 3), round(combined.height / 3)))  # resize because why not
    in_situ_filename = _filename[0:-4] + "_with_background.png"
    combined.save(os.path.join(main_dir, in_situ_filename))  # n.b. saving as jpg will end up being much smaller.


if __name__ == '__main__':
    # CONFIGURATION
    main_dir = os.getcwd() + '/card_files'  # directory of cards you want to go through
    print(main_dir)
    # font = '/Users/ilsefunkhouser/Downloads/2012-12-etsy/fonts/KeeponTruckin.ttf' # a font.
    font_name = 'KeeponTruckin.ttf'  # a font.
    files = os.listdir(main_dir)
    # I got this background on a site that claimed to be free public domain images.
    # I did no further research about it.
    background_bottom = Image.open(
        os.path.join(main_dir, '../backgrounds/background_2_bottom_layer.png'))  # background alpha bottom
    background_top = Image.open(
        os.path.join(main_dir, '../backgrounds/background_2_top_layer.png'))  # background alpha top

    fronts = [x for x in files if 'front.jpg' in x]  # get the files that are just the "front.jpg" files.

    for x in fronts:
        transform_pic(x, font_name)  # generate the small version and the larger watermarked version
        generate_in_situ(fronts[0], background_top, background_bottom)  # generate the in-situ version.
