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


class Parser:
    def __init__(self):
        self.url = 'https://rentgenprotect.ru/sitemap.xml'
        self.data = []
        self.ind = 0
        self.ua = UserAgent()


    def collect_all_pages(self):

        response = requests.get(url=self.url)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'xml')

        all_urls = soup.select('url')
        product_urls = []
        for u in all_urls:
            if float(u.select_one('priority').text) == 1:
                product_urls.append(u.select_one('loc').text)

        return list(set(product_urls))


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
                    meta_title = soup.select_one('meta[property="og:title"]').get('content').strip()
                except:
                    meta_title = ''

                try:
                    titles = []
                    if soup.select_one('.form-control.js-change-price'):
                        title = soup.select_one('.cat_title').text.strip()
                        title_parts = [string.text[:string.text.index('(')].strip() for string in soup.select_one('.form-control.js-change-price').select('option')]
                        for t in title_parts:
                            titles.append(title + ' (' + t + ')')
                    else:
                        title = soup.select_one('.cat_title').text.strip()

                except:
                    titles = []
                    title = ''

                try:
                    article = soup.select_one('.item_sku').text.strip().split(':')[-1].strip()
                except:
                    article = ''

                try:
                    path = ' > '.join([i.text.strip() for i in soup.select_one('.breadcrumb').select('li') if i.text])
                except:
                    path = ''

                try:
                    category = [i.text.strip() for i in soup.select_one('.breadcrumb').select('li') if i.text][2]
                except:
                    category = ''


                try:
                    availability = soup.select_one('.item_stock').text.strip()
                except:
                    availability = ''

                try:
                    image = 'https://rentgenprotect.ru/' + soup.select_one('.item_main_img').select_one('span')['href']
                except:
                    image = ''


                try:
                    gallery = ' | '.join([i['href'] for i in soup.select_one('.item_main_img_thumbs').select('span')])
                except:
                    gallery = ''


                try:
                    if 'цена указана' or 'цена\nуказана' in soup.select_one('div[itemprop="description"]').select_one('p').text.strip():
                        if soup.select_one('div[itemprop="description"]').select('p')[1].text.strip():
                            main_description = soup.select_one('div[itemprop="description"]').select('p')[1].text.strip()
                        else:
                            main_description = soup.select_one('div[itemprop="description"]').select('p')[2].text.strip()
                    else:
                        main_description = soup.select_one('div[itemprop="description"]').select_one('p').text.strip()

                except:
                    main_description = ''

                try:
                    description = soup.select_one('div[itemprop="description"]').get_text(separator='\n').strip()
                except:
                    description = ''

                try:
                    if soup.select_one('.form-control.js-change-price'):

                        prices = [p['data-digprice'] for p in soup.select_one('.form-control.js-change-price').select('option')]
                    else:
                        price = soup.select_one('#jsPrice').text.replace('₽', '').strip()

                except:
                    price = ''
                    prices = []

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
                    for i in soup.select_one('.table.table-bordered').select('tr'):
                        key = i.select_one('td').text.strip()
                        value = i.select('td')[-1].text.strip()
                        characteristics[key] = value

                except:
                    characteristics = {}
                # characteristics.update(tech_characteristics)

                # Объединяем основные поля и свойства
                if titles:
                    for t,p in zip(titles, prices):
                        product_data = {
                            'Название': t,
                            'url': url,
                            'meta_description': meta_description,
                            'meta_title': meta_title,
                            'Артикул': article,
                            'Категория': category,
                            'Путь': path,
                            'Картинка': image,
                            'Галерея': gallery,
                            'Описание': main_description,
                            'Цена': p,
                            'Доп описание': description,
                            'Доступность': availability
                        }

                        product_data.update(characteristics)
                        self.data.append(product_data)

                else:
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
correct_path = os.path.join('23_06_2025', 'rentgenprotect', 'rentgenprotect.xlsx')

try:
    df.to_excel(correct_path, index=False)
except PermissionError:
    print("Файл занят. Закройте его.")
    time.sleep(10)  # Дать время на закрытие файла
    df = pd.read_excel(correct_path)  # Повторная попытка