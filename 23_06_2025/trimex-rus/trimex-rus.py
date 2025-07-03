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

        product_urls = ['https://trimex-rus.ru/production/forestry/frame-scaffold.html', 'https://trimex-rus.ru/production/forestry/clamp-wood.html', 'https://trimex-rus.ru/production/forestry/flange.html', 'https://trimex-rus.ru/production/forestry/cup-type.html', 'https://trimex-rus.ru/production/forestry/frame-flooring.html', 'https://trimex-rus.ru/production/formwork/frame-tables.html', 'https://trimex-rus.ru/production/formwork/cup-type.html', 'https://trimex-rus.ru/production/formwork/flange-type.html', 'https://trimex-rus.ru/production/formwork/telescopic-racks-copy.html', 'https://trimex-rus.ru/production/wall/large.html', 'https://trimex-rus.ru/production/wall/small-panel.html', 'https://trimex-rus.ru/production/wall/girder-girder.html', 'https://trimex-rus.ru/production/formwork-round/round.html', 'https://trimex-rus.ru/production/formwork-round/oval.html', 'https://trimex-rus.ru/production/column-formwork/universal.html', 'https://trimex-rus.ru/production/column-formwork/girder-girder.html', 'https://trimex-rus.ru/production/towers/tura.html', 'https://trimex-rus.ru/production/towers/stairs.html', 'https://trimex-rus.ru/production/flooring/', 'https://trimex-rus.ru/production/container/', 'https://trimex-rus.ru/production/components/1.html', 'https://trimex-rus.ru/production/components/2.html', 'https://trimex-rus.ru/production/components/3.html', 'https://trimex-rus.ru/production/components/4.html', 'https://trimex-rus.ru/production/components/5.html', 'https://trimex-rus.ru/production/components/6.html', 'https://trimex-rus.ru/production/components/7.html', 'https://trimex-rus.ru/production/components/8.html', 'https://trimex-rus.ru/production/components/9.html', 'https://trimex-rus.ru/production/components/11.html', 'https://trimex-rus.ru/production/components/10.html', 'https://trimex-rus.ru/production/components/12.html', 'https://trimex-rus.ru/production/components/13.html', 'https://trimex-rus.ru/production/components/14.html', 'https://trimex-rus.ru/production/components/15.html', 'https://trimex-rus.ru/production/components/16.html', 'https://trimex-rus.ru/production/components/17.html', 'https://trimex-rus.ru/production/components/18.html', 'https://trimex-rus.ru/production/components/19.html', 'https://trimex-rus.ru/production/components/20.html', 'https://trimex-rus.ru/production/components/21.html', 'https://trimex-rus.ru/production/components/22.html']

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
                    title = soup.select_one('h1.border').text.strip()
                except:
                    title = ''

                try:
                    article = ''
                except:
                    article = ''


                try:
                    path = ''
                except:
                    path = ''

                try:
                    if 'forestry' in url:
                        category = 'Леса'
                    elif 'formwork' in url:
                        category = 'Опалубка перекрытий'
                    elif 'wall' in url:
                        category = 'Стеновая опалубка'
                    elif 'formwork-round' in url:
                        category = 'Опалубка круглых форм'
                    elif 'column-formwork' in url:
                        category = 'Опалубка колонн'
                    elif 'towers' in url:
                        category = 'Вышки'
                    elif 'flooring' in url:
                        category = 'Настил металлический'
                    elif 'container' in url:
                        category = 'Металлическая тара'
                    elif 'components' in url:
                        category = 'Комплектующие'

                except:
                    category = ''


                try:
                    availability = ''
                except:
                    availability = ''

                try:
                    images = ['https://trimex-rus.ru/production/' + url.split('/')[4] + '/' + i['src'] for i in soup.select_one('.images-slider__block').select('img')]
                    image = images[0]
                except:
                    image = ''

                try:
                    gallery = ' | '.join(images[1:])
                except:
                    gallery = ''

                try:
                    if 'components' in url:
                        main_description = soup.select_one('h1.border').find_next_sibling('p').text.strip()
                    else:
                        main_description = soup.select_one('#tab1').select_one('p').text.strip()
                except:
                    main_description = ''

                try:
                    description = '\n'.join([i.text for i in soup.select_one('#tab1').select('p')[1:]])
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

                try:
                    characteristics = {}
                    table = [i.select('td') for i in soup.select_one('.tab-content').select_one('table').select('tr')]
                    for t in table:
                        k = t[0].text.replace('-', '').replace('*', '').strip().capitalize()
                        v = t[-1].text.strip()
                        characteristics[k] = v


                except:
                    characteristics = {}
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
correct_path = os.path.join('23_06_2025', 'trimex-rus', 'trimex-rus.xlsx')

try:
    df.to_excel(correct_path, index=False)
except PermissionError:
    print("Файл занят. Закройте его.")
    time.sleep(10)  # Дать время на закрытие файла
    df = pd.read_excel(correct_path)  # Повторная попытка