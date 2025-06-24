import pandas as pd
import requests
import lxml
from bs4 import BeautifulSoup
import xml
import time
import random
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

class Parser:
    def __init__(self):
        driver_options = webdriver.ChromeOptions()
        self.ua = UserAgent()
        driver_options.add_argument(f'user-agent={self.ua.random}')  # Устанавливаем User-Agent

        service = Service("C:/chromedriver-win64/chromedriver.exe")
        self.driver = webdriver.Chrome(service=service, options=driver_options)

        self.url = 'https://mangra.ru/catalog'
        self.data = []
        self.ind = 0


    def collect_all_pages(self):

        response = requests.get(url=self.url)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')
        all_pages = [i.get('href') for i in soup.select('.main_name')]

        return all_pages


    def parsing_products(self):
        product_urls = self.collect_all_pages()


        for url in product_urls:
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
                html = self.driver.page_source
                soup = BeautifulSoup(html, 'html.parser')

                try:
                    profile = soup.select_one('.col_title').text

                except:
                    profile = ''


                try:
                    path = ' > '.join(soup.select_one('.kama_breadcrumbs').text.split(' / ')).strip()

                except:
                    path = ''

                try:
                    category = soup.select_one('.simple_p').text
                except:
                    category = ''

                try:
                    category_room = soup.select_one('.simple_p_new.bigger_p').select_one('.allowed_loads').text
                except:
                    category_room = ''

                try:
                    load_intensity_all_cat = [[[l.text.strip() for l in k.select('td')] for k in i.select('tr')] for i in soup.select('.halfed.simple_p_new')]
                    load_intensity = {i[0]:i[1] for i in load_intensity_all_cat[0] + load_intensity_all_cat[1]}
                except:
                    load_intensity = {}

                try:
                    main_image = soup.select_one('.attachment-shop_single')['src']
                except:
                    main_image = ''

                try:
                    main_description = '\n'.join(f'- {line.strip()}' for line in soup.select_one(".bordered_box").get_text().splitlines() if line.strip())
                except:
                    main_description = ''

                try:
                    description = '\n'.join(['- ' + i.text.strip() for i in soup.select_one("#description").select('li')])
                except:
                    description = ''

                try:
                    for tr in soup.find_all("tr"):
                        first_td = tr.find("td")
                        if first_td and first_td.get_text(strip=True) == "Схема монтажа":
                            plan_image_all = tr.select('td')[-1]
                            plan_image = ' | '.join([m.text + ': ' + n for m, n in zip(plan_image_all.select('p'), [i.get('href') for i in plan_image_all.select('a')])])
                            break

                except:
                    plan_image = ''

                try:
                    explanation = soup.select_one('.explanation_table').get_text(separator=' ').strip()
                except:
                    explanation = ''

                try:
                    extra_information = soup.select_one('.extra_information').text.strip()
                except:
                    extra_information = ''

                try:
                    table = soup.select_one('.adaptive_table')
                    if not table:
                        raise ValueError("adaptive_table не найдена")

                    rows = table.select('tr')

                    # Заголовок — первая строка
                    header_cells = rows[0].select('.legendary_explain')
                    header = ['Профиль'] + [i.text.strip().capitalize() for i in header_cells]

                    main_info = {key: [] for key in header}

                    for row in rows[1:]:
                        tds = row.select('td')
                        # Пропускаем строку, если в ней меньше данных, чем в заголовке
                        if len(tds) < len(header):
                            continue

                        values = [td.get_text(strip=True) for td in tds]
                        for i, key in enumerate(header):
                            main_info[key].append(values[i])

                except Exception as e:
                    print(f"[ERROR] Ошибка при разборе adaptive_table: {e}")
                    main_info = None

                options = ''
                try:
                    target_tag = soup.select('tr')
                    for i in target_tag:
                        header = i.select_one('.h2.new_section_title')
                        if header and header.text.strip() in ['Варианты конструкций', 'Варианты вставок']:
                            a_tag = i.select_one('a[href]')  # ищем <a> со ссылкой внутри того же <tr>
                            if a_tag:
                                options = a_tag['href']
                                break
                except:
                    pass

                try:
                    corner_name = [i.text for i in soup.select_one('#modification').find_all('p', style=lambda value: value and value.strip().startswith('margin-left:'))]
                    corner_page = [k.select_one('a')['href'] for k in [i for i in soup.select_one('#modification').select('.images_eps')][:-1]]
                    corners = ' | '.join([k + ': ' + v for k,v in zip(corner_name, corner_page)])
                except:
                    corners = ''

                try:
                    pdf = soup.select_one('#downloads').select_one('a')['href']
                except:
                    pdf = ''


                try:
                    dwg = soup.select_one('#downloads').select('a')[1]['href']
                except:
                    dwg = ''

                # # # article = soup.select_one('div.product__sku span.sku-value')

                # try:
                #     photo = ' | '.join(['https://dewmark.ru/' + i['href'] for i in soup.select_one('.profile_photos').select('a')])
                # except:
                #     photo = ''


                # try:
                #     plan = 'https://dewmark.ru/' + soup.select_one(".main-draw-inner").select_one('img')['src']
                # except:
                #     plan = ''

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

                profiles = main_info['Профиль']  # список профилей

                all_products = []

                for i in range(len(profiles)):
                    extra_info = {k:v[i] for k,v in main_info.items()}


                    product_data = {
                        'Серия профилей': profile,
                        'Путь': path,
                        'Категория': category,
                        'Категория помещений': category_room,
                        'Картинка': main_image,
                        'Описание': main_description,
                        'Доп описание': description,
                        'Схема монтажа': plan_image,
                        'Обозначение в проектах': explanation,
                        'Характеристики': extra_information,
                        'Варианты вставок': options,
                        'Угловые модификации': corners,
                        'pdf файл': pdf,
                        'dwg файл': dwg,
                        'url': url
                    }

                    extra_info.update(load_intensity)
                    extra_info.update(product_data)
                    all_products.append(extra_info)




                self.data.extend(all_products)
                time.sleep(random.uniform(1, 3))




            except Exception as e:
                print(f"Ошибка при обработке {url}: {e}")
                continue





parser = Parser()
parser.parsing_products()

df = pd.DataFrame(parser.data)
df.to_excel('mangra.xlsx', index=False)
