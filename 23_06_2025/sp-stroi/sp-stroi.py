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
        self.url = 'https://sudizol.ru/sitemap.xml'
        self.data = []
        self.ind = 0
        self.ua = UserAgent()


    def get_soup(self, url):
        response = requests.get(url=url)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')
        return soup

    def collect_all_pages(self):
        product_urls = ['https://sp-stroi.ru/spanel_mineral_wool/', 'https://sp-stroi.ru/spanel_penopolistirol/', 'https://sp-stroi.ru/spanel_pir/', 'https://sp-stroi.ru/spanels_pur/', 'https://sp-stroi.ru/kpanel_mineral_wool/', 'https://sp-stroi.ru/kpanel_penopolistirol/', 'https://sp-stroi.ru/kpanel_pur/', 'https://sp-stroi.ru/kpanel_pir/']
        sdfsdf = 'https://sp-stroi.ru/fastener/'

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
                    title = soup.select_one('.w-separator-text').text
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
                    category = 'Сэндвич панели'
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
                    image = soup.select_one('.attachment-large.size-large').get('src')
                except:
                    image = ''

                try:
                    gallery = ''
                except:
                    gallery = ''

                try:
                    main_description = soup.select_one('.wpb_wrapper').text.strip()
                except:
                    main_description = ''

                try:
                    description = soup.select('.wpb_wrapper')[2].text.strip()
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
                    if soup.select_one('.characteristics'):
                        for tr in soup.select_one('.characteristics').select('tr')[1:]:
                            key = tr.select_one('td').text.strip()
                            value = []
                            for td in tr.select('td')[1:]:
                                if td.get('colspan'):
                                    ind = int(td['colspan'])
                                    value.extend([td.text] * ind)
                                else:
                                    value.extend([td.text])
                            characteristics[key] = value
                    else:
                        for tr in soup.select('.wpb_wrapper')[1].select_one('table').select('tr')[1:]:
                            key = tr.select_one('td').text.strip()
                            value = []
                            for td in tr.select('td')[1:]:
                                if td.get('colspan'):
                                    ind = int(td['colspan'])
                                    value.extend([td.text] * ind)
                                else:
                                    value.extend([td.text])
                            characteristics[key] = value


                except:
                    characteristics = {}
                # characteristics.update(tech_characteristics)


                # Объединяем основные поля и свойства
                for i in range(len(characteristics['Толщина панели, мм'])):
                    product_data = {
                        'Название': title + ' ' + characteristics['Толщина панели, мм'][i] + 'мм',
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
correct_path = os.path.join('23_06_2025', 'sp-stroi', 'sp-stroi.xlsx')

try:
    df.to_excel(correct_path, index=False)
except PermissionError:
    print("Файл занят. Закройте его.")
    time.sleep(10)  # Дать время на закрытие файла
    df = pd.read_excel(correct_path)  # Повторная попытка