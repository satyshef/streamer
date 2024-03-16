import random 
import lib.youtube.stream as youtube
import lib.helper as helper
import lib.image.modifier as image

IMAGE_INPUT_PATH = 'youtube_streamer/images/masa_chronicle.png'
IMAGE_RESULT_DIR = 'thumbnail/'
IMAGE_FONT = 'youtube_streamer/fonts/Geist-UltraBlack.otf'
IMAGE_FONT_SIZE = 70
SOURCE_DIR = '/Users/outsider/Source/python/text2video/out/masa_live_1920_1080'
TIMEZONE = 3

def test_youtube_stream():
    TITLE = "СВОДКА НОВОСТЕЙ"
    DESCRIPTION = "Самые актуальные новости на данный момент"
    THUMBNAIL_FILE = "youtube_streamer/images/masa_stream.png"
    ingestion = youtube.create_stream(TITLE, DESCRIPTION, THUMBNAIL_FILE, "public")
    print(ingestion)

def create_thumbnail():
    font_size = IMAGE_FONT_SIZE
    font_path = IMAGE_FONT

    # Если указан IMAGE_INPUT_PATH применяем его иначе берем случайное изображение из директории с видеофрагментами
    image_list = helper.get_files_list(SOURCE_DIR, ['png', 'jpeg', 'jpg'])
    if len(image_list) != 0:
        image_file = random.choice(image_list)
        image_input_path = f"{SOURCE_DIR}/{image_file}"
        # если обложка из директории с исходниками тогда дату размещаем вверху
        x_pos = 0
        y_pos = 300
        font_size = int(font_size * 0.7)
        #font_path = 'youtube_streamer/fonts/Geist-Light.otf'
    else:
        if IMAGE_INPUT_PATH != '':
            image_input_path = IMAGE_INPUT_PATH 
            x_pos = 0
            y_pos = 0
        else:
            return None
    
    image_out_path = IMAGE_RESULT_DIR + helper.generate_filename(image_input_path)
    # Пример использования функции
    time = helper.get_formated_time(format=None, round=False, timezone=TIMEZONE)
    if image.place_text(input_path=image_input_path, output_path=image_out_path, text=time, x_pos=x_pos, y_pos=y_pos, font_path=font_path, font_size=font_size):
        return image_out_path
    return None



if __name__ == '__main__':
    #lst = helper.get_files_list('/Users/outsider/Downloads/newsvideo/export', ['mp4'])
    #test_youtube_stream()
    #img_path = test_text_image()
    create_thumbnail()
    #print(lst)
    
    
   