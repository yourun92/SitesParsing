import pandas as pd
import requests
import lxml
from bs4 import BeautifulSoup
import xml
import time
import random
from fake_useragent import UserAgent
import os


class Parser:
    def __init__(self):
        self.data = []
        self.ind = 0
        self.ua = UserAgent()
        self.all_urls = [
            "https://bitumbrit.com/ru/catalog/tproduct/562148930-532203569921-germetik-brit-nord",
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-285147579521-germetik-brit-arktik-3',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-641467481541-germetik-brit-bp-g25',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-186440862821-germetik-brit-bp-g35',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-739736859821-germetik-brit-bp-g50',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-476536489691-mastika-brit-dsh-85',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-760592661191-mastika-brit-dsh-90',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-760745001521-mastika-brit-t-65',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-882181148281-mastika-brit-t-75',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-791096983951-mastika-brit-t-85',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-777617934511-mastika-brit-t-90',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-474953307631-lenta-brit-a-50h5',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-820019565991-lenta-brit-a-50h8',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-512575904901-lenta-brit-schma-50h7',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-126497523481-lenta-brit-aero-50h8',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-514432879831-lenta-zhidkaya-brit-flex',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-313606968531-shnur-brit-22-mm',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-856432338831-shnur-brit-20-mm',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-478384698611-rulonnii-material-brit-biznes-ekp',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-375265004551-rulonnii-material-brit-premium-ekp',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-725672083631-rulonnii-material-brit-premium-epp',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-574297413021-rulonnii-material-brit-standart-ekp',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-966875347731-rulonnii-material-brit-standart-epp',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-669682783321-gruntovka-polimernaya-brit',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-650775788411-propitka-brit-pp',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-366616149821-sostav-brit-zvs-v',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-965127705331-sostav-brit-zvs-r',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-555080885131-shnur-brit-10-mm',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-966338316301-shnur-brit-13-mm',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-240604842101-shnur-brit-15-mm',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-899650239991-shnur-brit-25-mm',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-210787280991-shnur-brit-32-mm',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-238275532261-shnur-brit-38-mm',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-300182462001-mastika-brit-zhidkaya-rezina-most',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-476437281231-mastika-brit-izolyatsiya-v',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-694446416951-mastika-brit-izolyatsiya-r',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-691841160571-mastika-brit-krovlya-v',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-451807738971-mastika-brit-krovlya-r',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-805137521411-mastika-brit-mb-50',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-420371577491-mastika-brit-mbk-g-55',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-931854106931-mastika-brit-mbk-g-65',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-240548436871-mastika-brit-mbk-g-75',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-177589097501-mastika-brit-mbr-65',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-531691012381-mastika-brit-mbr-75',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-397106780291-mastika-brit-mbr-90',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-672288233391-mastika-brit-mbr-100',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-788211777171-mastika-brit-torma-most',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-638432226021-praimer-brit-standart-r',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-706914304991-praimer-brit-konnekt-r',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-426442190311-bitum-bnd-5070-bnd-6090-bnd-70100-i-dr',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-496150764591-mastika-brit-zhidkaya-rezina',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-544325141411-germetik-poliuretanovii-izhora',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-703155044311-germetik-poliuretanovii-izhora-zimnii',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-993533297621-rulonnii-material-brit-biznes-epp',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-442850160811-rulonnii-material-brit-biznes-tpp',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-992637934401-rulonnii-material-brit-premium-tkp',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-959508527181-rulonnii-material-brit-standart-tpp',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-326215939651-rulonnii-material-brit-standart-tkp',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-584048855371-rulonnii-material-brit-premium-tpp',
            'https://bitumbrit.com/ru/catalog/tproduct/562148930-687698699401-rulonnii-material-brit-biznes-tkp']

    # def collect_all_pages(self):

    #     response = requests.get(url=self.url)
    #     response.encoding = 'utf-8'
    #     soup = BeautifulSoup(response.text, 'lxml')

    #     urls = soup.select_one('.js-store-prod-all-text').text
    #     product_urls = [u.find('a').get('href') for u in urls]

    #     return urls

    def parsing_products(self):

        product_urls = self.all_urls


        for url in product_urls:
            try:
                headers = {
                    'User-Agent': self.ua.random,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8',
                    'Connection': 'keep-alive'
                }

                response = requests.get(
                    url=url, headers=headers, timeout=30)
                response.encoding = 'utf-8'
                soup = BeautifulSoup(response.text, 'lxml')

                # try:
                #     category = ' > '.join(url.split('/')[-4:])[:-2]
                # except:
                #     category = ''

                try:
                    image = soup.select_one(
                        '.t-container').select_one('meta').get('content')
                except:
                    image = ''

                try:
                    title = soup.select_one('.js-store-prod-name').text.strip()
                except:
                    title = ''

                try:
                    article = soup.select_one(
                        '.t-store__prod-popup__sku').text.strip()
                except:
                    article = ''

                try:
                    main_description = soup.select_one(
                        '.js-store-prod-all-text').get_text(separator='\n').replace('Есть вопросы? Задайте их нашему менеджеру по телефону: ', '').replace('+7 (495) 145-93-26', '').strip()
                except:
                    main_description = ''

                # try:
                #     price = soup.select_one('.price_value').select_one(
                #         '#catalog_item_price_top').text.strip()
                # except:
                #     price = 'Цена по запросу'

                # try:
                #     description = soup.select(".woocommerce-product-details__short-description .table-box")[-1].select('td')[3].text
                # except:
                #     description = ''

                try:
                    properties = {k:v for k,v in zip([d.text.strip() for d in soup.select('.t-store__tabs__button-title.t-name.t-name_xs')], [d.get_text(separator='\n').strip() for d in soup.select('.t-store__tabs__content.t-descr.t-descr_xxs')])}
                    try:
                        properties['Документация'] = soup.select_one('figure').select_one('a').get('href')
                    except:
                        pass
                except:
                    properties = {}

                # Объединяем основные поля и свойства
                product_data = {
                    'url': url,
                    # 'category': category,
                    'Картинка': image,
                    'Название': title,
                    'Артикул': article,
                    'Главное описание': main_description,
                    # 'price': price,
                    # 'description': description,
                }

                product_data.update(properties)
                self.data.append(product_data)

            #     self.ind += 1
            #     if self.ind % 50 == 0:
            #         print(f'Обработано {self.ind} страниц')

                # Случайная задержка между запросами
                time.sleep(random.uniform(1, 3))

            #     # Сохраняем промежуточные результаты
            #     if self.ind % 200 == 0:
            #         df = pd.DataFrame(self.data)
            #         df.to_excel(
            #             f"hobbyka\\bd\\hobbyka_interim_{self.ind}.xlsx", index=False)

            except Exception as e:
                print(f"Ошибка при обработке {url}: {e}")
                continue


parser = Parser()
parser.parsing_products()

df = pd.DataFrame(parser.data)
df.to_excel('bitumbrit.xlsx', index=False)
