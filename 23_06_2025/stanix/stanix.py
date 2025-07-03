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
        self.url = 'https://stanix.ru/sitemap-catalog.xml'
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
            if u.select_one('changefreq'):
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
                    title = soup.select_one('h1[itemprop="name"]').text.strip()
                except:
                    title = ''

                try:
                    article = ''
                except:
                    article = ''

                try:
                    path = ' > '.join([i.select_one('a')['title'] for i in soup.select_one('.uk-breadcrumb.uk-margin-top.lh-1').select('li')])
                except:
                    path = ''

                try:
                    category = [i.select_one('a')['title'] for i in soup.select_one('.uk-breadcrumb.uk-margin-top.lh-1').select('li')][2]
                except:
                    category = ''

                try:
                    availability = soup.select_one('.fw-prod-status-line__avalability').text.strip()
                except:
                    availability = ''

                try:
                    image = soup.select_one('meta[property="og:image"]')['content']
                except:
                    image = ''


                try:
                    gallery = ' | '.join(['https://stanix.ru/' + i.select_one('img')['src'] for i in soup.select_one('.fw-prod-slideshow__add').select('li')])
                except:
                    gallery = ''


                try:

                    if soup.select_one('.tab-body.fw-tab-body.fw-content').select_one('h2'):
                        first_h2 = soup.select_one('.tab-body.fw-tab-body.fw-content').select_one('h2')

                        # Собираем все элементы после него до следующего h2
                        content = []
                        next_element = first_h2.next_sibling

                        while next_element and next_element.name != 'h2':
                            if next_element.name:  # если это тег (а не просто текст)
                                content.append(next_element.get_text(separator=' ', strip=True))
                            next_element = next_element.next_sibling

                        main_description = " ".join(content)
                    else:
                        main_description = soup.select_one('.tab-body.fw-tab-body.fw-content').text.strip()

                except:
                    main_description = ''

                try:
                    description = soup.select_one('.tab-body.fw-tab-body.fw-content').get_text().strip()
                except:
                    description = ''


                try:
                    price = soup.select_one('#price_value').text.strip()
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
                    for i in soup.select_one('.main-prod-props').select('.fw-property-item'):
                        key = i.select_one('.fw-property-name').text.strip()
                        value = i.select_one('.fw-property-values').text.strip()
                        characteristics[key] = value

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
correct_path = os.path.join('23_06_2025', 'stanix', 'stanix.xlsx')

try:
    df.to_excel(correct_path, index=False)
except PermissionError:
    print("Файл занят. Закройте его.")
    time.sleep(10)  # Дать время на закрытие файла
    df = pd.read_excel(correct_path)  # Повторная попытка