import psycopg2
import csv
import sys


# get info from db and write it to a file
def select():
    # connect to db and get data
    try:
        conn = psycopg2.connect(
            dbname='task', user='postgres', password='drder32167', host='localhost'
        )
    except psycopg2.OperationalError as er:
        print(er)
        sys.exit(1)

    cursor = conn.cursor()

    query = 'SELECT * FROM users INNER JOIN offers ON offer_id = users.user_id ORDER BY price NULLS FIRST'

    cursor.execute(query)

    data = cursor.fetchall()

    # write data to a file
    with open('countries.csv', 'w') as f:
        writer = csv.writer(f)

        for row in data:
            writer.writerow(row)


select()


