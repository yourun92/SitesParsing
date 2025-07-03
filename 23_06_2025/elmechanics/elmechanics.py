import pandas as pd
import requests
import lxml
from bs4 import BeautifulSoup
import xml
import time
import random
from fake_useragent import UserAgent
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import copy


class Parser:
    def __init__(self):
        self.url = 'https://www.elmechanics.ru/katalog/'
        self.data = []
        self.ind = 0
        self.ua = UserAgent()


    def collect_all_pages(self):

        response = requests.get(url=self.url)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'xml')

        cats_all = []
        brend_1 = ['https://www.elmechanics.ru' + i.select_one('a')['href'] for i in soup.select_one('.drp').select_one('ul').select('li')[1:]][:-5]
        brend_2 = ['https://www.elmechanics.ru' + i.select_one('a')['href'] for i in soup.select_one('.drp').select('ul')[1].select('li')[1:]]
        cats_all.extend(brend_1)
        cats_all.extend(brend_2)


        cats_all.extend(['https://www.elmechanics.ru/katalog/elementa/khimicheskie-kleevye-ankery/?PAGEN_1=2', 'https://www.elmechanics.ru/katalog/elementa/khimicheskie-kleevye-ankery/?PAGEN_1=3', 'https://www.elmechanics.ru/katalog/elementa/fasadnye-i-ramnye-dyubeli/?PAGEN_1=2', 'https://www.elmechanics.ru/katalog/elementa/soedinitelnye-elementy/?PAGEN_1=2'])

        product_urls = []
        for cat_url in cats_all:
            response = requests.get(url=cat_url)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'xml')
            product_urls.extend(['https://www.elmechanics.ru' + i['href'] for i in soup.select('.item-catalog')])

        return product_urls


    def parsing_products(self):

        product_urls = self.collect_all_pages()
        print(f'Всего товаров - {len(product_urls)}')
        for url in product_urls:
            try:
                headers = {
                    'User-Agent': self.ua.random,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8',
                    'Connection': 'keep-alive'
                }

                response = requests.get(url=url, headers=headers, timeout=30)
                response.encoding = 'utf-8'
                soup = BeautifulSoup(response.text, 'lxml')

                url = url

                try:
                    meta_description = soup.select_one('meta[name="description"]').get('content').strip()
                except:
                    meta_description = ''

                try:
                    meta_title = soup.select_one('title').text.strip()
                except:
                    meta_title = ''

                try:
                    title = soup.select_one('.rw').select_one('h1').text.strip()
                except:
                    title = ''

                try:
                    article = ''
                except:
                    article = ''


                try:
                    path = ' > '.join([i.text.strip().replace(' |', '') for i in soup.select_one('.bred').select('li')[:-1]])
                except:
                    path = ''
                try:
                    category = soup.select_one('.def_li.active').text.strip()
                except:
                    category = ''

                try:
                    availability = ''
                except:
                    availability = ''

                try:
                    image = 'https://www.elmechanics.ru' + soup.select_one('.lef').select_one('img')['src']
                except:
                    image = ''

                try:
                    gallery = ' | '.join(['https://www.elmechanics.ru/' + i['src'] for i in soup.select_one('.wr-gh').select('img')])
                except:
                    gallery = ''

                try:
                    main_description = soup.select_one('.lef').select_one('strong').text.strip()
                except:
                    main_description = ''

                try:
                    purpose = 'Назначение:\n\n' + soup.find(class_='dstrf', string='Назначение').find_next_sibling('ul').text
                    charact = 'Характеристики:\n\n' + soup.find(class_='dstrf', string='Характеристики').find_next_sibling('ul').text.strip()
                    description = purpose + '\n' + charact
                except:
                    description = ''

                try:
                    price = soup.select_one('.good_price').select_one('.h3').text.replace('₽', '').strip()
                except:
                    price = ''

                # try:
                #     tech_characteristics = {}
                #     for i in soup.select_one('.table_har.top').select('tr'):
                #         key = i.select_one('th').text.strip()
                #         value = i.select_one('td').text.strip()
                #         tech_characteristics[key] = value

                # except:
                #     tech_characteristics = {}

                # try:
                #     characteristics = {}
                #     if soup.select_one('.content').select_one('table'):

                #         for i in soup.select_one('.content').select_one('table').select('tr'):
                #             key = i.select_one('td').text.split(',')[0].replace('не менее', '').strip()
                #             value = i.select('td')[-1].text.strip()
                #             characteristics[key] = value

                #     if soup.select_one('.props_table'):
                #         for i in soup.select_one('.props_table').select('tr'):
                #             key = i.select_one('.char_name').text.replace('\t', '').split(',')[0].replace('не менее', '').strip()
                #             value = i.select_one('.char_value').text.strip().replace('\t', '')
                #             characteristics[key] = value

                # except:
                #     characteristics = {}
                # characteristics.update(tech_characteristics)


                # Объединяем основные поля и свойства

                product_data = {
                        'Название': title,
                        'url': url,
                        'meta_description': meta_description,
                        'meta_title': meta_title,
                        'Артикул': article,
                        'Категория': category,
                        'Путь': path,
                        'Картинка': image,
                        'Галерея': gallery,
                        'Описание': main_description,
                        'Цена': price,
                        'Доп описание': description,
                        'Доступность': availability
                    }

                # product_data.update(characteristics)
                self.data.append(product_data)

                self.ind += 1
                if self.ind % 50 == 0:
                    print(f'Обработано {self.ind} страниц')

                # Случайная задержка между запросами
                time.sleep(random.uniform(1, 3))

        #         # Сохраняем промежуточные результаты
        #         if self.ind % 100 == 0:
        #             df = pd.DataFrame(self.data)
        #             df.to_excel(f"mafproject_interim_{self.ind}.xlsx", index=False)



            except Exception as e:
                print(f"Ошибка при обработке {url}: {e}")
                continue


parser = Parser()
parser.parsing_products()


df = pd.DataFrame(parser.data)
correct_path = os.path.join('23_06_2025', 'elmechanics', 'elmechanics.xlsx')

try:
    df.to_excel(correct_path, index=False)
except PermissionError:
    print("Файл занят. Закройте его.")
    time.sleep(10)  # Дать время на закрытие файла
    df = pd.read_excel(correct_path)  # Повторная попытка