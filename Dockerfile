# базовый образ питона
FROM python:3.13-slim

# рабочая папка внутри контейнера
WORKDIR /app

# копирую зависимости (библиотеки и модули для питона)
COPY requirements.txt .

# устанавливаю зависимости
# RUN - запускается на этапе сборки контейнера
# устанавливаются все сборки из requirements.txt 
# --no-cache-dir - не хранит временные файлы
# -r - читает файл
RUN pip install --no-cache-dir -r requirements.txt

# копирую весь проект
COPY . .

# запускаю python и generator.py, когда запускается контейнер
CMD ["python", "generator.py"]