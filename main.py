import configparser
from pprint import pprint
import requests
from tqdm import tqdm



config = configparser.ConfigParser()
config.read('setting.ini')
vk_token = config['Token']['vk_token']

class VK:
    def __init__(self, token, version='5.199'):
        self.params = {
            'access_token': token,
            'v': version
        }
        self.base = 'https://api.vk.com/method/'

    def get_photos(self, user_id, count=5):
        url = f'{self.base}photos.get'
        params = {
            'owner_id': user_id,
            'count': count,
            'album_id': 'profile',
            'extended': 1
        }
        params.update(self.params)
        response = requests.get(url, params=params)
        return response.json()

vk_connector = VK(vk_token)
pprint(vk_connector.get_photos(65843136))
