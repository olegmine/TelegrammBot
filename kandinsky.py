import json
import time
import os
import asyncio

import config
import requests
import base64
from PIL import Image
from io import BytesIO



async def kandynsky(prompt):

    user_prompt = prompt


    def base64_to_image(base64_string, output_path):
        # Декодируем строку Base64 в бинарные данные
        image_data = base64.b64decode(base64_string)

        # Создаем объект изображения из бинарных данных
        image = Image.open(BytesIO(image_data))

        # Сохраняем изображение в файл
        image.save(output_path)

    key = config.kandinsky_key
    s_key = config.kandinsky_secret

    class Text2ImageAPI:

        def __init__(self, url, api_key, secret_key):
            self.URL = url
            self.AUTH_HEADERS = {
                'X-Key': f'Key {key}',
                'X-Secret': f'Secret {s_key}',
            }

        def get_model(self):
            response = requests.get(self.URL + 'key/api/v1/models', headers=self.AUTH_HEADERS)
            data = response.json()
            return data[0]['id']

        def generate(self, prompt, model, images=1, width=1024, height=1024):
            params = {
                "type": "GENERATE",
                "numImages": images,
                "width": width,
                "height": height,
                "generateParams": {
                    "query": f"{user_prompt}"
                }
            }

            data = {
                'model_id': (None, model),
                'params': (None, json.dumps(params), 'application/json')
            }
            response = requests.post(self.URL + 'key/api/v1/text2image/run', headers=self.AUTH_HEADERS, files=data)
            data = response.json()
            return data['uuid']

        def check_generation(self, request_id, attempts=10, delay=10):
            while attempts > 0:
                response = requests.get(self.URL + 'key/api/v1/text2image/status/' + request_id,
                                        headers=self.AUTH_HEADERS)
                data = response.json()
                if data['status'] == 'DONE':
                    return data['images']

                attempts -= 1
                time.sleep(delay)

    current_time = time.strftime("%Y-%m-%d_%H-%M")
    file_name = ('img_cache/image_' + current_time + '.png')

    if len(current_time)>0:
        api = Text2ImageAPI('https://api-key.fusionbrain.ai/', key, s_key)
        model_id = api.get_model()
        uuid = api.generate(user_prompt, model_id)
        images = str(api.check_generation(uuid))
        # print(images)
        # Пример данных в формате Base64
        base64_data = images




        # print(file_name)



        # Вызываем функцию и сохраняем изображение в файл image.png
        base64_to_image(base64_data, file_name)
    return file_name

# Удаляем старые ,уже отправленные пользователям файлы
async def delete_files(folder_path='img_cache'):

    # Получаем текущее время
    current_time = time.time()

    # Перебираем все файлы в папке
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # Проверяем, является ли файл файлом и содержит ли название дату и время
        if os.path.isfile(file_path) and "image_" in filename:
            # Получаем время создания файла
            creation_time = os.path.getctime(file_path)

            # Проверяем, прошло ли более 5 минут с момента создания файла
            if current_time - creation_time > 5 * 60:
                # Удаляем файл
                os.remove(file_path)

# print(asyncio.run(kandynsky('рыжая красотка в бикини ,на пляже ,в очках ,игриво улыбается')))