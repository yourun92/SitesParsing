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
        self.cat_urls = ['https://hobbyka.ru/catalog/sadovaia_i_dachnaia_mebel/', 'https://hobbyka.ru/catalog/skameyki/', 'https://hobbyka.ru/catalog/urny/', 'https://hobbyka.ru/catalog/tsvetochnitsy_i_vazony_sadovoparkovye/', 'https://hobbyka.ru/catalog/velosipednye_parkovki/', 'https://hobbyka.ru/catalog/ulichnoe_i_sadovoparkovoe_osveshchenie/', 'https://hobbyka.ru/catalog/lezhaki_dlya_plyazha_i_dachi/', 'https://hobbyka.ru/catalog/kacheli_parkovye/', 'https://hobbyka.ru/catalog/pavilony_i_navesy/', 'https://hobbyka.ru/catalog/reshetki_vokrug_derevev/', 'https://hobbyka.ru/catalog/ulichnoe_sportivnoe_oborudovanie/', 'https://hobbyka.ru/catalog/mobilnye_i_statsionarnye_tribuny/', 'https://hobbyka.ru/catalog/detskoe_igrovoe_oborudovanie/', 'https://hobbyka.ru/catalog/trotuarnye_stolbiki/', 'https://hobbyka.ru/catalog/ulichnye_stendy_ukazateli_vyveski/', 'https://hobbyka.ru/catalog/mebel_dlya_ulichnykh_kafe_i_horeca/', 'https://hobbyka.ru/catalog/mangaly_barbekyu_i_aksessuary/', 'https://hobbyka.ru/catalog/chugunnye_balyasiny/', 'https://hobbyka.ru/catalog/beskarkasnaya_mebel/', 'https://hobbyka.ru/catalog/umnyy_gorod/', 'https://hobbyka.ru/catalog/konteynernye_ploshchadki_dlya_tbo/', 'https://hobbyka.ru/catalog/aksessuary/', 'https://hobbyka.ru/catalog/skameyki_dlya_razdevalok/', 'https://hobbyka.ru/catalog/gril_i_aksessuary/', 'https://hobbyka.ru/catalog/korziny_dlya_konditsionerov/', 'https://hobbyka.ru/catalog/mafy/', 'https://hobbyka.ru/catalog/mebel_dlya_terras_i_besedok/', 'https://hobbyka.ru/catalog/ulichnye_kukhni/']
        self.data = pd.DataFrame({})
        self.ind = 0
        self.product_urls = []
        self.ua = UserAgent()


    # def collect_all_pages(self):

    #     for cat_url in self.cat_urls:
    #         response = requests.get(url=cat_url)
    #         response.encoding = 'utf-8'
    #         soup = BeautifulSoup(response.text, 'xml')

    #         urls = ['https://irfix.ru/' + u.select_one('a').get('href') for u in soup.select_one('.strainer__body').select('.st')]

    #         self.product_urls.extend(urls)


    def parsing_products(self):

        # self.collect_all_pages()

        for url in self.cat_urls:
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

                url_prods = ['https://hobbyka.ru' + u.get('href') for u in soup.select('.cont_name_anchor')]
                # try:
                #     category = ' > '.join([u.text for u in soup.select_one('.breadcrumb__list.card__breadcrumb-list.--scroll').select('li')])
                # except:
                #     category = ''

                # try:
                #     image = 'https://irfix.ru' + soup.select_one('.zoom-img').get('src')
                # except:
                #     image = ''

                # try:
                #     title = soup.select_one('.card-title.card--name.title').text.strip()
                # except:
                #     title = ''

                articles = [u.text.split()[-1] for u in soup.select('.article_item_list')]


                # try:
                #     main_description = soup.select_one('.card__coll.card--bottom ').select('p')[1].text.strip()
                # except:
                #     main_description = ''

                prices = [u.select_one('div').get_text(strip=True, separator='$').split('$')[0] for u in soup.select('.item_prices_and_type')]

                # try:
                #     description = soup.select_one("#info-descrip").get_text(separator='\n')
                # except:
                #     description = ''

                # try:
                #     properties = {u.select('.info__tab-coll')[0].text.strip():u.select('.info__tab-coll')[1].text.strip() for u in soup.select_one("#characteristic").select('.info__tab-inner')}
                # except:
                #     properties = {}

                # Объединяем основные поля и свойства
                product_data = pd.DataFrame({
                    "URL": url_prods,
                    "Article": articles,
                    "Price": prices
                })

                self.data = pd.concat([self.data, product_data], ignore_index=True)

                # product_data.update(properties)
                if len(articles) != len(prices):
                    print(f'{url} - чет не то')

                # self.ind += 1
                # if self.ind % 100 == 0:
                #     print(f'Обработано {self.ind} страниц')

                # Случайная задержка между запросами
                time.sleep(random.uniform(1, 3))

                # # Сохраняем промежуточные результаты
                # if self.ind % 100 == 0:
                #     df = pd.DataFrame(self.data)
                #     df.to_excel(f"hobbyka_interim_{self.ind}.xlsx", index=False)


            except Exception as e:
                print(f"Ошибка при обработке {url}: {e}")
                continue





parser = Parser()
parser.parsing_products()



df = pd.DataFrame(parser.data)
df.to_excel('hobbyka.xlsx', index=False)







