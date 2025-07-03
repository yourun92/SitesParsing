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


class Parser:
    def __init__(self):
        self.url = 'https://prosvar.com/sitemap-catalog.xml'
        self.data = []
        self.ind = 0
        self.ua = UserAgent()


    def collect_all_pages(self):

        response = requests.get(url=self.url)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'xml')
        all_urls = soup.select('url')
        product_urls = []
        for url in all_urls:
            if url.select_one('changefreq'):
                product_urls.append(url.select_one('loc').text)

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
                    meta_description = soup.select_one('meta[name="description"]').get('content')
                except:
                    meta_description = ''

                try:
                    meta_title = soup.select_one('title').text.strip()
                except:
                    meta_title = ''

                try:
                    title = soup.select_one('[itemprop="name"]').text.strip()
                except:
                    title = ''

                try:
                    article = ''
                except:
                    article = ''

                try:
                    path = ' > '.join([i.text.strip() for i in soup.select_one('.fw-bc').select('li')])
                except:
                    path = ''

                try:
                    category = [i.text.strip() for i in soup.select_one('.fw-bc').select('li')][2]
                except:
                    category = ''

                try:
                    availability = soup.select_one('.uk-margin-small-right.uk-margin-small-bottom.uk-text-success').text.strip()
                except:
                    availability = ''

                try:
                    image = soup.select_one('.lb-link.uk-height-1-1.uk-flex.uk-flex-middle').select_one('link').get('href')
                except:
                    image = ''

                try:
                    gallery = ' | '.join(['https://prosvar.com' + i.select_one('a')['href'] for i in soup.select_one('.uk-slideshow-items').select('li')[1:]])
                except:
                    gallery = ''

                try:
                    main_description = soup.select_one('.tab-body.fw-tab-body.fw-content').text.strip()
                except:
                    main_description = ''

                try:
                    price = soup.select_one('span[itemprop="price"]').text.strip()
                except:
                    price = ''

                # try:
                #     tech_characteristics = {}
                #     for i in soup.select_one('.table.table_desc').select_one('tbody').select('tr'):
                #         tds = i.select('td')
                #         key = tds[0].text
                #         value = tds[1].text
                #         measure = tds[2].text
                #         tech_characteristics[key] = value + ' ' + measure

                # except:
                #     tech_characteristics = {}

                try:
                    characteristics = {}
                    for i in soup.select_one('.uk-width-expand').select('.fw-property-item'):
                        key_elem = i.select_one('.fw-property-name').text.strip().capitalize()
                        val_elem = i.select_one('.fw-property-values').text.strip()
                        characteristics[key_elem] = val_elem

                except:
                    characteristics = {}

                # characteristics.update(tech_characteristics)


                try:
                    description = 'Комплектация:\n\n' + '\n'.join(['- ' + i.text.strip() for i in soup.select_one('#tab-00').select('li')])
                except:
                    description = ''


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
                    'Компания': 'Просвар',
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
correct_path = os.path.join('23_06_2025', 'prosvar', 'prosvar.xlsx')

try:
    df.to_excel(correct_path, index=False)
except PermissionError:
    print("Файл занят. Закройте его.")
    time.sleep(10)  # Дать время на закрытие файла
    df = pd.read_excel(correct_path)  # Повторная попытка