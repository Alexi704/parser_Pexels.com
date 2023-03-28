import requests
from tqdm import tqdm
import json
import os
import math
from dotenv import load_dotenv

load_dotenv()
headers = {'Authorization': f'{os.getenv("API_KEY")}'}
proxies = {
    'https': f'http://{os.getenv("PROXY_LOGIN")}:{os.getenv("PROXY_PASS")}'
             f'@{os.getenv("PROXY_IP")}:{os.getenv("PROXY_PORT")}'
}


def scrap_pexels(query=''):
    query_str = f'https://api.pexels.com/v1/search?query={query}&per_page=80'
    response = requests.get(url=query_str, headers=headers, proxies=proxies)

    if response.status_code != 200:
        return print(f'Ошибка. Статус код - {response.status_code}, {response.json()}')

    img_dir_path = 'out/' + '_'.join(i for i in query.split(' ') if i.isalnum())
    json_data = response.json()
    images_count = json_data.get('total_results')

    if not os.path.exists(img_dir_path) and images_count > 0:
        os.makedirs(img_dir_path)

    # with open(f'out/result_{query}.json', 'w', encoding='utf-8') as file:
    #     json.dump(json_data, file, indent=4, ensure_ascii=False)

    if not json_data.get('next_page'):
        print(f'[INFO] Всего изображений: {images_count}.')
        img_urls = [item.get('src', {}).get('original') for item in json_data.get('photos')]
        download_images(img_list=img_urls, img_dir_path=img_dir_path)
    else:
        print(f'[INFO] Всего изображений: {images_count}. Сохранение может занять какое-то время.')

        images_list_urls = []
        for page in range(1, math.ceil(images_count / 80) + 1):
            query_str = f'{query_str}&page={page}'
            response = requests.get(url=query_str, headers=headers, proxies=proxies)
            json_data = response.json()
            img_urls = [item.get('src', {}).get('original') for item in json_data.get('photos')]
            images_list_urls.extend(img_urls)
        download_images(img_list=images_list_urls, img_dir_path=img_dir_path)


def download_images(img_list=[], img_dir_path=''):
    for item_url in tqdm(img_list):
        response = requests.get(url=item_url, headers=headers, proxies=proxies)
        img = response.content
        if response.status_code == 200:
            with open(f'./{img_dir_path}/{item_url.split("-")[-1]}', 'wb') as file:
                file.write(img)
        else:
            print('Что-то пошло не так при скачивании изображения!')


def main():
    query = input('Введите ключевую фразу для поиска: ')
    scrap_pexels(query=query)


if __name__ == '__main__':
    main()
