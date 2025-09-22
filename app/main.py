import logging
import sys
import os
import time
from datetime import timezone
import requests
import json
import psycopg2  # Меняем pyodbc на psycopg2
import csv
from datetime import datetime, timedelta, date
from dateutil.relativedelta import *
from elasticsearch import Elasticsearch

es = Elasticsearch(['http://elasticsearch:9200'])

def send_to_elasticsearch(data, index_name):
    try:
        es.index(index=index_name, body=data)
        logger.info(f"Data sent to Elasticsearch index: {index_name}")
    except Exception as e:
        logger.error(f"Error sending to Elasticsearch: {e}")

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


# Настройки подключения к БД из переменных окружения
DB_CONFIG = {
    "host": "postgres",      # имя контейнера с PostgreSQL
    "database": "my_db",
    "user": "user",
    "password": "password",
    "port": "5432"
}

def append_to_csv(data, filename):
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for entry in data:
            writer.writerow([entry['name'], entry['daily-settlement-price-abs'], entry['total-volume'], entry['formatted_date']])

def to_log_file(str_to_log, flag_print=False):
    if(flag_print):
        print(str_to_log)
    path = "/app/logs"
    if os.path.exists(path) is False:
        os.mkdir(path)
    file_name = path + "/log_ore_futures" + str(date.today()) + ".txt"
    with open(file_name, 'a', encoding='utf-8') as file:
        file.write(str_to_log)

def get_data_json(url, i):
    global health_status
    data = []
    try:
        response = requests.get(url)
        data1 = json.loads(response.text)
        for n in data1['data']:
            date_obj = datetime.strptime(n['base-date'], "%Y%m%d")
            formatted_date = date_obj.strftime("%Y-%m-%d")
            data.append({'name': i,
                'daily-settlement-price-abs': n['daily-settlement-price-abs'],
                'total-volume': n['total-volume'],
                'formatted_date': formatted_date
            })
    except requests.exceptions.RequestException as er:
        #print('Network error:', er)
        logger.error('Network error: %s', er)
        health_status = 0
        to_log_file('\nNetwork error!\n')
        set_status_robot(1012, health_status, '')
    except ValueError as err:
        #print('\nError:', err)
        logger.error('ValueError: %s', err)
        health_status = 0
        to_log_file('\nNo data available for the requested date\n')
    return data

def insert_record_if_not_exists():
    try:
        # Подключение к базе данных через psycopg2
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        for name in name_list:
            # Поиск записи с данным именем
            cursor.execute("SELECT id FROM public.www_data_idx WHERE name_eng = %s AND source = 'ore_futures'", (name,))
            record = cursor.fetchone()

            if record is None:  # Если запись не найдена, вставляем новую запись
                cursor.execute("SELECT MAX(id) FROM public.www_data_idx")
                max_id = cursor.fetchone()[0]

                if max_id is None:
                    max_id = 0

                new_id = max_id + 1
                current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Вставка новой записи
                cursor.execute("INSERT INTO public.www_data_idx (id, mask, name_rus, name_eng, source, url, descr, date_upd) VALUES (%s, NULL, 'Железная руда 62% Fe', %s, 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, %s)",
                               (new_id, name, current_date))
                logger.info("Запись была успешно добавлена")

        conn.commit()

    except (Exception, psycopg2.Error) as error:
        #print("Ошибка при работе с PostgreSQL", error)
        logger.error("Ошибка при работе с PostgreSQL: %s", error)

    finally:
        # Закрываем соединение с базой данных
        if conn:
            cursor.close()
            conn.close()
            #print("Соединение с PostgreSQL закрыто")
            logger.info("Соединение с PostgreSQL закрыто")

class SetInformation():
    @staticmethod
    def set(cursor, id_value, data):  # SECID,TRADEDATE,LOW,HIGH,CLOSE,VOLUME

        to_log_file(f"\n{data[0]} | {data[1]} | {data[4]} | {data[5]}", True)

        sql_query = """INSERT INTO public.agriculture_moex(id_value, date_val, min_val, max_val, avg_val, volume, currency, date_upd)
                    VALUES(%s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        now()) 
                    ON CONFLICT(id_value, date_val) DO UPDATE 
                    SET min_val = EXCLUDED.min_val, 
                        max_val = EXCLUDED.max_val, 
                        avg_val = EXCLUDED.avg_val, 
                        volume = EXCLUDED.volume, 
                        currency = EXCLUDED.currency, 
                        date_upd = now()"""

        cursor.execute(sql_query, (
            id_value,
            data[1],
            data[2] if data[2] is not None else None,
            data[3] if data[3] is not None else None,
            data[4] if data[4] is not None else None,
            data[5] if data[5] is not None else None,
            data[6] if data[6] is not None else None
        ))

def set_status_robot(id, health_status, add_text):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        query = "UPDATE public.health_monitor SET date_upd = now(), health_status = %s, add_text = %s WHERE id = %s"
        cursor.execute(query, (health_status, add_text, id))
        conn.commit()

    except psycopg2.DatabaseError as e:
        print("Error at execute:")
        #print(query)
        logger.error("Error at execute query: %s", query)
        #print(e)
        logger.error("Database error: %s", e)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_current_date():
    
     # UTC+3 (Московское время)
    current_time = datetime.now(timezone.utc) + timedelta(hours=3)
    return current_time.strftime("%Y-%m-%d %H:%M:%S MSK") + '\n'
    #return str(datetime.fromtimestamp(int(time.time()))) + '\n'
    
    
def sync_to_elasticsearch():
    """Автоматическая синхронизация данных с Elasticsearch"""
    try:
        
        import psycopg2
        
        logger.info("Начинаем синхронизацию с Elasticsearch...")
        
       
        # Подключение к PostgreSQL
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Выбираем данные из таблицы
        cursor.execute("""
            SELECT am.id_value, am.date_val, am.avg_val, am.volume, am.currency,
                   wdi.name_eng, wdi.name_rus
            FROM agriculture_moex am
            JOIN www_data_idx wdi ON am.id_value = wdi.id
        """)
        
        synced_count = 0
        for row in cursor.fetchall():
            doc = {
                'id_value': row[0],
                'date': row[1].isoformat(),
                'price': float(row[2]) if row[2] else None,
                'volume': float(row[3]) if row[3] else None,
                'currency': row[4],
                'contract': row[5],
                'name_rus': row[6],
                'source': 'moex_sgx',
                'sync_timestamp': datetime.now().isoformat()
            }
            
            # Отправляем в Elasticsearch
            es.index(index='agriculture-data', document=doc)
            synced_count += 1
        
        logger.info(f"Синхронизация завершена! Обработано записей: {synced_count}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Ошибка синхронизации с Elasticsearch: {e}")

# Основной код
interval  = '1w' #'3y'
health_status = 100

name_list = []
current_date = datetime.now() - timedelta(days=1)
dict_month = ["F", "G", "H", "J", "K", "M", "N", "Q", "U", "V", "X", "Z"]
for i in range(0, 37):
    next_date = current_date + relativedelta(months=i)
    name_list.append(f"FEF{dict_month[next_date.month-1]}{str(next_date.year)[-2:]}")
insert_record_if_not_exists()

print(name_list)
print(len(name_list))

try:
    to_log_file("\n\n\nSTART RUN SCRIPT\n", True)
    to_log_file(get_current_date(), True)

    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    to_log_file("\nConnect to DB PostgreSQL:  YES!!!\n", True)

    cursor.execute("SELECT id, name_eng, url FROM public.www_data_idx where source='ore_futures'")
    rows = cursor.fetchall()
    data = []

    for row in rows:
        if row[1] in name_list:  # row[1] = name_eng
            url = f"https://api.sgx.com/derivatives/v1.0/history/symbol/{row[1]}?days={interval}&category=futures&params=base-date%2Cbase-date%2Ctotal-volume%2Cdaily-settlement-price-abs"
            print("\n-----\n" + url + "\n")
            to_log_file("\n-----\n" + url + "\n")

            try:
                data1 = get_data_json(url, row[1])
                for i in data1:
                    data.append(row[0])  # row[0] = id
                    data.append(i['formatted_date'])
                    data.append(None)
                    data.append(None)
                    data.append(i['daily-settlement-price-abs'])
                    data.append(i['total-volume'])
                    data.append("USD")
                    try:
                        SetInformation().set(cursor, row[0], data)
                        data = []

                    except IndexError:
                        #print('An IndexError occurred when processing data:', data)
                        logger.error('An IndexError occurred when processing data: %s', data)
                        health_status = 0

            except Exception as e:
                #print(f"Exception: {e}")
                logger.error("Exception: %s", e)
                health_status = 0
                continue

    cursor.close()
    conn.commit()
    conn.close()

    to_log_file("\nFINISH RUN SCRIPT\n", True)
    #print(health_status)
    logger.info("Health status: %s", health_status)
    set_status_robot(1012, health_status, '')
    sync_to_elasticsearch()

except psycopg2.DatabaseError as e:
    health_status = 0
    to_log_file("\nConnect to DB PostgreSQL:  NO!!!\n", True)
    to_log_file(str(e), True)
    set_status_robot(1012, health_status, '')
    
