# app/main_refactored.py - Рефакторированная версия с модульной структурой
import sys
import os
import time
from datetime import timezone
import requests
import json
import psycopg2
import csv
from datetime import datetime, timedelta, date
from dateutil.relativedelta import *
from decimal import Decimal

# Импортируем наши новые модули
from core.logging_utils import setup_logging
from core.kafka_utils import KafkaManager
from core.elastic_utils import ElasticsearchManager

# Константы и настройки
health_status = 100  # ← ВЕРНУЛИ глобальную переменную
DB_CONFIG = {
    "host": "postgres",
    "database": "my_db", 
    "user": "user",
    "password": "password",
    "port": "5432"
}

# Классы
class SetInformation:
    @staticmethod
    def set(cursor, id_value, data):
        
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
        
        logger.debug("Data inserted/updated in agriculture_moex", extra={
            'extra_data': {
                'event_type': 'db_data_upserted',
                'id_value': id_value,
                'date': data[1],
                'price': data[4]
            }
        })

# Функции
def to_log_file(str_to_log, flag_print=False):
    """Функция логирования в файл"""
    if flag_print:
        print(str_to_log)
    path = "/app/logs"
    if not os.path.exists(path):
        os.mkdir(path)
    file_name = path + "/log_ore_futures" + str(date.today()) + ".txt"
    with open(file_name, 'a', encoding='utf-8') as file:
        file.write(str_to_log)

def get_data_json(url, contract_name):
    """Получение данных с Singapore Exchange"""
    global health_status  # ← ДОБАВИЛИ глобальную переменную
    data = []
    try:
        logger.info(f"Fetching data for {contract_name}")
        response = requests.get(url)
        
        if response.status_code != 200:
            logger.warning(f"API returned status {response.status_code} for {contract_name}")
            return []
        
        response_data = response.text
        if not response_data:
            logger.warning(f"Empty response for {contract_name}")
            return []
            
        try:
            data1 = json.loads(response_data)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for {contract_name}: {e}")
            return []
        
        # Проверка кода ответа
        if 'meta' in data1:
            error_code = data1['meta'].get('code')
            error_msg = data1['meta'].get('message', 'Unknown message')
            
            if error_code != '200':
                logger.warning(f"API error for {contract_name}: {error_msg} (code: {error_code})")
                return []
        
        # Проверяем структуру данных
        if 'data' not in data1:
            logger.warning(f"No 'data' field in response for {contract_name}")
            return []
            
        if data1['data'] is None:
            logger.warning(f"Data is None for {contract_name}")
            return []
            
        if not isinstance(data1['data'], list):
            logger.warning(f"Data is not a list for {contract_name}, type: {type(data1['data'])}")
            return []
            
        if len(data1['data']) == 0:
            logger.warning(f"Empty data list for {contract_name}")
            return []
            
        logger.info(f"Successfully retrieved {len(data1['data'])} records for {contract_name}")
        
        # Обрабатываем данные
        for n in data1['data']:
            if 'base-date' not in n:
                logger.warning(f"Missing 'base-date' in record for {contract_name}")
                continue
                
            date_obj = datetime.strptime(n['base-date'], "%Y%m%d")
            formatted_date = date_obj.strftime("%Y-%m-%d")
            
            data.append({
                'name': contract_name,
                'daily-settlement-price-abs': n.get('daily-settlement-price-abs'),
                'total-volume': n.get('total-volume'),
                'formatted_date': formatted_date
            })
        
        return data
        
    except requests.exceptions.RequestException as er:  # ← ДОБАВИЛИ конкретные исключения
        logger.error(f'Network error for {contract_name}: {er}')
        health_status = 0
        return []
    except ValueError as err:  # ← ДОБАВИЛИ конкретные исключения
        logger.error(f'Data parsing error for {contract_name}: {err}')  
        health_status = 0
        return []
    except Exception as e:
        logger.error(f'Unexpected error for {contract_name}: {str(e)}')
        health_status = 0  # ← ОБНОВЛЯЕМ статус при ошибке
        return []

def insert_record_if_not_exists():
    """Вставка записей в www_data_idx если их нет"""
    try:
        print("🔍 DEBUG: insert_record_if_not_exists() started")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Формируем список контрактов
        name_list = []
        current_date = datetime.now() - timedelta(days=1)
        dict_month = ["F", "G", "H", "J", "K", "M", "N", "Q", "U", "V", "X", "Z"]
        for i in range(0, 37):
            next_date = current_date + relativedelta(months=i)
            name_list.append(f"FEF{dict_month[next_date.month-1]}{str(next_date.year)[-2:]}")

        print(f"🔍 DEBUG: Generated {len(name_list)} contracts")

        # Параметризованные запросы
        inserted_count = 0
        
        for name in name_list:
            cursor.execute("SELECT id FROM public.www_data_idx WHERE name_eng = %s AND source = 'ore_futures'", (name,))
            record = cursor.fetchone()

            if record is None:
                cursor.execute("SELECT MAX(id) FROM public.www_data_idx")
                max_result = cursor.fetchone()
                max_id = max_result[0] if max_result[0] is not None else 0
                new_id = max_id + 1
                
                # ИСПРАВЛЕНИЕ: Меняем на русское название
                cursor.execute("""
                    INSERT INTO public.www_data_idx 
                    (id, mask, name_rus, name_eng, source, url, descr, date_upd) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    new_id, 
                    None,  # mask
                    'Железная руда 62% Fe',  # ← ИСПРАВИЛИ НА РУССКОЕ!
                    name,  # name_eng
                    'ore_futures',  # source
                    'https://api.sgx.com/derivatives/v1.0/history/symbol/',  # url
                    None,  # descr
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # date_upd
                ))
                
                inserted_count += 1
                print(f"✅ INSERTED: {name} with id {new_id}")

        conn.commit()
        cursor.close()
        conn.close()
        print(f"🔍 DEBUG: Completed, inserted {inserted_count} contracts")

    except Exception as error:
        print(f"❌ ERROR: {error}")


def set_status_robot(id, health_status, add_text):
    """Обновление статуса в health_monitor (из старого скрипта)"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        query = "UPDATE public.health_monitor SET date_upd = now(), health_status = %s, add_text = %s WHERE id = %s"
        cursor.execute(query, (health_status, add_text, id))
        conn.commit()
        
        logger.info("Health status updated", extra={
            'extra_data': {
                'event_type': 'health_status_updated',
                'health_status': health_status,
                'add_text': add_text
            }
        })

        cursor.close()
        conn.close()

    except Exception as e:
        logger.error(f"Error updating health status: {e}")

def sync_to_elasticsearch():
    """Синхронизация данных с Elasticsearch"""
    try:
        logger.info("Starting Elasticsearch synchronization...")
        
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # ТОЛЬКО ОДИН ЗАПРОС (с сортировкой)
        cursor.execute("""
            SELECT am.id_value, am.date_val, am.avg_val, am.volume, am.currency,
                   wdi.name_eng, wdi.name_rus
            FROM agriculture_moex am
            JOIN www_data_idx wdi ON am.id_value = wdi.id
            ORDER BY am.date_val, wdi.name_eng
        """)
        
        synced_count = 0
        kafka_sent_count = 0
        
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
            
            # Отправка в Elasticsearch
            es_result = es_manager.send_data(doc, 'agriculture-data')
            
            # Отправка в Kafka (ОДИН РАЗ!)
            kafka_result = kafka_manager.send_message('market-data', doc)
            if kafka_result:
                kafka_sent_count += 1
                logger.info(f"SUCCESS Data sent to Kafka: {doc.get('contract', 'Unknown')} - {doc.get('date', 'No date')}")
            else:
                logger.warning(f"FAILED to send to Kafka: {doc.get('contract', 'Unknown')}")
            
            synced_count += 1
        
        kafka_manager.flush()
        logger.info(f"SUCCESS Synchronization completed! ES: {synced_count}, Kafka: {kafka_sent_count}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"ERROR Elasticsearch synchronization error: {e}")

def get_current_date():  # ← ДОБАВИЛИ функцию из старого скрипта
    """Получение текущей даты для логов"""
    return str(datetime.fromtimestamp(int(time.time()))) + '\n'

# Основная функция
def main():
    global health_status, kafka_manager, es_manager  # ← ДОБАВИЛИ глобальные переменные
    
    logger.info("Script started")
    
    try:
        to_log_file("\n\n\nSTART RUN SCRIPT\n", True)
        to_log_file(get_current_date(), True)  # ← ДОБАВИЛИ запись даты
        
        interval = '1w'
        health_status = 100  # ← СБРАСЫВАЕМ статус при запуске
        
        # Вставляем записи если их нет
        #insert_record_if_not_exists()
        
        
        print("🔍 DEBUG: BEFORE insert_record_if_not_exists")
        insert_record_if_not_exists()
        print("🔍 DEBUG: AFTER insert_record_if_not_exists")
        
        # Динамическое формирование списка контрактов
        name_list = []
        current_date = datetime.now() - timedelta(days=1)
        dict_month = ["F", "G", "H", "J", "K", "M", "N", "Q", "U", "V", "X", "Z"]
        for i in range(0, 37):
            next_date = current_date + relativedelta(months=i)
            name_list.append(f"FEF{dict_month[next_date.month-1]}{str(next_date.year)[-2:]}")
        
        print(f"Generated {len(name_list)} dynamic contracts")
        
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        logger.info("Database connection established")
        to_log_file("\nConnect to DB PostgreSQL: YES!!!\n", True)
        
        # Получаем все контракты (как в старом скрипте)
        cursor.execute("SELECT id, name_eng, url FROM public.www_data_idx where source='ore_futures'")
        rows = cursor.fetchall()
        
        total_processed = 0
        successful_contracts = 0
        
        for row in rows:
            # ФИЛЬТРАЦИЯ как в старом скрипте
            if row[1] in name_list:  # ← ВЕРНУЛИ фильтрацию!
                url = f"{row[2]}{row[1]}?days={interval}&category=futures&params=base-date%2Cbase-date%2Ctotal-volume%2Cdaily-settlement-price-abs"
                to_log_file(f"\n-----\n{url}\n", True)  # ← ВЕРНУЛИ формат лога
                
                data_points = get_data_json(url, row[1])
                
                if data_points:
                    successful_contracts += 1
                    print(f"✅ Processing {len(data_points)} records for {row[1]}")
                    
                    # Вставляем данные в БД
                    for data_point in data_points:
                        data = []
                        data.append(row[0])  # id
                        data.append(data_point['formatted_date'])
                        data.append(None)  # min_val
                        data.append(None)  # max_val  
                        data.append(data_point['daily-settlement-price-abs'])
                        data.append(data_point['total-volume'])
                        data.append("USD")
                        
                        try:
                            SetInformation().set(cursor, row[0], data)
                            total_processed += 1
                        except Exception as e:
                            logger.error(f"Error inserting data for {row[1]}: {e}")
                            health_status = 0
                else:
                    print(f"❌ No data for {row[1]}")
        
        # Комитим изменения и закрываем соединение
        conn.commit()
        cursor.close()
        conn.close()
        
        # Синхронизируем с Elasticsearch
        sync_to_elasticsearch()
        
        # Обновляем статус
        set_status_robot(1012, health_status, '')
        
        to_log_file("\nFINISH RUN SCRIPT\n", True)
        print(f"\n🎉 COMPLETED: Processed {total_processed} records from {successful_contracts} contracts")
        logger.info(f"Script completed: {total_processed} records from {successful_contracts} contracts")
        
    except Exception as e:
        logger.error("Error in main", extra={'error': str(e)})
        print(f"Error: {e}")
        health_status = 0
        set_status_robot(1012, health_status, '')

# Точка входа
if __name__ == "__main__":
    # Инициализация логирования и менеджеров
    logger = setup_logging('main_script')
    kafka_manager = KafkaManager()
    es_manager = ElasticsearchManager()
    
    main()