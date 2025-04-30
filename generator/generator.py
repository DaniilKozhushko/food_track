import os
import csv
import requests
import sys
from re import fullmatch
from random import choice, choices
from datetime import datetime, timedelta as td
from time import sleep
from dotenv import load_dotenv

# 0. Входные данные:____________________________________________________________________________________________________

# добавляю новый путь для поиска модулей
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data')))
from menus import menus

# Шансы для внесения погрешности:
chance_1 = choice([0.96, 0.97, 0.98, 0.99, 1.01, 1.03, 1.05, 1.07, 1.08, 1.09])

# Возможные "типы" гостей:
guest_types = ['child', 'man', 'woman']

# Шансы для "типов" гостей:
guest_type_chance = [2, 58, 40]

# Возможные заказы в зависимости от "типа" гостя:
sets = {'child': (['ДЕСЕРТЫ', 'НАПИТКИ'],
                  ['САЛАТЫ', 'НАПИТКИ'],
                  ['СУПЫ', 'САЛАТЫ', 'НАПИТКИ'],
                  ['ГОРЯЧИЕ БЛЮДА', 'ГАРНИРЫ', 'НАПИТКИ']),
        'man': (['ПРЕМИАЛЬНЫЕ СТЕЙКИ (Зерновой откорм)', 'ГАРНИРЫ', 'bar'],
                ['АЛЬТЕРНАТИВНЫЕ СТЕЙКИ', 'ГАРНИРЫ', 'bar'],
                ['БУРГЕР', 'ГАРНИРЫ', 'bar'],
                ['ГОРЯЧИЕ ЗАКУСКИ', 'СУПЫ', 'bar'],
                ['РУССКИЕ СТЕЙКИ СУХОГО ВЫЗРЕВАНИЯ 28 ДНЕЙ', 'ГАРНИРЫ', 'wine'],
                ['ПРЕМИАЛЬНЫЕ СТЕЙКИ (Травяной откорм)', 'ГАРНИРЫ', 'wine'],
                ['ХОЛОДНЫЕ ЗАКУСКИ', 'СУПЫ', 'bar'],
                ['РЫБА И МОРЕПРОДУКТЫ', 'ГАРНИРЫ', 'bar'],
                ['ТОЛЬКО В "СТРОГАНОВ"', 'ГАРНИРЫ', 'bar'],
                ['БУРГЕР', 'БЕЗАЛКОГОЛЬНЫЕ НАПИТКИ'],
                ['АЛЬТЕРНАТИВНЫЕ СТЕЙКИ', 'ГАРНИРЫ', 'РАЗЛИВНОЕ ПИВО (300 мл)'],
                ['РУССКИЕ СТЕЙКИ СУХОГО ВЫЗРЕВАНИЯ 28 ДНЕЙ', 'ЗАКУСКИ К ВОДКЕ', 'РОССИЙСКАЯ ВОДКА (40 мл)'],
                ['ПРЕМИАЛЬНЫЕ СТЕЙКИ (Зерновой откорм)', 'ГОРЯЧИЕ ЗАКУСКИ', 'bar'],
                ['БУРГЕР', 'БЕЗАЛКОГОЛЬНЫЕ НАПИТКИ', 'ГАРНИРЫ'],
                ['ГОРЯЧИЕ ЗАКУСКИ', 'АРМАНЬЯК (40 мл)', 'САЛАТЫ'],
                ['СУПЫ', 'ДЕЛИКАТЕСЫ "СТРОГАНОВ"', 'ПОЛУГАР, ХЛЕБНОЕ ВИНО (40 мл)'],
                ['РЫБА И МОРЕПРОДУКТЫ', 'ГОРЯЧИЕ ЗАКУСКИ', 'СМЕШАННЫЙ ВИСКИ'],
                ['ТОЛЬКО В "СТРОГАНОВ"', 'ЗАКУСКИ К ВОДКЕ', 'ЗАРУБЕЖНАЯ ВОДКА (40 мл)', 'РОССИЙСКАЯ ВОДКА (40 мл)'],
                ['ПРЕМИАЛЬНЫЕ СТЕЙКИ (Травяной откорм)', 'ГАРНИРЫ', 'bar'],
                ['АЛЬТЕРНАТИВНЫЕ СТЕЙКИ', 'САЛАТЫ', 'РОМ (40 мл)'],),
        'woman': (['САЛАТЫ', 'wine'],
                  ['РЫБА И МОРЕПРОДУКТЫ', 'ГАРНИРЫ', 'wine'],
                  ['СУПЫ', 'ГОРЯЧИЕ ЗАКУСКИ', 'wine'],
                  ['ТОЛЬКО В "СТРОГАНОВ"', 'ГАРНИРЫ', 'АПЕРИТИВЫ'],
                  ['ДЕСЕРТЫ', 'ГОРЯЧИЕ НАПИТКИ'],
                  ['ДЕСЕРТЫ', 'wine'],
                  ['ГОРЯЧИЕ ЗАКУСКИ', 'wine'],
                  ['САЛАТЫ', 'ГОРЯЧИЕ НАПИТКИ'],
                  ['РЫБА И МОРЕПРОДУКТЫ', 'ГАРНИРЫ', 'wine'],
                  ['АПЕРИТИВЫ', 'АПЕРИТИВЫ'],
                  ['АПЕРИТИВЫ', 'КОКТЕЙЛИ'],
                  ['КОКТЕЙЛИ', 'КОКТЕЙЛИ'],
                  ['САЛАТЫ', 'ГОРЯЧИЕ ЗАКУСКИ', 'wine'],
                  ['СУПЫ', 'САЛАТЫ', 'desserts_and_hot_drinks'],
                  ['РЫБА И МОРЕПРОДУКТЫ', 'МИНЕРАЛЬНАЯ ВОДА', 'desserts_and_hot_drinks'],
                  ['КОКТЕЙЛИ', 'БЕЗАЛКОГОЛЬНЫЕ НАПИТКИ'],
                  ['САЛАТЫ', 'ВИНА БОКАЛАМИ (150 мл)', 'ДЕСЕРТЫ'],
                  ['ГАРНИРЫ', 'ГОРЯЧИЕ НАПИТКИ', 'ГОРЯЧИЕ ЗАКУСКИ', 'wine'],
                  ['РЫБА И МОРЕПРОДУКТЫ', 'wine', 'САЛАТЫ'],
                  ['ХОЛОДНЫЕ ЗАКУСКИ', 'АПЕРИТИВЫ', 'desserts_and_hot_drinks'],
                  ['АЛЬТЕРНАТИВНЫЕ СТЕЙКИ', 'КОКТЕЙЛИ'],
                  ['ДЕЛИКАТЕСЫ "СТРОГАНОВ"', 'САЛАТЫ', 'wine'],)}

# Функция, возвращающая случайное блюдо, в зависимости от выбранной гостем категории и от "типа" гостя
def return_random_dish(category, guest):
    """returns a random dish or drink from the given category"""
    if guest == 'child':
        check = menus['kids'].get(category)
        if check:
            return choice(list(menus['kids'][category].items()))
    if category in menus:
        all_dishes = []
        for section in menus[category].values():
            all_dishes.extend(section.items())
        return choice(all_dishes)
    else:
        for section in menus.values():
            if category in section:
                return choice(list(section[category].items()))

# Функция, возвращающая количество секунд, необходимое для задержки генерации новых заказов
# для имитации реального потока гостей в зависимости от дня недели и времени
def return_guest_delay(amount_guests_today, total_guests_today):
    """returns the delay for guests to arrive"""
    delay = 0
    today = datetime.now() # 2025-04-15 20:36:01.002619
    week_day = today.isoweekday() # день недели от 1 до 7
    guest_waves = {1: {(12, 0): 17.5, (14, 0): 17.5, (16, 0): 5, (17, 30): 27.5, (20, 30): 23, (23, 0): 9.5, (23, 59): 0},
                   2: {(12, 0): 17.5, (14, 0): 17.5, (16, 0): 5, (17, 30): 27.5, (20, 30): 23, (23, 0): 9.5, (23, 59): 0},
                   3: {(12, 0): 17.5, (14, 0): 17.5, (16, 0): 5, (17, 30): 27.5, (20, 30): 23, (23, 0): 9.5, (23, 59): 0},
                   4: {(12, 0): 17.5, (14, 0): 17.5, (16, 0): 5, (17, 30): 27.5, (20, 30): 23, (23, 0): 9.5, (23, 59): 0},
                   5: {(12, 0): 17.5, (14, 0): 17.5, (16, 0): 5, (17, 30): 27.5, (20, 30): 23, (23, 0): 9.5, (23, 59): 0},
                   6: {(12, 0): 25, (17, 0): 20, (19, 0): 20, (21, 0): 20, (23, 0): 15, (23, 59): 0},
                   7: {(12, 0): 25, (17, 0): 20, (19, 0): 20, (21, 0): 20, (23, 0): 15, (23, 59): 0}
                   } # например: во Вторник с 16:00 до 17%=:30 будет 5% гостей от общего количества
    td_time = td(hours=today.hour, minutes=today.minute, seconds=today.second) # текущее время (timedelta)
    curr_week_day = list(guest_waves[week_day].items()) # [((12, 0), 35), ((16, 0), 5), ((17, 30), 60), ((23, 59), 0)]
    prev_periods_guest_counter = 0
    for i in range(len(curr_week_day) - 1):
        curr_period = td(hours=curr_week_day[i][0][0], minutes=curr_week_day[i][0][1])
        next_period = td(hours=curr_week_day[i+1][0][0], minutes=curr_week_day[i+1][0][1])
        if next_period > td_time >= curr_period:
            left_seconds_this_period = (next_period - td_time).seconds
            expected_guests = int(amount_guests_today / 100 *  curr_week_day[i][1]) # сколько гостей ожидается за текущий период
            guests_during_this_period = expected_guests - (total_guests_today - prev_periods_guest_counter) # сколько гостей осталось за этот период
            if guests_during_this_period > 0:
                delay = left_seconds_this_period / guests_during_this_period
            else:
                delay = (next_period - td_time).seconds
            break
        else:
            prev_periods_guest_counter += amount_guests_today / 100 *  curr_week_day[i][1]
    return delay

# 1. Генерация количества гостей за день:_______________________________________________________________________________

# Возможное количество гостей:
guests = [200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 950]

# Шансы в зависимости от дня недели:
week_days = {
    'Monday': [1, 1, 1, 20, 30, 20, 10, 6, 3, 2, 1, 1, 1, 1, 1, 1],
    'Tuesday': [1, 1, 1, 20, 30, 20, 10, 6, 3, 2, 1, 1, 1, 1, 1, 1],
    'Wednesday': [1, 1, 1, 1, 1, 1, 20, 30, 20, 10, 6, 3, 2, 1, 1, 1],
    'Thursday': [1, 1, 1, 1, 1, 1, 1, 1, 1, 20, 30, 20, 10, 6, 3, 2],
    'Friday': [1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 3, 6, 10, 30, 30, 10],
    'Saturday': [1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 3, 6, 10, 30, 30, 10],
    'Sunday': [1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 3, 6, 10, 30, 30, 10]}

# Текущий день недели:
week_day = datetime.today().strftime('%A')

# Генерация количества гостей за день:
amount_guests_today = round(choices(guests, weights=week_days[week_day], k=1)[0] * chance_1)

# 2. Влияние погодных условий на количество гостей:_____________________________________________________________________
try:
    # Получение города:
    response = requests.get('http://ip-api.com/json/', timeout=20)
    response.raise_for_status() # проверяю, что код ответа 200 (успех), иначе - ошибка
    data = response.json() # преобразую ответ сервера в json
    city = data.get('city', 'Tbilisi') # беру из ответа город (иначе - Tbilisi)

    # Получение погоды:
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')) # загружаю переменные из .env в память (в переменные окружения)
    api_key = os.getenv("API_KEY") # получаю из окружения переменную API_KEY
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    response = requests.get(url, timeout=20)
    response.raise_for_status()  # проверяю, что код ответа 200 (успех), иначе - ошибка
    data = response.json() # преобразую ответ сервера в json
    weather_id = data['weather'][0]['id'] # например: 520
except Exception:
    weather_id = 800

# Изменение количества гостей в зависимости от погоды:
ids = {'2': 0.64, '3': 0.93, '5': 0.87, '6': 0.98, '7': 0.12, '8': 1.17}
# ... где 2 - гроза, 3 - морось, 5 - дождь, 6 - снег, 7 - атмосферные явления (от тумана до торнадо), 8 - чистое небо
for idx in ids:
    if fullmatch(fr'{idx}\d\d', str(weather_id)):
        amount_guests_today *= ids[idx]

# 3. Генерация количества гостей за столом и скрипт создания заказов:___________________________________________________

# Возможные варианты:
table = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

# Вероятности для количества гостей за столом:
table_chance = [5, 45, 10, 9, 8, 7, 3, 3, 3, 3, 2, 2]

# Счётчик итогового количества гостей:
total_guests_today = 0

# Папка для сохранения файлов:
# получаю текущее положение файла, перемещаюсь на уровень вверх, в папку data, в папку orders
abs_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
folder = os.path.join(abs_folder, 'data', 'orders')
filename = os.path.join(folder, datetime.strftime(datetime.now(), 'orders_%d_%m_%y.csv'))
# файлы в формате "orders_DD_MM_YY.csv" где DD MM YY - день запуска скрипта

# Создание и запись в файл:
with open(filename, 'w', encoding='utf-8', newline='') as file:
    writer = csv.writer(file, delimiter='\t') # создание записывающего объекта
    writer.writerow(['table', 'guest_number', 'guest_type', 'dish', 'timestamp']) # запись заголовков таблицы
    orders = 0 # счётчик столов, также нумерация в таблице
    while total_guests_today < amount_guests_today:
        orders += 1
        order = [orders]
        guests_at_the_table = choices(table, weights=table_chance, k=1)[0] # генерация количества гостей за столом
        total_guests_today += guests_at_the_table # отслеживание текущего количества гостей, чтобы не превышало плановое
        max_children = guests_at_the_table // 2 # количество детей не должно превышать 50%
        children_count = 0 # счётчик детей за столом
        guest_counter = 0  # для идентификации гостя за столом
        for _ in range(guests_at_the_table): # генерация "типов" гостей за столом
            guest = choices(guest_types, weights=guest_type_chance, k=1)[0] # man? woman? child?
            if guest == 'child': # проверка количества детей
                children_count += 1
                if children_count > max_children:
                    guest = choice(['man', 'woman']) # количество детей не должно превышать 50%
            guest_counter += 1
            order.append(guest_counter)
            order.append(guest)
            for category in choice(sets[guest]): # каждый гость заказывает несколько блюд
                dish = return_random_dish(category, guest)
                order.append(dish[1][0]) # из кортежа ('название блюда', (id, цена)) беру только id
                order.append(datetime.now().strftime('%H:%M:%S.%f')) # добавляю timestamp
                writer.writerow(order) # записываю строку в файл
                # например: [245, 3, 'man', 240, 14:40:35.174336]
                # где 245 - номер стола, 3 - номер гостя за столом, 'man' - "тип" гостя, 240 - заказанное блюдо и timestamp
                del order[-2:] # удаляю timestamp и блюдо
            del order[-2:] # удаляю "тип" гостя и его id
        sleep(return_guest_delay(amount_guests_today, total_guests_today))