import random
import time

import requests
from bs4 import BeautifulSoup
import csv

def get_data():
    with open('sneakers.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(('Пара', 'Фото'))
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/92.0.4515.159 Safari/537.36 OPR/78.0.4093.231 ',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    for page in range(1, 26):
        url = f'https://stockx.com/sneakers?page={page}'
        print(f'Обзор на странице #{page}')
        response = requests.get(url, headers=headers)
        print(response.status_code)
        with open('index.html', 'w', encoding='utf-8') as file:
            file.write(response.text)
        with open('index.html', encoding='utf-8') as file:
            src = file.read()
        soup = BeautifulSoup(src, 'lxml')
        sneakers_list = soup.find_all('div', class_='tile css-1duh0sd-Tile ew378jy0')
        for sneaker in sneakers_list:
            sneaker_url = 'https://stockx.com' + sneaker.find('a').get('href')
            resp = requests.get(sneaker_url, headers=headers)
            with open('index.html', 'w', encoding='utf-8') as file:
                file.write(resp.text)
            with open('index.html', encoding='utf-8') as file:
                src = file.read()
            soup = BeautifulSoup(src, 'lxml')
            name = soup.find('h1')
            name = soup.find('h1').text + ' ' + name.find_next('h1').text
            img = soup.find('img').get('src')
            print(f'{name} загружена')
            with open('sneakers.csv', 'a', encoding='utf-8', newline='') as file:
                writer = csv.writer(file)
                writer.writerow((name, img))
            time.sleep(random.randrange(1, 5))

def main():
    get_data()

if __name__ == '__main__':
    main()