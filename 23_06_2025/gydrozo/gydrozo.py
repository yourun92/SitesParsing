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
        self.url = 'https://www.gydrozo.ru/sitemap-iblock-21.xml'
        self.data = []
        self.ind = 0
        self.ua = UserAgent()


    def collect_all_pages(self):

        response = requests.get(url=self.url, verify=False)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'xml')

        product_urls = [i.find('loc').text for i in soup.find_all('url')]


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

                response = requests.get(url=url, headers=headers, timeout=30, verify=False)
                response.encoding = 'utf-8'
                soup = BeautifulSoup(response.text, 'lxml')

                url = url

                try:
                    meta_description = soup.select_one('meta[name="description"]')['content']
                except:
                    meta_description = ''

                try:
                    meta_title = soup.select_one('title').text
                except:
                    meta_title = ''

                try:
                    title = soup.select_one('.no-sidebar').select_one('h1').text.strip()
                except:
                    title = ''

                # try:
                #     article = soup.select_one('.artikul').text.split(':')[-1].strip()
                # except:
                #     article = ''

                try:
                    path = ' > '.join([i.text.strip() for i in soup.select_one('.breadcrumbs').select('a')])
                except:
                    path = ''

                try:
                    category = [i.text.strip() for i in soup.select_one('.breadcrumbs').select('a')][3]
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
                    src = 'https://www.gydrozo.ru/' + soup.select_one('.bjqs').select_one('img')['src']
                    if 'upload/' in src:
                        parts = src.rsplit('/', 1)
                        image = parts[0] + '/' + quote(parts[1])
                except:
                    image = ''


                # try:
                #     gallery = ' | '.join([i['href'] for i in soup.select_one('.tovar_mini_gallery').select('[data-fancybox="gallery"]')])
                # except:
                #     gallery = ''

                try:
                    main_description = soup.select_one('.item-det-product-text').text.strip()
                except:
                    main_description = ''


                # try:
                #     _price = soup.select_one('#img')
                #     if _price:
                #         price = _price.text.strip()
                #     else:
                #         price = 'Под заказ'
                # except:
                #     price = ''


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
                    for i in soup.select_one('.item-det-2').select('.item-det-rel-block'):
                        if i.select_one('a').text == 'Технические характеристики':
                            for row in i.select_one('table').select('tr'):
                                key_value = row.select('td')
                                key = key_value[0].text.strip()
                                value = key_value[1].text.strip()
                                characteristics[key] = value

                except:
                    characteristics = {}

                try:
                    for i in soup.select_one('.item-det-2').select('.item-det-rel-block'):
                        if i.select_one('a').text == 'Области применения':
                            application_field = i.select_one('.item-det-rel-cont').get_text(separator='\n').strip()


                except:
                    application_field = ''

                try:
                    for i in soup.select_one('.item-det-2').select('.item-det-rel-block'):
                        if i.select_one('a').text == 'Преимущества':
                            advantages = i.select_one('.item-det-rel-cont').get_text(separator='\n').strip()


                except:
                    advantages = ''

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
                    # 'Галерея': gallery,
                    'Описание': main_description,
                    # 'Цена': price,
                    # 'Доп описание': description,
                    # 'Доступность': availability
                    'Область применения': application_field,
                    'Преимущества': advantages
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
correct_path = os.path.join('23_06_2025', 'gydrozo', 'gydrozo.xlsx')

try:
    df.to_excel(correct_path, index=False)
except PermissionError:
    print("Файл занят. Закройте его.")
    time.sleep(10)  # Дать время на закрытие файла
    df = pd.read_excel(correct_path)  # Повторная попытка