from PIL import Image, ImageDraw, ImageFont
#import textwrap
import os
import time

# Размещает текст в центре изображения
def place_text(input_path, output_path, text, x_pos=0, y_pos=0, font_path=None, font_size=40):
    """
    Размещает текст по центру изображения.
    
    :param image_path: Путь к исходному изображению.
    :param output_path: Путь для сохранения результата.
    :param text: Текст для размещения на изображении.
    :param x_pos, y_pos: Смещение текста от цента.
    :param font_path: Путь к файлу шрифта. Если None, используется шрифт по умолчанию.
    :param font_size: Размер шрифта.
    """
    text_color = 'black'
    background_color = 'white'
    # Загрузка изображения
    image = Image.open(input_path)
    draw = ImageDraw.Draw(image)

    # Задание шрифта
    if font_path:
        font = ImageFont.truetype(font_path, font_size)
    else:
        font = ImageFont.load_default()
    
    # Вычисление размера текста
    text_width, text_height = draw.textsize(text, font=font)
    # Получение размера изображения
    image_width, image_height = image.size
    # Вычисление позиции для текста            
        
    x = (image_width - text_width) / 2 + x_pos
    y = (image_height - text_height) / 2 + y_pos
    # ФОН
    delta_x = 30
    delta_y = 10
    draw.rectangle([x-delta_x, y-delta_y, x + text_width+delta_x, y + text_height + delta_y+4], fill=background_color)
    draw.text(xy=(x, y), text=text, fill=text_color, font=font,)

    
    # Сохранение изображения
    image.save(output_path)
    return True
