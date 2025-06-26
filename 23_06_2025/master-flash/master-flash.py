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
from urllib.parse import quote


class Parser:
    def __init__(self):
        self.url = 'https://master-flash.org/catalogs/'
        self.data = []
        self.ind = 0
        self.ua = UserAgent()
        self.product_urls = []
        self.cats = ['germetik', 'manzhety', 'dymohod', 'sistema-ventilyacii', 'krovelnye-aeratory', 'turbodeflektor', 'snegozaderzhatel-dlya-trub']


    def collect_all_pages(self):
        for cat in self.cats:
            url = self.url + cat + '?page=1'
            response = requests.get(url=url)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'lxml')

            if soup.select_one('nav[aria-label="Навигация по страницам"]'):
                pages = int(soup.select_one('nav[aria-label="Навигация по страницам"]').select('li')[-2].text)
            else:
                pages = 1

            for i in range(1, pages + 1):
                url = self.url + cat + '?page=' + str(i)
                print(url)
                response = requests.get(url=url)
                response.encoding = 'utf-8'
                soup = BeautifulSoup(response.text, 'lxml')
                self.product_urls.extend(['https://master-flash.org' + i.select_one('a')['href'] for i in soup.select_one('.flex.flex-wrap.gap-8').select('li')])





    def parsing_products(self):

        self.collect_all_pages()

        print(f'Всего товаров - {len(self.product_urls)}')

        for url in self.product_urls:
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
                    meta_description = ''
                except:
                    meta_description = ''

                try:
                    meta_title = soup.select_one('title').text.strip()
                except:
                    meta_title = ''

                try:
                    title = soup.select_one('.text-4xl.font-semibold.mb-8').text.strip()
                except:
                    title = ''

                # try:
                #     article = soup.select_one('.artikul').text.split(':')[-1].strip()
                # except:
                #     article = ''

                try:
                    path = ' > '.join([i.text.strip() for i in soup.select_one('nav[aria-label="Breadcrumb"]').select('li')])
                except:
                    path = ''

                try:
                    category = [i.text.strip() for i in soup.select_one('nav[aria-label="Breadcrumb"]').select('li')][1]
                except:
                    category = ''

                # try:
                #     if soup.select_one('.v_nalichii'):
                #         availability = soup.select_one('.v_nalichii').text.strip()
                #     elif soup.select_one('.no_v_nalichii'):
                #         availability = soup.select_one('.no_v_nalichii').text.strip()

                # except:
                #     availability = ''

                try:
                    images = ['https://master-flash.org' + i['href'] for i in soup.select_one('.fotorama').select('a')]
                    image = images[0]
                except:
                    image = ''


                try:

                    gallery = ' | '.join(images)
                except:
                    gallery = ''

                try:
                    main_description = soup.select_one('.app-base').text.strip()
                except:
                    main_description = ''


                try:
                    price = soup.select_one('#product-price').text.replace('₽', '').strip()
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

                try:
                    characteristics = {}
                    for i in soup.select_one('#tab__content0').select('li'):
                        key = i.select_one('p').text.strip()
                        value = i.select_one('div').text.strip()
                        characteristics[key] = value

                except:
                    characteristics = {}

                # try:
                #     for i in soup.select_one('.item-det-2').select('.item-det-rel-block'):
                #         if i.select_one('a').text == 'Области применения':
                #             application_field = i.select_one('.item-det-rel-cont').get_text(separator='\n').strip()


                # except:
                #     application_field = ''

                # try:
                #     for i in soup.select_one('.item-det-2').select('.item-det-rel-block'):
                #         if i.select_one('a').text == 'Преимущества':
                #             advantages = i.select_one('.item-det-rel-cont').get_text(separator='\n').strip()


                # except:
                #     advantages = ''

                # characteristics.update(tech_characteristics)


                # try:
                #     description = soup.select_one('[aria-labelledby="vert_tab_item-3"]')
                # except:
                #     description = ''



                # Объединяем основные поля и свойства
                product_data = {
                    'Название': title,
                    'url': url,
                    'meta_description': meta_description,
                    'meta_title': meta_title,
                    # 'Артикул': article,
                    'Категория': category,
                    'Путь': path,
                    'Картинка': image,
                    'Галерея': gallery,
                    'Описание': main_description,
                    'Цена': price,
                    # 'Доп описание': description,
                    # 'Доступность': availability
                    # 'Область применения': application_field,
                    # 'Преимущества': advantages
                }

                product_data.update(characteristics)
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
correct_path = os.path.join('23_06_2025', 'master-flash', 'master-flash.xlsx')

try:
    df.to_excel(correct_path, index=False)
except PermissionError:
    print("Файл занят. Закройте его.")
    time.sleep(10)  # Дать время на закрытие файла
    df = pd.read_excel(correct_path)  # Повторная попытка