import psycopg2
import os
import sys
from dotenv import load_dotenv

# добавляю новый путь для поиска модулей
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data')))
from menus import menus

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

# запрос на вставку данных в таблицу categories
cur.execute("""
INSERT INTO guest_types (guest_type_name)
VALUES
    (%s),
    (%s),
    (%s);
""", ('man', 'woman', 'child'))

for category in menus:
    # запрос на вставку данных в таблицу categories
    cur.execute("""
    INSERT INTO categories (category_name)
    VALUES (%s)
    RETURNING category_id;
    """, (category,))

    # получение category_id из RETURNING
    cat_id = cur.fetchone()[0]

    for sub_category in menus[category]:
        # запрос на вставку данных в таблицу sub_categories
        cur.execute("""
        INSERT INTO sub_categories (sub_category_name)
        VALUES (%s)
        ON CONFLICT (sub_category_name) DO NOTHING;
        """, (sub_category,))

        # запрос на получение sub_category_id
        cur.execute("SELECT sub_category_id FROM sub_categories WHERE sub_category_name = %s", (sub_category,))
        sub_cat_id = cur.fetchone()[0]

        # запрос на вставку данных в таблицу categories_sub_categories
        cur.execute("""
        INSERT INTO categories_sub_categories (category_id, sub_category_id)
        VALUES (%s, %s);
        """, (cat_id, sub_cat_id))

        for dish, params in menus[category][sub_category].items():
            # запрос на вставку данных в таблицу dishes
            cur.execute("""
            INSERT INTO dishes (dish_name, category_id, sub_category_id, price)
            VALUES (%s, %s, %s, %s);
            """, (dish, cat_id, sub_cat_id, params[1]))

# подтверждаю наполнение таблиц, закрываю объект и соединение
conn.commit()
cur.close()
conn.close()