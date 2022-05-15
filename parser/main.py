import requests
from bs4 import BeautifulSoup
import psycopg2
import sys

# url for parsing
URL = input()

# name of browser
HEADERS = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36',
           'accept': '*/*'}


# create beautiful soup object
def b_soup(link=URL, params=None, **kwargs):
    try:
        page = requests.get(link, headers=HEADERS, params=params)
    except (requests.exceptions.MissingSchema, requests.exceptions.InvalidSchema):
        print('Your link is not correctly. Try another link...')
    else:
        soup = BeautifulSoup(page.content, "html.parser")
        return soup


# get name of seller
def page_parser(link):
    results = b_soup(link=link).find("div", class_="css-z88e9u")
    name = results.find("h2", class_="css-u8mbra-Text").get_text()

    return name


# get all current pages for parsing
def page_count(*args, **kwargs):
    try:
        pages_count_html = b_soup(URL).find_all("span", class_="item fleft")
    except (TypeError, AttributeError):
        pass
    else:
        pages_count = pages_count_html[-1].find_next('span').get_text()

        for page in range(1, int(pages_count) + 1):
            parser(page={'page': page})
            print('{} of {} is already parsed.'.format(page, pages_count))


# write parsed info to db
def db_manager(data_list):
    print('i start to write data to a db')
    # connect to db
    try:
        conn = psycopg2.connect(
            dbname='task', user='postgres', password='drder32167', host='localhost'
        )
    except psycopg2.OperationalError as er:
        print(er)
        sys.exit(1)

    conn.autocommit = True
    cursor = conn.cursor()

    # get parsed info from dict
    for data in data_list:
        insert_user = [
            (data['name'])
        ]

        insert_offer = [
            (data['offer']['title']),
            (data['offer']['city']),
            (data['offer']['link']),
            (data['offer']['price']),

        ]

        # insert info to db
        insert_u = 'INSERT INTO users (user_name) VALUES (%s)'
        insert_c = 'INSERT INTO offers (title, city, link, price) VALUES (%s, %s, %s, %s)'

        cursor.execute(insert_u, insert_user)
        cursor.execute(insert_c, insert_offer)

    cursor.close()
    conn.close()


# get info from cards in current page
def parser(page, **kwargs):
    results = b_soup(URL, params=page).find(id="offers_table")
    job_elements = results.find_all("tr", class_="wrap")

    users = []

    for el in job_elements:
        link = el.find("td", class_="title-cell").find_next('a').get('href')

        name = page_parser(link)

        users.append({'name': name, 'offer': {'title': el.find("a", class_="marginright5").find_next('strong').get_text(),
                                            'price': el.find("td", class_="wwnormal").find_next('strong').get_text(),
                                            'city': el.find("td", class_="bottom-cell").find_next('span').get_text(),
                                            'link': el.find("td", class_="title-cell").find_next('a').get('href'),
                                            }})

    db_manager(users)


page_count()
