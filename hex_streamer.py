
import subprocess
import hashlib

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

class WidthHeight:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def to_tuple(self):
        return self.width, self.height

IMAGE_RESOLUTION = WidthHeight(1920, 1080)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
RED_SQUARES_SIZE = WidthHeight(80, 80)
TEXT_MARGIN = 30
TEXT_Y_MARGIN = 50
PAGE_TEXT_SIZE = 60
SHA_TEXT_SIZE = 45
TEXT_SIZE = 45
SYNC_MARK_COORD = 219, 45,
TARGET_FILE = "toto.rar"
FONT = "monofont.otf"
IMG_FILE_PATH = f"tmp_files/hex_s/{TARGET_FILE}_size_{TEXT_SIZE}_imgs"
VIDEO_TEXT_FILE_PATH = f"tmp_files/hex_s/{TARGET_FILE}_size_{TEXT_SIZE}_text_data"
VIDEO_FILE_PATH = f"tmp_files/hex_s/{TARGET_FILE}_size_{TEXT_SIZE}_video"
CHAR_HEIGHT = 20

def convert_to_special(s):
    return s.upper().replace("A", "A").replace("B", "?").replace("C", "x") \
        .replace("D", "d").replace("E", "p").replace("F", "f").replace("0", "q") \
        .replace("3", "m").replace("5", "K").replace("8", "S")

def draw_rectangle(img_drawer, left_x, left_y, width, height, color, linewidth=10):
    shape = [(left_x, left_y), (left_x+width, left_y+height)]
    img_drawer.rectangle(shape, outline=color, width=linewidth)

def draw_corner_rectangles(img_drawer, r_width, r_height):
    img_width, img_height = IMAGE_RESOLUTION.width, IMAGE_RESOLUTION.height
    draw_rectangle(img_drawer, 0, 0, r_width, r_height, RED)
    draw_rectangle(img_drawer, img_width - r_width, 0, r_width, r_height, RED)
    draw_rectangle(img_drawer, 0, img_height - r_height, r_width, r_height, RED)
    draw_rectangle(img_drawer, img_width - r_width, img_height - r_height, r_width, r_height, RED)

def draw_page_num(img_drawer, num):
    num = "Page " + str(num)
    font = ImageFont.truetype(FONT, PAGE_TEXT_SIZE)
    f_width, f_height = font.getsize(num)
    left_x = int(IMAGE_RESOLUTION.width/2.0 - f_width/2.0)
    left_y = int(110 / 2.0 - f_height / 2.0)
    img_drawer.text((left_x, left_y), num, font=font, fill=WHITE)

def get_char_height():
    max_line_size = IMAGE_RESOLUTION.width - TEXT_MARGIN * 2
    font = ImageFont.truetype(FONT, TEXT_SIZE)
    l_width, l_height = font.getsize('B')
    return l_height

def compute_number_of_char_per_line():
    max_line_size = IMAGE_RESOLUTION.width - TEXT_MARGIN * 2
    line = ''
    font = ImageFont.truetype(FONT, TEXT_SIZE)
    while True:
        line += 'B'
        l_width, l_height = font.getsize(line)
        if l_width > max_line_size:
            return len(line) - 1

def print_sha_on_page(img_drawer, text_bloc):
    hash = str(hashlib.sha256(text_bloc.replace(" ", "").encode('utf-8')).hexdigest())
    hash = str(hash).upper()
    font = ImageFont.truetype(FONT, SHA_TEXT_SIZE)
    
    text_a = hash[32:]
    text_a = convert_to_special(text_a)
    text_a_final = ''
    for char in text_a:
        text_a_final += char + " "
    f_width, f_height = font.getsize(text_a_final)
    left_x = int(IMAGE_RESOLUTION.width/2.0 - f_width/2.0)
    left_y = int((IMAGE_RESOLUTION.height-70-53))
    img_drawer.text((left_x, left_y), text_a_final, font=font, fill=WHITE)

    text_b = hash[:32]
    text_b = convert_to_special(text_b)
    text_b_final = ''
    for char in text_b:
        text_b_final += char + " "
    left_x = int(IMAGE_RESOLUTION.width/2.0 - f_width/2.0)
    left_y = int((IMAGE_RESOLUTION.height-70))
    img_drawer.text((left_x, left_y), text_b_final, font=font, fill=WHITE)

    return hash, text_a_final, text_b_final

def add_sync_mark(im_drawer):
    x, y = SYNC_MARK_COORD
    r = 20
    im_drawer.ellipse((x-r, y-r, x+r, y+r), fill=GREEN, outline=GREEN)

def remove_sync_mark(im_drawer):
    x, y = SYNC_MARK_COORD
    r = 21
    im_drawer.ellipse((x-r, y-r, x+r, y+r), fill=BLACK, outline=BLACK)

def draw_text_on_image(img_drawer, n_char_per_line, text, page_num):
    char_height = get_char_height()
    font = ImageFont.truetype(FONT, TEXT_SIZE)
    current_line = ''
    current_line_number = 0
    current_y_offset = RED_SQUARES_SIZE.height + TEXT_Y_MARGIN
    y_to_stop = IMAGE_RESOLUTION.height - RED_SQUARES_SIZE.height - TEXT_Y_MARGIN
    number_of_char_printed = 0
    text_bloc = ''
    text_bloc_data = []
    for char in text:
        number_of_char_printed += 1
        current_line += char + " "
        if len(current_line) == n_char_per_line:
            text_bloc += current_line
            img_drawer.text((TEXT_MARGIN, current_y_offset), convert_to_special(current_line), font=font, fill=WHITE)
            text_bloc_data.append(current_line)
            current_line = ''
            current_line_number += 1
            current_y_offset += char_height + 10
            if current_y_offset + char_height + 10 > y_to_stop:
                hash, a, b = print_sha_on_page(img_drawer, text_bloc)
                
                with open(rf"{VIDEO_TEXT_FILE_PATH}\{TARGET_FILE}_page_{page_num}.txt", "w") as f:
                    for line in text_bloc_data:
                        f.write(line+'\n')
                    f.write('\n')
                    f.write(hash.lower()+'\n')
                    f.write('\n')
                    f.write(a+'\n')
                    f.write(b+'\n')
                
                return text[number_of_char_printed:]

    text_bloc += current_line
    text_bloc_data.append(current_line)
    img_drawer.text((TEXT_MARGIN, current_y_offset), convert_to_special(current_line), font=font, fill=WHITE)
    hash, a, b = print_sha_on_page(img_drawer, text_bloc)
    with open(rf"{VIDEO_TEXT_FILE_PATH}\{TARGET_FILE}_page_{page_num}.txt", "w") as f:
        for line in text_bloc_data:
            f.write(line+'\n')
        f.write('\n')
        f.write(hash+'\n')
        f.write(hash.lower()+'\n')
        f.write('\n')
        f.write(a+'\n')
        f.write(b+'\n')
    return None

def make_video():
    command = [
        r"ffmpeg_full_build_2021-12-23-git-60ead5cd68\bin\ffmpeg.exe",
        "-r",
        "25", #fps
        "-s",
        "1920x1080",
        "-i",
        rf"{IMG_FILE_PATH}\{TARGET_FILE}_{TEXT_SIZE}_%7d.png",
        "-vcodec",
        "libx264",
        "-crf",
        "15",
        "-pix_fmt",
        "yuv420p",
        rf"{VIDEO_FILE_PATH}/{TARGET_FILE}_{TEXT_SIZE}.mp4",
    ]
    try:
        subprocess.check_output(command)
    except subprocess.CalledProcessError as e:
        print(e.output)


with open(TARGET_FILE, 'rb') as f:
    hexdata = str(f.read().hex()).upper()

true_current_page_num = 0
current_page_num = 0
remaining_text = hexdata
n_char_per_line = compute_number_of_char_per_line()
Path(IMG_FILE_PATH).mkdir(parents=True, exist_ok=True)
Path(VIDEO_TEXT_FILE_PATH).mkdir(parents=True, exist_ok=True)
Path(VIDEO_FILE_PATH).mkdir(parents=True, exist_ok=True)
while True:
    img = Image.new('RGB', IMAGE_RESOLUTION.to_tuple(), color=BLACK)
    img_drawer = ImageDraw.Draw(img)
    draw_rectangle(img_drawer, 0, 0, IMAGE_RESOLUTION.width, IMAGE_RESOLUTION.height, RED, linewidth=10)
    #draw_corner_rectangles(img_drawer, RED_SQUARES_SIZE.width, RED_SQUARES_SIZE.height)
    draw_page_num(img_drawer, true_current_page_num)
    remaining_text = draw_text_on_image(img_drawer, n_char_per_line, remaining_text, true_current_page_num)
    img.save(f'{IMG_FILE_PATH}/{TARGET_FILE}_{TEXT_SIZE}_{str(current_page_num).zfill(7)}.png')
    true_current_page_num += 1
    current_page_num += 1
    img.save(f'{IMG_FILE_PATH}/{TARGET_FILE}_{TEXT_SIZE}_{str(current_page_num).zfill(7)}.png')
    add_sync_mark(img_drawer)
    current_page_num += 1
    img.save(f'{IMG_FILE_PATH}/{TARGET_FILE}_{TEXT_SIZE}_{str(current_page_num).zfill(7)}.png')
    current_page_num += 1
    remove_sync_mark(img_drawer)
    img.save(f'{IMG_FILE_PATH}/{TARGET_FILE}_{TEXT_SIZE}_{str(current_page_num).zfill(7)}.png')
    current_page_num += 1

    if remaining_text is None:
        break

    print(true_current_page_num)

make_video()
