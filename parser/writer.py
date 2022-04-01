import psycopg2
import csv


# get info from db and write it to a file
def select():
    # connect to db and get data
    conn = psycopg2.connect(
        dbname='task', user='postgres', password='drder32167', host='localhost'
    )

    cursor = conn.cursor()

    query = 'SELECT * FROM users INNER JOIN cars ON car_id = users.user_id ORDER BY price NULLS FIRST'

    cursor.execute(query)

    data = cursor.fetchall()

    # write data to a file
    with open('countries.csv', 'w') as f:
        writer = csv.writer(f)

        for row in data:
            writer.writerow(row)


select()


