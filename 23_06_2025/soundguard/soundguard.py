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
        self.url = 'https://po-gska.ru/product-sitemap.xml'
        self.data = []
        self.ind = 0
        self.ua = UserAgent()


    def get_soup(self, url):
        response = requests.get(url=url)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')
        return soup

    def collect_all_pages(self):
        cat_urls = ['https://soundguard.ru/' + i.select_one('a')['href'] for i in self.get_soup('https://soundguard.ru/catalog/').select('.b-category__item.category-detail')]

        products_urls = []
        for u in cat_urls:
            products_soup = self.get_soup(u)
            products_urls.extend(['https://soundguard.ru/' + i.select_one('a')['href'] for i in products_soup.select('.b-category__item.js-category-item')])

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
                    meta_description = soup.select_one('meta[name="description"]').get('content').strip()
                except:
                    meta_description = ''

                try:
                    meta_title = soup.select_one('title').text.strip()
                except:
                    meta_title = ''

                try:
                    title = soup.select_one('h1').text.strip()
                except:
                    title = ''

                try:
                    article = [i.text.strip() for i in soup.select_one('.b-single-item__info-table').select_one('tr').select('.ammount')]
                except:
                    article = ''

                try:
                    path = ' > '.join([i.text.strip() for i in soup.select_one('.b-breadcrumbs').select('li')][:-1])
                except:
                    path = ''

                try:
                    category = [i.text.strip() for i in soup.select_one('.b-breadcrumbs').select('li')][:-1][2]
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
                    image = 'https://soundguard.ru' + soup.select_one('[itemprop="image"]').get('src')
                except:
                    image = ''

                try:
                    gallery = ''
                except:
                    gallery = ''

                try:
                    main_description = soup.select_one('p[itemprop="description"]').text.strip()
                except:
                    main_description = ''

                try:
                    description = '\n'.join([i.text.strip() for i in soup.select_one('.b-single-item__middle').select_one('.right').select('p, ul')][1:])
                except:
                    description = ''

                try:
                    price = [i.text.split()[0] for i in soup.select('.ammount.price')]
                except:
                    price = ''

                try:
                    characteristics = {}
                    for i in [i for i in soup.select_one('.b-single-item__info-table').select('tr')[1:-1] if i.select_one('.title')]:
                        key = i.select_one('.title').text.strip()
                        value = [j.get_text(separator=' ').replace('\n', '').strip() for j in i.select('.ammount')]
                        characteristics[key] = value

                except:
                    characteristics = {}

                try:
                    tech_characteristics = {}
                    for i in soup.select_one('.b-single-item__charact').select('div'):
                        key = i.select_one('.title').text.strip().replace(':', '')
                        value = [i.select_one('.text').text.strip()] * len(article)
                        tech_characteristics[key] = value

                except:
                    tech_characteristics = {}


                characteristics.update(tech_characteristics)

                for i in range(len(article)):
                # Объединяем основные поля и свойства
                    product_data = {
                        'Название': title,
                        'url': url,
                        'meta_description': meta_description,
                        'meta_title': meta_title,
                        'Артикул': article[i],
                        'Категория': category,
                        'Путь': path,
                        'Картинка': image,
                        'Галерея': gallery,
                        'Описание': main_description,
                        'Цена': price[i],
                        'Доп описание': description,
                        # 'Доступность': availability
                    }

                    product_data.update({k:v[i] for k,v in characteristics.items()})
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
correct_path = os.path.join('23_06_2025', 'soundguard', 'soundguard.xlsx')

try:
    df.to_excel(correct_path, index=False)
except PermissionError:
    print("Файл занят. Закройте его.")
    time.sleep(10)  # Дать время на закрытие файла
    df = pd.read_excel(correct_path)  # Повторная попытка