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
        self.url = 'https://russdom.net/sitemap-shop.xml'
        self.data = []
        self.ind = 0
        self.ua = UserAgent()


    def collect_all_pages(self):

        response = requests.get(url=self.url)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'xml')

        product_urls = [i.text for i in soup.select('loc')]


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
                    meta_title = soup.select_one('meta[property="og:title"]').get('content')
                except:
                    meta_title = ''


                try:
                    title = soup.select_one('[name="keywords"]').get('content')
                except:
                    title = ''


                try:
                    article = soup.select_one('.sku__value').text.strip()
                except:
                    article = ''


                try:
                    path = ' > '.join([i.select_one('.breadcrumbs__link').get('title') for i in soup.select_one('.breadcrumbs__wrapper').select('.breadcrumbs') if i.select_one('.breadcrumbs__link')])
                except:
                    path = ''


                try:
                    category = [i.select_one('.breadcrumbs__link').get('title') for i in soup.select_one('.breadcrumbs__wrapper').select('.breadcrumbs') if i.select_one('.breadcrumbs__link')][1]
                except:
                    category = ''


                try:
                    availability = soup.select_one('.stocks__text').text.strip()
                except:
                    availability = ''

                try:
                    image = soup.select_one('meta[property="og:image"]')['content']
                except:
                    image = ''


                # try:
                #     gallery = ' | '.join([i['href'] for i in soup.select_one('.tovar_mini_gallery').select('[data-fancybox="gallery"]')])
                # except:
                #     gallery = ''


                try:
                    main_description = soup.select_one('#s-product-desc').text.strip()

                except:
                    main_description = ''


                try:
                    price = 'Под заказ'
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


                # characteristics.update(tech_characteristics)


                # try:
                #     description = soup.select_one('[aria-labelledby="vert_tab_item-3"]')
                # except:
                #     description = ''


                try:

                    table = soup.select_one('#s-product-desc').select_one('table')
                    if table and table.select_one('tr').select_one('td').text.strip() == 'Модель':
                        keys = [i.text.strip().split(',')[0].strip() for i in table.select_one('tr').select('td')]
                        for values in [k.select('td') for k in table.select('tr')[1:]]:
                            characteristics = {k:v.text.strip() for k,v in zip(keys, values)}
                            # Объединяем основные поля и свойства
                            product_data = {
                                'Название': title + ' ' + characteristics.get('Модель', '').strip(),
                                'url': url,
                                'meta_description': meta_description,
                                'meta_title': meta_title,
                                'Артикул': article,
                                'Категория': category,
                                'Путь': path,
                                'Картинка': image,
                                # 'Галерея': gallery,
                                'Описание': main_description,
                                'Цена': price,
                                # 'Доп описание': description,
                                'Доступность': availability
                            }
                            product_data.update(characteristics)
                            self.data.append(product_data)
                            self.ind += 1


                    else:
                        characteristics = {}
                        for i in soup.select_one('.features__wrapper').select('.features__item'):
                            key = i.select_one('.features__code').text.strip()
                            value = i.select_one('.features__value').text.strip()
                            characteristics[key] = value

                        product_data = {
                                'Название': title + ' ' + characteristics.get('Модель', '').strip(),
                                'url': url,
                                'meta_description': meta_description,
                                'meta_title': meta_title,
                                'Артикул': article,
                                'Категория': category,
                                'Путь': path,
                                'Картинка': image,
                                # 'Галерея': gallery,
                                'Описание': main_description,
                                # 'Цена': price,
                                # 'Доп описание': description,
                                'Доступность': availability
                            }
                        product_data.update(characteristics)
                        self.data.append(product_data)
                        self.ind += 1



                except:
                    characteristics = {}

                if not characteristics:
                    product_data = {
                                'Название': title,
                                'url': url,
                                'meta_description': meta_description,
                                'meta_title': meta_title,
                                'Артикул': article,
                                'Категория': category,
                                'Путь': path,
                                'Картинка': image,
                                # 'Галерея': gallery,
                                'Описание': main_description,
                                # 'Цена': price,
                                # 'Доп описание': description,
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
correct_path = os.path.join('23_06_2025', 'russdom', 'russdom.xlsx')

try:
    df.to_excel(correct_path, index=False)
except PermissionError:
    print("Файл занят. Закройте его.")
    time.sleep(10)  # Дать время на закрытие файла
    df = pd.read_excel(correct_path)  # Повторная попытка