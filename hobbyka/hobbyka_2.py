import pandas as pd
import requests
import lxml
from bs4 import BeautifulSoup
import xml
import time
import random
from fake_useragent import UserAgent
import os

# 'https://hobbyka.ru/product/skameyka_ulichnaya_litsey/' глянуть
class Parser:
    def __init__(self):
        self.data = []
        self.ind = 0
        self.ua = UserAgent()
        self.url = 'https://hobbyka.ru/sitemappart_products.xml'


    def collect_all_pages(self):

        response = requests.get(url=self.url)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'xml')

        urls = soup.find_all('loc')
        product_urls = [u.text for u in urls]

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
                # try:
                #     category = ' > '.join(url.split('/')[-4:])[:-2]
                # except:
                #     category = ''

                # try:
                #     image = soup.select_one('.woocommerce-product-gallery__image a').get('href')
                # except:
                #     image = ''

                # try:
                #     title = soup.select_one('.product_title.entry-title.elementor-heading-title.elementor-size-default').text.strip()
                # except:
                #     title = ''

                try:
                    article = soup.select_one('.element_article').text.split(':')[-1].strip()
                except:
                    article = ''

                # try:
                #     main_description = '\n\n'.join([desc.text for desc in soup.select_one(".woocommerce-product-details__short-description").select('p, h5')][:-2])
                # except:
                #     main_description = ''

                try:
                    price = soup.select_one('.price_value').select_one('#catalog_item_price_top').text.strip()
                except:
                    price = 'Цена по запросу'

                # try:
                #     description = soup.select(".woocommerce-product-details__short-description .table-box")[-1].select('td')[3].text
                # except:
                #     description = ''

                # try:
                #     properties = {i.split(':')[0].strip():i.split(':')[1].strip() for i in soup.select(".woocommerce-product-details__short-description .table-box")[-1].select('td')[2].text.split('\n')}
                # except:
                #     properties = {}

                # Объединяем основные поля и свойства
                product_data = {
                    'url': url,
                    # 'category': category,
                    # 'image': image,
                    # 'title': title,
                    'article': article,
                    # 'main_description': main_description,
                    'price': price,
                    # 'description': description,
                }

            #     # product_data.update(properties)
                self.data.append(product_data)

                self.ind += 1
                if self.ind % 50 == 0:
                    print(f'Обработано {self.ind} страниц')

                # Случайная задержка между запросами
                time.sleep(random.uniform(1, 3))

                # Сохраняем промежуточные результаты
                if self.ind % 200 == 0:
                    df = pd.DataFrame(self.data)
                    df.to_excel(f"hobbyka\\bd\\hobbyka_interim_{self.ind}.xlsx", index=False)


            except Exception as e:
                print(f"Ошибка при обработке {url}: {e}")
                continue





parser = Parser()
parser.parsing_products()


df = pd.DataFrame(parser.data)
df.to_excel('hobbyka\\hobbyka_2.xlsx', index=False)
