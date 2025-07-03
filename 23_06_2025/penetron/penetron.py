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
        self.url = 'https://www.silplast.ru/sitemap.xml'
        self.data = []
        self.ind = 0
        self.ua = UserAgent()


    def collect_all_pages(self):

        response = requests.get(url=self.url)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'xml')

        product_urls = ['https://penetron.ru/sistema-penetron/penetron', 'https://penetron.ru/sistema-penetron/penekrit', 'https://penetron.ru/sistema-penetron/peneplug', 'https://penetron.ru/sistema-penetron/vaterplag', 'https://penetron.ru/sistema-penetron/admix', 'https://penetron.ru/sistema-penetron/penebar', 'https://penetron.ru/remontnie-sostavi/skrepa-m500', 'https://penetron.ru/remontnie-sostavi/skrepa-m600-inektsionnaya', 'https://penetron.ru/remontnie-sostavi/skrepa-m700-konstruktsionnaya', 'https://penetron.ru/remontnie-sostavi/skrepa-finishnaya', 'https://penetron.ru/remontnie-sostavi/skrepa-samonivelir', 'https://penetron.ru/remontnie-sostavi/skrepa-2k-elastichnaya', 'https://penetron.ru/remontnie-sostavi/skrepa-zimnyaya', 'https://penetron.ru/inektsionnie-sostavi/penesplitsil', 'https://penetron.ru/inektsionnie-sostavi/penepurfom', 'https://penetron.ru/inektsionnie-sostavi/penepurfom-1k', 'https://penetron.ru/inektsionnie-sostavi/penepurfom-65', 'https://penetron.ru/germetizatsiya-deformatsionnih-shvov/peneband-s', 'https://penetron.ru/germetizatsiya-deformatsionnih-shvov/penepoksi-2k', 'https://penetron.ru/germetizatsiya-deformatsionnih-shvov/peneband', 'https://penetron.ru/germetizatsiya-deformatsionnih-shvov/penepoksi', 'https://penetron.ru/oborudovanie-dlya-raboti-s-materialami/ruchnoy-porshnevoy-nasos-ndm-20', 'https://penetron.ru/oborudovanie-dlya-raboti-s-materialami/ndm-40-elektricheskiy-shnekoviy-nasos', 'https://penetron.ru/oborudovanie-dlya-raboti-s-materialami/ek-100m-ruchnoy-porshnevoy-nasos', 'https://penetron.ru/oborudovanie-dlya-raboti-s-materialami/ek-200-porshnevoy-nasos-visokogo-davleniya-s-elektroprivodom']

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
                    title = soup.select_one('h1.page_tit').text.strip()
                except:
                    title = ''

                try:
                    article = ''
                except:
                    article = ''


                try:
                    path = ' > '.join([i.text.strip() for i in soup.select_one('.breadcrumbs').select('a')][:-1])
                except:
                    path = ''


                try:
                    category = [i.text.strip() for i in soup.select_one('.breadcrumbs').select('a')][1]
                except:
                    category = ''

                try:
                    availability = ''
                except:
                    availability = ''

                try:
                    image = soup.select_one('.product__img')['src']
                except:
                    image = ''

                try:
                    gallery = ''
                except:
                    gallery = ''

                try:

                    main_description = soup.select_one('.openuptext__inn.js-hide_container__inn').text.strip()
                except:
                    main_description = ''

                try:
                    description = ''.join([i.text for i in soup.select('.ilist__item')][1:])
                except:
                    description = ''


                try:
                    price = ''
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
                #     table = [i.select('td') for i in soup.select_one('.tab-content').select_one('table').select('tr')]
                #     for t in table:
                #         k = t[0].text.replace('-', '').replace('*', '').strip().capitalize()
                #         v = t[-1].text.strip()
                #         characteristics[k] = v


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
correct_path = os.path.join('23_06_2025', 'penetron', 'penetron.xlsx')

try:
    df.to_excel(correct_path, index=False)
except PermissionError:
    print("Файл занят. Закройте его.")
    time.sleep(10)  # Дать время на закрытие файла
    df = pd.read_excel(correct_path)  # Повторная попытка