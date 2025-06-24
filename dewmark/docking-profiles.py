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
        self.url = 'https://ecoblik.ru/sitemap.xml'
        self.data = []
        self.ind = 0
        self.ua = UserAgent()


    # def collect_all_pages(self):

    #     response = requests.get(url=self.url)
    #     response.encoding = 'utf-8'
    #     soup = BeautifulSoup(response.text, 'xml')

    #     urls = soup.find_all("loc")
    #     product_urls = [url.text for url in urls if (url.text.startswith("https://ecoblik.ru/catalog") or url.text.startswith("https://ecoblik.ru/po-tipam")) and not url.text.endswith('/')]

    #     return product_urls

    #sdg
    def parsing_products(self):

        # product_urls = self.collect_all_pages()

        product_urls = ['https://dewmark.ru/products/stadium/sv-164153/']
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
                    category = ' > '.join([i.strip() for i in soup.select_one('.bx-breadcrumb').text.strip().split('\n') if i.strip()])

                except:
                    category = ''

                try:
                    image = 'https://dewmark.ru/' + soup.select_one('.single_image')['href']
                except:
                    image = ''

                try:
                    plan_image = ' | '.join(['https://dewmark.ru/' + i['src'] for i in soup.find_all("img", alt=lambda x: x and x.startswith("профиль в разрезе"))])
                except:
                    plan_image = ''

                # try:
                #     material =
                # except:
                #     material =

                try:
                    title = soup.select_one('.col-xl-8').select_one('h1').text.strip()
                except:
                    title = ''
                # # article = soup.select_one('div.product__sku span.sku-value')

                try:
                    pdf = 'https://dewmark.ru/' + soup.select_one('.download-tbl').select_one('a')['href']
                except:
                    pdf = ''

                try:
                    photo = ' | '.join(['https://dewmark.ru/' + i['href'] for i in soup.select_one('.profile_photos').select('a')])
                except:
                    photo = ''
                try:
                    main_description = soup.select_one(".innter-t1.text-left").text.strip()
                except:
                    main_description = ''

                try:
                    plan = 'https://dewmark.ru/' + soup.select_one(".main-draw-inner").select_one('img')['src']
                except:
                    plan = ''

                # # price = soup.select_one('.product__price')
                # # price = price.text.strip() if price else ''

                # try:
                #     description = soup.select_one(".tovar_def").select('p')[-1].text.strip()
                # except:
                #     description = ''

                # try:
                #     properties = {k.text.strip():v.text.strip() for k,v in zip(soup.select('.prop_block_Line_cap'), soup.select('.prop_block_Line_val'))}
                # except:
                #     properties = {}

                # Объединяем основные поля и свойства
                # product_data = {
                #     'url': url,
                #     'category': category,
                #     'image': image,
                #     'title': title,
                #     # 'article': article,
                #     'main_description': main_description,
                #     # 'price': price,
                #     'description': description,
                # }

                # product_data.update(properties)
                # self.data.append(product_data)


                print(title)
                print()
                print(category)
                print()
                print(image)
                print()
                print(url)
                print()
                # print(plan_image)
                # print()
                print(pdf)
                print()
                print(photo)
                print()
                print(plan)
                print()
                print(main_description)
                print()


            except Exception as e:
                print(f"Ошибка при обработке {url}: {e}")
                continue





parser = Parser()
print(parser.parsing_products())


# df = pd.DataFrame(parser.data)
# df.to_excel('docking-profiles.xlsx', index=False)
