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
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Parser:
    def __init__(self):
        driver_options = webdriver.ChromeOptions()
        self.ua = UserAgent()
        driver_options.add_argument(f'user-agent={self.ua.random}')  # Устанавливаем User-Agent

        service = Service("C:/chromedriver-win64/chromedriver.exe")
        self.driver = webdriver.Chrome(service=service, options=driver_options)
        self.url = 'https://diodex.ru/sitemap-iblock-24.xml'
        self.data = []
        self.ind = 0
        self.ua = UserAgent()


    def collect_all_pages(self):

        response = requests.get(url=self.url)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'xml')

        product_urls = [i.find('loc').text for i in soup.find_all('url') if 'product' in i.find('loc').text]


        return product_urls


    def parsing_products(self):

        product_urls = self.collect_all_pages()

        print(f'Всего товаров - {len(product_urls)}')
        for url in ['https://diodex.ru/catalog/product/vizum-duo-u-80vt/']:

            try:
                # headers = {
                #     'User-Agent': self.ua.random,
                #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                #     'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8',
                #     'Connection': 'keep-alive'
                # }

                # response = requests.get(url=url, headers=headers, timeout=30)
                # response.encoding = 'utf-8'
                # soup = BeautifulSoup(response.text, 'lxml')
                self.driver.get(url)
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".card__product-heading"))
                )
                html = self.driver.page_source
                soup = BeautifulSoup(html, 'lxml')
                url = url

                try:
                    meta_description = soup
                except:
                    meta_description = ''

                return meta_description

                try:
                    meta_title = soup.select_one('meta[property="og:title"]').get('content')
                except:
                    meta_title = ''

                try:
                    title = soup.select_one('.item_card_product h1').text.strip()
                except:
                    title = ''

                try:
                    article = soup.select_one('.manufacturer__box.test333').select_one('div[itemprop="sku"]').text.split(':')[-1].strip()
                except:
                    article = ''


                try:
                    path = ' > '.join([i.text.strip() for i in soup.select_one('.breadcrumbs').select('span') if i.text.strip()])
                except:
                    path = ''

                try:
                    category = soup.select_one('.active._active').select_one('a').text.strip()
                except:
                    category = ''


        #         try:
        #             availability = soup.select_one('meta[property="product:availability"]')['content']
        #         except:
        #             availability = ''


                try:
                    image = soup.select_one('.wrp_fly_image').get('src')
                except:
                    image = ''


                try:
                    gallery = ' | '.join([i['href'] for i in soup.select_one('.tovar_mini_gallery').select('[data-fancybox="gallery"]')])
                except:
                    gallery = ''


                try:
                    main_description = soup.select_one('.info-block.info-block2').text.strip()
                except:
                    main_description = ''

                try:
                    _price = soup.select_one('.wholesale.wholesale2')
                    if _price.select_one('.wholesale-price._oldprice'):
                        price = _price.select_one('.product_old_price.product_old_price2').text.replace('₽', '').strip()
                    else:
                        price = _price.select_one('#price').get('data-value').split('.')[0]
                except:
                    price = ''

                try:
                    tech_characteristics = {}
                    for i in soup.select_one('.table.table_desc').select_one('tbody').select('tr'):
                        tds = i.select('td')
                        key = tds[0].text
                        value = tds[1].text
                        measure = tds[2].text
                        tech_characteristics[key] = value + ' ' + measure

                except:
                    tech_characteristics = {}


                try:
                    characteristics = {}
                    for i in soup.select_one('.char_list').select('tr'):
                        key_elem = i.select_one('.char_row_cap')
                        val_elem = i.select_one('.char_row_values')
                        if key_elem and val_elem:
                            key = key_elem.text.strip()
                            value = val_elem.text.strip()
                            characteristics[key] = value

                except:
                    characteristics = {}

                characteristics.update(tech_characteristics)


                # try:
                #     description = soup.select_one('[aria-labelledby="vert_tab_item-3"]')
                # except:
                #     description = ''



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
                    # 'Доп описание': description,
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
print(parser.parsing_products())


# df = pd.DataFrame(parser.data)
# correct_path = os.path.join('23_06_2025', 'ant_snab', 'ant_snab.xlsx')

# try:
#     df.to_excel(correct_path, index=False)
# except PermissionError:
#     print("Файл занят. Закройте его.")
#     time.sleep(10)  # Дать время на закрытие файла
#     df = pd.read_excel(correct_path)  # Повторная попытка