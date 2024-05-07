from django.http import HttpResponse
from django.conf import settings
import os


def get_image(request, image_name):
    # Определяем путь к папке с изображениями
    images_folder = os.path.join(settings.BASE_DIR, 'media/images')

    # Полный путь к изображению
    image_path = os.path.join(images_folder, image_name)

    # Проверяем существует ли файл с заданным именем
    if os.path.exists(image_path):
        # Открываем файл и читаем его содержимое
        with open(image_path, 'rb') as f:
            image_data = f.read()

        # Определяем MIME-тип изображения
        content_type = 'image/jpeg'  # Замените на нужный MIME-тип вашего изображения

        # Возвращаем изображение в HTTP response
        return HttpResponse(image_data, content_type=content_type)
    else:
        # Если файл не найден, возвращаем HTTP 404 Not Found
        return HttpResponse(status=404)

