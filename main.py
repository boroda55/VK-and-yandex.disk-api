import configparser
import json
import requests
from tqdm import tqdm
from datetime import datetime
import logging
import os.path

config = configparser.ConfigParser()
config.read('setting.ini')

logging.basicConfig(
    level=logging.INFO,
    filename='log.log',
    filemode='a',
    format='[%(asctime)s] %(levelname)s %(message)s',
    encoding='utf-8'
)


class VK:
    def __init__(self, version='5.199'):
        self.params = {
            'access_token': config['Token']['vk_token'],
            'v': version
        }
        self.base = 'https://api.vk.com/method/'

    def get_photos(self, count=5):
        url = f'{self.base}photos.get'
        params = {
            'owner_id': config['Other']['id_vk'],
            'count': count,
            'album_id': config['Other']['album_id'],
            'extended': 1
        }
        params.update(self.params)
        response = requests.get(url, params=params)
        logging.info(f'Сохранены данные по {count} фотографиям '
                     f'из {config['Other']['album_id']}.')
        return response.json()


class Transfer:
    def __init__(self, json_VK):
        self.json_VK = json_VK

    def selection(self):
        list_photo_upload = list()
        try:
            for i in self.json_VK['response']['items']:
                data_photo_dict = dict()
                data_photo_dict['file_name'] = f'{i['likes']['count']}.jpg'
                max_size_photo = max(i['sizes'], key=lambda x: x['height'])
                data_photo_dict['url'] = max_size_photo['url']
                list_photo_upload.append(data_photo_dict)
        except KeyError as err:
            logging.error('KeyError', exc_info=True)
        set_count_like = set()
        today = datetime.now()
        str_date_now = today.strftime('%d.%m.%Y')
        for photo in list_photo_upload:
            file_name = photo['file_name']
            if file_name in set_count_like:
                photo['file_name'] = photo['file_name'].replace('.jpg', f'_{str_date_now}.jpg')  # Изменяем имя, добавляя '_duplicate'
            else:
                set_count_like.add(file_name)
        logging.info(f'Найдены фотографии по самому наибольшему размеру.')
        return list_photo_upload


class YD:
    def __init__(self, list_photo_upload):
        self.yd_token = config['Token']['yd_token']
        self.save_folder = config['Other']['save_folder']
        self.list_photo_upload = list_photo_upload
        self.base = 'https://cloud-api.yandex.net/v1/disk/resources'
        self.headers = {
            'Authorization': self.yd_token
        }

    def create_folder(self):
        params = {
            'path': self.save_folder
        }
        response = requests.put(self.base, params=params, headers=self.headers)
        if response.status_code != 201:
            logging.warning(f'HTTP код {response.status_code}: {response.text}')
        else:
            logging.info(f'HTTP код {response.status_code}')

    def upload_file(self):
        for photo_upload in tqdm(self.list_photo_upload):
            url = f'{self.base}/upload'
            params = {
                'path': f'{self.save_folder}/{photo_upload['file_name']}',
                'url': photo_upload['url']
            }
            response = requests.post(url, headers=self.headers, params=params)
        logging.info(f'Фотографии перенесены из ВК на ЯД')


if os.path.isfile('setting.ini'):
    if len(config['Token']['vk_token']) > 0 and len(config['Token']['yd_token']) > 0 and \
       len(config['Other']['save_folder']) > 0 and len(config['Other']['album_id']) > 0 and \
       len(config['Other']['id_vk']) > 0:
        vk_connection = VK()
        transfer = Transfer(vk_connection.get_photos())
        yd_connection = YD(transfer.selection())
        yd_connection.create_folder()
        yd_connection.upload_file()
    else:
        logging.critical('Проверьте внесены ли в файле "setting.ini" все данные')
        print('Проверьте внесены ли в файле "setting.ini" все данные')
else:
    logging.critical('Конфигурационный файл "setting.ini" отсутствует')
    print('Создайте конфигурационный файл "setting.ini"')
