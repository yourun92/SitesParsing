import pandas as pd
import requests
import lxml
from bs4 import BeautifulSoup
import xml
import time
import random
from fake_useragent import UserAgent
import re

class Parser:
    def __init__(self):
        self.cat_urls = ['https://irfix.ru/pena-montazhnaya?posts=90', 'https://irfix.ru/germetiki?posts=90', 'https://irfix.ru/lenty?posts=90', 'https://irfix.ru/kley?posts=90', 'https://irfix.ru/khimicheskie-ankery?posts=90', 'https://irfix.ru/montazhnye-pistolety?posts=90', 'https://irfix.ru/ochistiteli-i-smazki?posts=90', 'https://irfix.ru/materialy-dlya-restavratsii?posts=90', 'https://irfix.ru/spetsialnye-produkty?posts=90']
        self.data = []
        self.ind = 0
        self.product_urls = []
        self.ua = UserAgent()
        
    
    def collect_all_pages(self):

        for cat_url in self.cat_urls:
            response = requests.get(url=cat_url)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'xml')

            urls = ['https://irfix.ru/' + u.select_one('a').get('href') for u in soup.select_one('.strainer__body').select('.st')]
            
            self.product_urls.extend(urls)


    def parsing_products(self):

        self.collect_all_pages()

        for url in self.product_urls:
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
                    category = ' > '.join([u.text for u in soup.select_one('.breadcrumb__list.card__breadcrumb-list.--scroll').select('li')])
                except:
                    category = ''
                
                try:
                    image = 'https://irfix.ru' + soup.select_one('.zoom-img').get('src')
                except:
                    image = ''

                try:
                    title = soup.select_one('.card-title.card--name.title').text.strip()
                except:
                    title = ''
                
                try:
                    article = soup.select_one('.card__swiper-title').text.strip()
                except:
                    article = ''
                
                try:
                    main_description = soup.select_one('.card__coll.card--bottom ').select('p')[1].text.strip()
                except:
                    main_description = ''
                
            #     # price = soup.select_one('.product__price')
            #     # price = price.text.strip() if price else ''
                
                try:
                    description = soup.select_one("#info-descrip").get_text(separator='\n')
                except:
                    description = ''
                
                try:
                    properties = {u.select('.info__tab-coll')[0].text.strip():u.select('.info__tab-coll')[1].text.strip() for u in soup.select_one("#characteristic").select('.info__tab-inner')}
                except:
                    properties = {}

                # Объединяем основные поля и свойства
                product_data = {
                    'url': url,
                    'category': category,
                    'image': image,
                    'title': title,
                    'article': article,
                    'main_description': main_description,
                    # 'price': price,
                    'description': description,
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
                    df.to_excel(f"irfix_interim_{self.ind}.xlsx", index=False)



            except Exception as e:
                print(f"Ошибка при обработке {url}: {e}")
                continue

            

   

parser = Parser()
parser.parsing_products()



df = pd.DataFrame(parser.data)
df.to_excel('irfix.xlsx', index=False)







