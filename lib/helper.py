import os
from datetime import datetime, timedelta

def get_current_time(timezone):
    
    utc_now = datetime.utcnow()

    # Создайте объект timedelta для задания разницы в часах
    target_offset = timedelta(hours=timezone)

    # Примените разницу к текущей дате и времени
    current_datetime = utc_now + target_offset
    return current_datetime

def get_news_time(format=None, round=True, timezone=3):
    # Примените разницу к текущей дате и времени
    current_datetime = get_current_time(timezone)
    # Вычислить разницу в минутах до следующего часа
    minutes_to_next_hour = 60 - current_datetime.minute

    if round:
        # Если текущее время не в конце часа, округлить вверх
        if minutes_to_next_hour < 60:
            result_datetime = current_datetime + timedelta(minutes=minutes_to_next_hour)
            result_datetime = result_datetime.replace(second=0, microsecond=0)
        else:
            # Если уже конец часа, просто обнулить минуты
            result_datetime = current_datetime.replace(minute=0, second=0, microsecond=0)
    else:
        result_datetime = current_datetime

    if format == 'usa':
        return result_datetime.strftime("%m/%d/%y %I:%M %p")
    if format != None:
        return result_datetime.strftime(format)
    return result_datetime.strftime("%d.%m.%y %H:%M")

def generate_filename(path):
    ext = get_file_extension(path)
    name = get_file_name(path)
    timestamp = str(datetime.utcnow())
    print("TIME : ", timestamp)
    timestamp = timestamp.replace(" ", "")
    timestamp = timestamp.replace(".", "_")
    timestamp = timestamp.replace(":", "")
    timestamp = timestamp.replace("-", "")
    return f"{name}_{timestamp}.{ext}"

def get_file_extension(file_path):
    # Извлечь расширение файла из пути
    _, file_extension = os.path.splitext(file_path)
    
    # Удалить точку из расширения (если она присутствует)
    file_extension = file_extension[1:] if file_extension.startswith('.') else file_extension
    
    return file_extension

def get_file_name(file_path):
    # Извлечь имя файла из полного пути
    file_name = os.path.basename(file_path)
    name, _ = os.path.splitext(file_name)
    #r = file_name.rsplit(".")
    return name