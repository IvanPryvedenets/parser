import requests
from bs4 import BeautifulSoup
import psycopg2

# url for parsing
URL = "https://www.olx.ua/uk/list/q-2121/"

# name of browser
HEADERS = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36',
           'accept': '*/*'}


# create beautiful soup object
def b_soup(link=URL, params=None, **kwargs):
    page = requests.get(link, headers=HEADERS, params=params)
    soup = BeautifulSoup(page.content, "html.parser")

    return soup


# get name of seller
def page_parser(link):
    results = b_soup(link=link).find("div", class_="css-1dp6pbg")
    name = results.find("h2", class_="css-u8mbra-Text").get_text()

    return name


# get all current pages for parsing
def page_count(*args, **kwargs):
    pages_count_html = b_soup(URL).find_all("span", class_="item fleft")
    pages_count = pages_count_html[-1].find_next('span').get_text()

    for page in range(1, int(pages_count) + 1):
        parser(page={'page': page})
        print('{} of {} is already parsed.'.format(page, pages_count))


# write parsed info to db
def db_manager(data_list):
    print('i start to write a data to a db')
    # connect to db
    conn = psycopg2.connect(
        dbname='task', user='postgres', password='drder32167', host='localhost'
    )
    conn.autocommit = True
    cursor = conn.cursor()

    # get parsed info from dict
    for data in data_list:
        insert_user = [
            (data['name'])
        ]

        insert_car = [
            (data['car']['title']),
            (data['car']['city']),
            (data['car']['link']),
            (data['car']['price']),

        ]

        # insert info to db
        insert_u = 'INSERT INTO users (user_name) VALUES (%s)'
        insert_c = 'INSERT INTO cars (title, city, link, price) VALUES (%s, %s, %s, %s)'

        cursor.execute(insert_u, insert_user)
        cursor.execute(insert_c, insert_car)

    cursor.close()
    conn.close()


# get info from cards in current page
def parser(page, **kwargs):
    results = b_soup(URL, params=page).find(id="offers_table")
    job_elements = results.find_all("tr", class_="wrap")

    users = []

    for el in job_elements:
        if el.find("a", class_="marginright5").find_next('small').get_text().strip() == 'Легкові автомобілі » ВАЗ':
            link = el.find("td", class_="title-cell").find_next('a').get('href')

            name = page_parser(link)

            users.append({'name': name, 'car': {'title': el.find("a", class_="marginright5").find_next('strong').get_text(),
                                                'price': el.find("td", class_="wwnormal").find_next('strong').get_text(),
                                                'city': el.find("td", class_="bottom-cell").find_next('span').get_text(),
                                                'link': el.find("td", class_="title-cell").find_next('a').get('href'),
                                                }})

    db_manager(users)


page_count()
