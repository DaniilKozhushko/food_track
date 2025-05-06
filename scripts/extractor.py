import csv
import psycopg2
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta as td

load_dotenv()

# получаю из окружения переменные
db_name = os.getenv("POSTGRES_DB")
db_user = os.getenv("POSTGRES_USER")
db_password = os.getenv("POSTGRES_PASSWORD")
db_host = os.getenv("POSTGRES_HOST", "localhost")

# устанавливаю соединение
conn = psycopg2.connect(
    dbname = db_name,
    user = db_user,
    password = db_password,
    host = db_host,
    port = "5432"
)

# создаю курсор
cur = conn.cursor()
# получаю текущее положение файла, перемещаюсь на уровень вверх, в папку data, в папку orders
# и из этой папки беру файл с названием, в котором присутствует вчерашнее число
abs_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
folder = os.path.join(abs_folder, 'data', 'orders')
filename = os.path.join(folder, (datetime.today().date() - td(days=1)).strftime('orders_%d_%m_%y.csv'))

with open(filename, 'r', encoding='utf-8') as file:
    orders = csv.DictReader(file, delimiter='\t')
    for order in orders:
        full_timestamp = f"{datetime.today().date() - td(days=1)} {order['timestamp']}"
        cur.execute("""
            INSERT INTO orders (table_number, guest_index, guest_type_id, dish_id, order_time)
            VALUES (%s, %s,
                (SELECT guest_type_id FROM guest_types WHERE guest_type_name = %s),
                    %s, %s);
            """, (order['table'], order['guest_number'], order['guest_type'], order['dish'], full_timestamp)
                    )

# подтверждаю создание таблиц, закрываю объект и соединение
conn.commit()
cur.close()
conn.close()