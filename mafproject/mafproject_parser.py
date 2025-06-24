import pandas as pd
import requests
import lxml
from bs4 import BeautifulSoup
import xml
import time
import random
from fake_useragent import UserAgent

class Parser:
    def __init__(self):
        self.url = 'https://mafproject.ru/sitemap-product.xml'
        self.data = []
        self.ind = 0
        self.ua = UserAgent()


    def collect_all_pages(self):

        response = requests.get(url=self.url)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'xml')

        urls = soup.find_all('loc')
        product_urls = [u for u in [url.text for url in urls] if u.endswith('/')]


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
                try:
                    path = ' > '.join(url.split('/')[-4:])[:-2]
                except:
                    path = ''

                try:
                    category = soup.select_one('meta[property="product:category"]')['content']
                except:
                    category = ''

                try:
                    availability = soup.select_one('meta[property="product:availability"]')['content']
                except:
                    availability = ''


                try:
                    image = soup.select_one('.woocommerce-product-gallery__image a').get('href')
                except:
                    image = ''

                try:
                    title = soup.select_one('.product_title.entry-title.elementor-heading-title.elementor-size-default').text.strip()
                except:
                    title = ''

                try:
                    article = soup.select('.elementor-heading-title.elementor-size-default')[1].text.strip()
                except:
                    article = ''

                try:
                    main_description = soup.select_one('meta[name="description"]')['content'].strip()
                except:
                    main_description = ''

                try:
                    price = soup.select_one('meta[property="product:price:amount"]')['content']
                except:
                    price = ''

                try:
                    description = soup.select(".woocommerce-product-details__short-description .table-box")[-1].select('td')[3].text
                except:
                    description = ''

                try:
                    properties = {i.split(':')[0].strip():i.split(':')[1].strip() for i in soup.select(".woocommerce-product-details__short-description .table-box")[-1].select('td')[2].text.split('\n')}
                except:
                    properties = {}

                # Объединяем основные поля и свойства
                product_data = {
                    'Название': title,
                    'url': url,
                    'Путь': path,
                    'Категория': category,
                    'Картинка': image,
                    'Артикул': article,
                    'Описание': main_description,
                    'Цена': price,
                    'Доп описание': description,
                    'Доступность': availability
                }

                product_data.update(properties)
                self.data.append(product_data)

                self.ind += 1
                if self.ind % 100 == 0:
                    print(f'Обработано {self.ind} страниц')

                # Случайная задержка между запросами
                time.sleep(random.uniform(1, 3))

                # Сохраняем промежуточные результаты
                if self.ind % 100 == 0:
                    df = pd.DataFrame(self.data)
                    df.to_excel(f"mafproject_interim_{self.ind}.xlsx", index=False)



            except Exception as e:
                print(f"Ошибка при обработке {url}: {e}")
                continue





parser = Parser()
print(parser.parsing_products())


df = pd.DataFrame(parser.data)
df.to_excel('mafproject.xlsx', index=False)
