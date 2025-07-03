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
        options = Options()
        options.add_argument("--headless=new")  # Объединяем все опции в один объект
        ua = UserAgent()
        options.add_argument(f'user-agent={ua.random}')  # Добавляем User-Agent в options

        service = Service("C:/chromedriver-win64/chromedriver.exe")
        driver = webdriver.Chrome(service=service, options=options)  # Используем единый объект options

        try:
            driver.get(url)
            html = driver.page_source
            return BeautifulSoup(html, 'html.parser')
        finally:
            driver.quit()

    def collect_all_pages(self):
        cat_urls = ['https://fastengroup.ru/catalog/krovelnyy-krepezh/', 'https://fastengroup.ru/catalog/fasadnyy-krepezh-evofast/', 'https://fastengroup.ru/catalog/krepezhnye-elementy/', 'https://fastengroup.ru/catalog/voronki-i-aeratory/', 'https://fastengroup.ru/catalog/shayby/', 'https://fastengroup.ru/catalog/planki/', 'https://fastengroup.ru/catalog/prochee/']
        cat_sub_urls = []
        for u in cat_urls:
            cats_sub_soup = self.get_soup(u)
            cat_sub_urls.extend(['https://fastengroup.ru' + i['href'] for i in cats_sub_soup.select_one('.category__wrapper').select('a')])

        products_urls = []
        for u in cat_sub_urls:
            products_soup = self.get_soup(u)
            if products_soup.select_one('.table-wrap'):
                products_urls.extend(['https://fastengroup.ru' + i.select_one('a')['href'] for i in products_soup.select_one('.table-wrap').select('tr')[1:]])
            else:
                products_urls.append(u)

        return products_urls


    def parsing_products(self):
        correct_path = os.path.join('23_06_2025', 'fastengroup', 'fastengroup.csv')
        product_urls = pd.read_csv(correct_path, sep=',')

        print(f'Всего товаров - {len(product_urls)}')

        for url in product_urls['url']:
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
                    article = ''
                except:
                    article = ''

                try:
                    path = ' > '.join([i.text.strip() for i in soup.select_one('.breadcrumbs.breadcrumbs--outside').select('li')][:-1])
                except:
                    path = ''

                try:
                    category = [i.text.strip() for i in soup.select_one('.breadcrumbs.breadcrumbs--outside').select('li')][:-1][2]
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
                    image = 'https://fastengroup.ru' + soup.select_one('.swiper-wrapper').select_one('picture').select_one('img').get('src')
                except:
                    image = ''

                try:
                    gallery = ' | '.join('https://fastengroup.ru' + i.select_one('img').get('src') for i in soup.select_one('.swiper-wrapper').select('picture')[1:])
                except:
                    gallery = ''

                try:
                    main_description = soup.select_one('.productInfo__wrapper').text.strip()
                except:
                    main_description = ''

                try:
                    description = soup.select('.productInfo__wrapper')[1].text.strip()
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

                try:
                    characteristics = {}
                    for i in soup.select_one('[data-tab-content="characteristics"]').select('.productInfo__characteristics-wrapper'):
                        key = i.select_one('.productInfo__title').text.strip()
                        value = i.select_one('.productInfo__value').text.strip()
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
                    # 'Цена': price,
                    'Доп описание': description,
                    # 'Доступность': availability
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
correct_path = os.path.join('23_06_2025', 'fastengroup', 'fastengroup.xlsx')

try:
    df.to_excel(correct_path, index=False)
except PermissionError:
    print("Файл занят. Закройте его.")
    time.sleep(10)  # Дать время на закрытие файла
    df = pd.read_excel(correct_path)  # Повторная попытка