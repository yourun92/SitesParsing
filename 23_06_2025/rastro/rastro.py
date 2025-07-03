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
from selenium.webdriver.chrome.options import Options


class Parser:
    def __init__(self):
        self.url = 'https://www.rastro.ru/catalogue/'
        self.data = []
        self.ind = 0
        self.ua = UserAgent()


    def get_soup(self, url):
        response = requests.get(url=url)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')
        return soup

    def collect_all_pages(self):

        products_urls = []
        for u in self.get_soup(self.url).select_one('.content').select_one('ul').select('li')[3:]:
            prod = u.select('li')
            products_urls.extend(['https://www.rastro.ru' + i.select_one('a')['href'] for i in prod])

        return products_urls

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
                    meta_description = soup.select_one('meta[name="Description"]').get('content').strip()
                except:
                    meta_description = ''

                try:
                    meta_title = soup.select_one('title').text.strip()
                except:
                    meta_title = ''

                try:
                    title = soup.select_one('.newclasscard').text.strip()
                except:
                    title  = ''

                try:
                    article = soup.select_one('.cat_ty').text.strip()
                except:
                    article = ''

                try:
                    path = ' > '.join([i.text.strip() for i in soup.select_one('.top-block.kroshki').select('a')][:-1])
                except:
                    path = ''


                try:
                    category = [i.text.strip() for i in soup.select_one('.top-block.kroshki').select('a')][:-1][2]
                except:
                    category = ''


                # if soup.select_one('.v_nalichii') and len(soup.select('.v_nalichii')) == 1 and not soup.select_one('.sort_title'):
                #     availability = soup.select_one('.v_nalichii').text.strip()
                # elif soup.select_one('.no_v_nalichii') and len(soup.select('.no_v_nalichii')) == 1 and not soup.select_one('.sort_title'):
                #     availability = soup.select_one('.no_v_nalichii').text.strip()
                # else:
                #     availability = 'На удаление'
                #     continue

                try:
                    image = 'https://www.rastro.ru' + soup.select_one(f'[alt="{title}"]').get('src')
                except:
                    image = ''

                try:
                    gallery = ' | '.join(['https://www.rastro.ru/' + i['href'] for i in soup.select_one('.catalog_text').find('h2', string='Область применения').find_next_sibling('table').select('a')])
                except:
                    gallery = ''

                try:
                    main_description = soup.select_one('.catalog_text').find('h2', string='Описание ').find_next_sibling().text.strip()
                except:
                    main_description = ''

                try:
                    desc_1 =  'Область применения:\n\n' + soup.select_one('.catalog_text').find('h2', string='Область применения').find_next_sibling().text.strip()
                    desc_2 = 'Преимущества:\n\n' + soup.select_one('.catalog_text').find('h2', string='Преимущества').find_next_sibling().text.strip()
                    desc_3 = 'Типы обрабатываемых поверхностей:\n\n' + soup.select_one('.catalog_text').find('h2', string='Типы обрабатываемых поверхностей').find_next_sibling().text.strip()
                    description = f'{desc_1}\n\n{desc_2}\n\n{desc_3}'
                except:
                    description = ''

                try:
                    price = ''
                except:
                    price = ''

                # try:
                #     characteristics = {}
                #     for i in [i for i in soup.select_one('.b-single-item__info-table').select('tr')[1:-1] if i.select_one('.title')]:
                #         key = i.select_one('.title').text.strip()
                #         value = [j.get_text(separator=' ').replace('\n', '').strip() for j in i.select('.ammount')]
                #         characteristics[key] = value

                # except:
                #     characteristics = {}

                try:
                    characteristics = {}
                    for i in soup.select_one('.catalog_text').find('h2', string='Технические характеристики').find_next_sibling('table').select('tr')[1:]:
                        key = i.select('td')[0].text.strip()
                        value = i.select('td')[-1].text.strip()
                        characteristics[key] = value

                except:
                    characteristics = {}

                # characteristics.update(tech_characteristics)

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
                    'Компания': 'Растро',
                    # 'Доступность': availability
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
correct_path = os.path.join('23_06_2025', 'rastro', 'rastro.xlsx')

try:
    df.to_excel(correct_path, index=False)
except PermissionError:
    print("Файл занят. Закройте его.")
    time.sleep(10)  # Дать время на закрытие файла
    df = pd.read_excel(correct_path)  # Повторная попытка