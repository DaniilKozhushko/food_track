import psycopg2
import os
from dotenv import load_dotenv

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

# запрос на создание таблицы categories
cur.execute("""
CREATE TABLE IF NOT EXISTS categories (
    category_id SERIAL,
    name VARCHAR(23) UNIQUE NOT NULL,
    PRIMARY KEY (category_id)
);
""")

# запрос на создание таблицы sub_categories
cur.execute("""
CREATE TABLE IF NOT EXISTS sub_categories (
    sub_category_id SERIAL,
    sub_category_name VARCHAR(40) UNIQUE NOT NULL,
    PRIMARY KEY (sub_category_id)
);
""")

# запрос на создание таблицы categories_sub_categories
cur.execute("""
CREATE TABLE IF NOT EXISTS categories_sub_categories (
    category_id INT NOT NULL,
    sub_category_id INT NOT NULL,
    PRIMARY KEY (category_id, sub_category_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (sub_category_id) REFERENCES sub_categories(sub_category_id)
);
""")

# запрос на создание таблицы guest_types
cur.execute("""
CREATE TABLE IF NOT EXISTS guest_types (
    guest_type_id SERIAL,
    guest_type_name VARCHAR(5) UNIQUE NOT NULL,
    PRIMARY KEY (guest_type_id)
);
""")

# запрос на создание таблицы dishes
cur.execute("""
CREATE TABLE IF NOT EXISTS dishes(
    dish_id SERIAL,
    dish_name VARCHAR(200) UNIQUE NOT NULL,
    category_id INT NOT NULL,
    sub_category_id INT NOT NULL,
    price INT NOT NULL,
    PRIMARY KEY (dish_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (sub_category_id) REFERENCES sub_categories(sub_category_id)
);
""")

# запрос на создание таблицы orders
cur.execute("""
CREATE TABLE IF NOT EXISTS orders(
    order_id SERIAL,
    table_number INT NOT NULL,
    guest_index INT NOT NULL,
    guest_type_id INT NOT NULL,
    dish_id INT NOT NULL,
    order_time TIMESTAMP NOT NULL,
    PRIMARY KEY (order_id),
    FOREIGN KEY (guest_type_id) REFERENCES guest_types(guest_type_id),
    FOREIGN KEY (dish_id) REFERENCES dishes(dish_id)
);
""")

# подтверждаю создание таблиц, закрываю объект и соединение
conn.commit()
cur.close()
conn.close()