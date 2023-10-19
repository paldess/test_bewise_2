import time

from flask import Flask, request
import requests
import pymysql
from datetime import datetime

app = Flask(__name__)

def database_connect(sql):
    # подключение к базе данных MySQL
    # возвращает данные полученные от запроса
    connection = pymysql.connect(
        host='mysql_db',
        port=3306,
        user='root',
        password='523524',
        database='jservice',
        cursorclass=pymysql.cursors.DictCursor)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        connection.commit()
        out = cursor.fetchall()
    time.sleep(0.01)
    return out


@app.route('/testing', methods=['POST'])
def testing():
    accepted_value = request.get_json()['questions_num']
    data = requests.get('https://jservice.io/api/random', json={'count':f'{accepted_value}'})
    data = data.json()
    for i in data:
        while True:
            search = i["question"].replace("'", '"')
            sql = f"select question from main_table where question = '{search}';"
            out = database_connect(sql)
            if len(out) == 0:
                break
            i = requests.get('https://jservice.io/api/random', json={'count':'1'}).json()[0]

        date = i['created_at'].split('T')[0]
        date = datetime.strptime(date, '%Y-%m-%d').date()
        sql_last_search = 'UPDATE main_table SET last_search = 0;'
        database_connect(sql_last_search)
        sql_insert = (f"insert into main_table(id, question, answer, created_question, last_search) "
                      f"values({i['id']}, '{search}', '{i['answer']}', '{date}', True);")
        database_connect(sql_insert)
    sql_return = 'select question from main_table where last_search = 1;'
    return database_connect(sql_return)[0]['question']



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
