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
        self.url = 'https://xn----7sbb7btkedf.xn--p1ai/product-sitemap.xml'
        self.data = []
        self.ind = 0
        self.ua = UserAgent()


    def collect_all_pages(self):

        response = requests.get(url=self.url)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'xml')

        product_urls = [i.find('loc').text for i in soup.find_all('url')[1:]]


        return product_urls


    def parsing_products(self):

        product_urls = self.collect_all_pages()


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
        #         try:
        #             path = ' > '.join(url.split('/')[-4:])[:-2]
        #         except:
        #             path = ''

        #         try:
        #             category = soup.select_one('meta[property="product:category"]')['content']
        #         except:
        #             category = ''

        #         try:
        #             availability = soup.select_one('meta[property="product:availability"]')['content']
        #         except:
        #             availability = ''


                try:
                    image = soup.select_one('meta[property="og:image"]')['content']
                except:
                    image = ''



                try:
                    title = soup.select_one('meta[property="og:title"]')['content'].replace('- АСТ-Пласт', '').strip()
                except:
                    title = ''



                try:
                    article_ = [i.text for i in soup.select_one('#additional_information').select(f'[align="left"]')]
                    article = [a for a in article_ if a.startswith('АРТИКУЛ')][0].split('\r\n')[0].split(':')[-1].strip()
                except:
                    article = ''



                try:
                    main_description = [a for a in article_ if not a.startswith('АРТИКУЛ') and not a == '\xa0'][0]
                except:
                    main_description = ''


        #         try:
        #             price = soup.select_one('meta[property="product:price:amount"]')['content']
        #         except:
        #             price = ''

        #         try:
        #             description = soup.select(".woocommerce-product-details__short-description .table-box")[-1].select('td')[3].text
        #         except:
        #             description = ''

                try:
                    properties = {k.strip():v.strip() for k,v in [i.split(':') for i in [a for a in article_ if a.startswith('АРТИКУЛ')][0].split('\r\n')[1:]]}
                except:
                    properties = {}

                # try:
                #     images = ''
                # except:
                #     images = ''


                # Объединяем основные поля и свойства
                product_data = {
                    'Название': title,
                    'url': url,
                    # 'Путь': path,
                    # 'Категория': category,
                    'Картинка': image,
                    'Артикул': article,
                    'Описание': main_description,

                    # 'Цена': price,
                    # 'Доп описание': description,
                    # 'Доступность': availability
                }

                product_data.update(properties)
                self.data.append(product_data)

                self.ind += 1
                if self.ind % 25 == 0:
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
correct_path = os.path.join('23_06_2025', 'ast_plast', 'ast_plast.xlsx')

try:
    df.to_excel(correct_path, index=False)
except PermissionError:
    print("Файл занят. Закройте его.")
    time.sleep(10)  # Дать время на закрытие файла
    df = pd.read_excel(correct_path)  # Повторная попытка