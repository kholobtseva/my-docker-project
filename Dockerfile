# My Python Script for Singapore Exchange
# Automatically built with GitHub Actions CI/CD
FROM python:3.9

# Устанавливаем зависимости для PostgreSQL и ODBC
RUN apt-get update && apt-get install -y \
    postgresql-client \
    unixodbc \
    unixodbc-dev \
    odbc-postgresql

WORKDIR /app

# Копируем и устанавливаем Python-зависимости
COPY requirements.txt .
RUN pip install -r requirements.txt

# Копируем все файлы
COPY . .

# Даем скрипту права на выполнение
RUN chmod +x app/main.py

# Ждем запуска БД и запускаем скрипт
# CMD ["sh", "-c", "sleep 30 && python app/main.py"]
CMD ["sleep", "infinity"]