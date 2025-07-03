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
        self.url = 'https://ecoroom.ru/catalog/'
        self.data = []
        self.ind = 0
        self.ua = UserAgent()


    def get_soup(self, url):
        response = requests.get(url=url)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')
        return soup

    def collect_all_pages(self):
        cat_urls_all = []
        cat_urls = [i.select_one('ul') for i in self.get_soup(self.url).select_one('#side-nav').select('li') if i.select_one('ul')]
        for ul in cat_urls:
            cat_urls_all.extend([a['href'] for a in ul.select('a')])

        product_urls_with_articles = {}
        for cat_url in cat_urls_all[:-4]:
            print(cat_url)
            if self.get_soup(cat_url).select_one('#listgoods'):
                prod_urls_tag = [li.select_one('a[href^="https://ecoroom.ru/catalog/"]') for li in self.get_soup(cat_url).select_one('#listgoods').select('li')]

                for a in prod_urls_tag:
                    product_urls_with_articles[a['href']] = a.select_one('span').text.split(':')[-1].strip()

        return product_urls_with_articles


    def parsing_products(self):

        product_urls_with_articles = self.collect_all_pages()
        print(f'Всего товаров - {len(product_urls_with_articles)}')

        for url in product_urls_with_articles.keys():
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
                    article = product_urls_with_articles[url]
                except:
                    article = ''

                try:
                    path = ' > '.join([i.text.replace('/', '').strip() for i in soup.select_one('#breadcrumbs').select('li')][:-1])
                except:
                    path = ''


                try:
                    category = [i.text.replace('/', '').strip() for i in soup.select_one('#breadcrumbs').select('li')][1]
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
                    image = soup.select_one('.view').select_one('[alt="image"]').get('src')
                except:
                    image = ''

                try:
                    gallery = ''
                except:
                    gallery = ''

                try:

                    main_description = soup.select_one('#content').find('h2', string='Описание').find_next_sibling().text.strip()
                except:
                    main_description = ''


                try:
                    features = soup.select_one('.features').text.replace('Скачать техническое описание на продукт', '').strip()
                    advantages = 'Преимущества\n\n' + soup.select_one('#content').find('h2', string='Преимущества').find_next_sibling('ul').text.strip()
                    description = features + '\n\n' + advantages
                except:
                    description = ''


                # try:
                #     price = soup.select_one('.ProductContent_priceBlock_orig__CrQCy').text.strip()
                # except:
                #     price = ''

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
                #     for i in soup.select_one('[data-tab-content="characteristics"]').select('.productInfo__characteristics-wrapper'):
                #         key = i.select_one('.productInfo__title').text.strip()
                #         value = i.select_one('.productInfo__value').text.strip()
                #         characteristics[key] = value


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
                    # 'Цена': price,
                    'Доп описание': description,
                    # 'Доступность': availability
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
correct_path = os.path.join('23_06_2025', 'ecoroom', 'ecoroom.xlsx')

try:
    df.to_excel(correct_path, index=False)
except PermissionError:
    print("Файл занят. Закройте его.")
    time.sleep(10)  # Дать время на закрытие файла
    df = pd.read_excel(correct_path)  # Повторная попытка