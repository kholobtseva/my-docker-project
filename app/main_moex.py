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

# Импортируем наши модули
from core.logging_utils import setup_logging
from core.kafka_utils import KafkaManager
from core.elastic_utils import ElasticsearchManager
from core.logging_utils import setup_graylog_logger

# Константы и настройки (такие же как в main)
health_status = 100
DB_CONFIG = {
    "host": "postgres",
    "database": "my_db", 
    "user": "user",
    "password": "password",
    "port": "5432"
}

# Классы (совместимые с main)
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
        

class Api:
    @staticmethod
    def get_data_json(url, contract_name):
        global health_status
        try:
            logger.info(f"Fetching MOEX data for {contract_name}")
            response = requests.get(url)
            data = json.loads(response.text)
            if len(data['history']['data']) == 0:
                health_status = 0
                raise ValueError(f'\nNo data available for {contract_name}\n')

            return data['history']['data']

        except requests.exceptions.RequestException as er:
            health_status = 0
            logger.error(f'MOEX Network error for {contract_name}: {er}')
            return []

        except ValueError as err:
            health_status = 0
            logger.error(f'MOEX Data error for {contract_name}: {err}')
            return []
        except Exception as e:
            logger.error(f'Unexpected MOEX error for {contract_name}: {str(e)}')
            health_status = 0
            return []

# Функции
def to_log_file(str_to_log, flag_print=False):
    """Функция логирования в файл"""
    if flag_print:
        print(str_to_log)
    path = "/app/logs"
    if not os.path.exists(path):
        os.mkdir(path)
    file_name = path + "/log_moex_" + str(date.today()) + ".txt"
    with open(file_name, 'a', encoding='utf-8') as file:
        file.write(str_to_log)

def get_current_date():
    """Получение текущей даты для логов"""
    return str(datetime.fromtimestamp(int(time.time()))) + '\n'

def set_status_robot(id, health_status, add_text):
    """Обновление статуса в health_monitor"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        query = "UPDATE public.health_monitor SET date_upd = now(), health_status = %s, add_text = %s WHERE id = %s"
        cursor.execute(query, (health_status, add_text, id))
        conn.commit()
        
        logger.info("MOEX health status updated", extra={
            'extra_data': {
                'event_type': 'health_status_updated',
                'health_status': health_status,
                'add_text': add_text
            }
        })

        cursor.close()
        conn.close()

    except Exception as e:
        logger.error(f"Error updating MOEX health status: {e}")

def sync_to_elasticsearch():
    """Синхронизация MOEX данных с Elasticsearch"""
    try:
        logger.info("Starting MOEX Elasticsearch synchronization...")
        
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT am.id_value, am.date_val, am.avg_val, am.volume, am.currency,
                   wdi.name_eng, wdi.name_rus
            FROM agriculture_moex am
            JOIN www_data_idx wdi ON am.id_value = wdi.id
            WHERE wdi.source = 'MOEX'
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
                'source': 'moex',
                'sync_timestamp': datetime.now().isoformat()
            }
            
            # Отправка в Elasticsearch
            es_result = es_manager.send_data(doc, 'agriculture-data')
            
            # Отправка в Kafka в отдельный топик
            kafka_result = kafka_manager.send_message('moex-market-data', doc)
            if kafka_result:
                kafka_sent_count += 1
                logger.info(f"SUCCESS MOEX data sent to Kafka: {doc.get('contract', 'Unknown')} - {doc.get('date', 'No date')}")
            else:
                logger.warning(f"FAILED to send MOEX data to Kafka: {doc.get('contract', 'Unknown')}")
            
            synced_count += 1
        
        kafka_manager.flush()
        logger.info(f"SUCCESS MOEX synchronization completed! ES: {synced_count}, Kafka: {kafka_sent_count}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"ERROR MOEX Elasticsearch synchronization error: {e}")

# Основная функция MOEX
def main_moex():
    global health_status, kafka_manager, es_manager
     
    logger.info("MOEX script started")
    
    try:
        to_log_file("\n\n\nSTART MOEX RUN SCRIPT\n", True)
        to_log_file(get_current_date(), True)
        
        health_status = 100
        
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        logger.info("MOEX database connection established")
        to_log_file("\nMOEX Connect to DB PostgreSQL: YES!!!\n", True)
        
        # Получаем все MOEX контракты
        cursor.execute("SELECT id, name_eng, url FROM public.www_data_idx where source='MOEX'")
        rows = cursor.fetchall()
        
        total_processed = 0
        successful_contracts = 0
        
        # Период для данных (последние 7 дней как в оригинальном скрипте)
        d1 = date.today() - timedelta(days=7)
        d2 = date.today()
        
        for row in rows:
            # Формируем URL для MOEX API
            url = f"{row[2]}{row[1]}.json?iss.only=history&iss.df=%25Y-%25m-%25d&from={str(d1)}&till={str(d2)}&history.columns=SECID,TRADEDATE,LOW,HIGH,CLOSE,VOLUME,CURRENCYID"
            
            to_log_file(f"\n-----\n{url}\n", True)  
            
            data_points = Api.get_data_json(url, row[1])
            
            if data_points:
                successful_contracts += 1
                print(f"✅ MOEX Processing {len(data_points)} records for {row[1]}")
                
                # Вставляем данные в БД
                for data_point in data_points:
                    # MOEX данные: SECID,TRADEDATE,LOW,HIGH,CLOSE,VOLUME,CURRENCYID
                    data = []
                    data.append(row[0])  # id
                    data.append(data_point[1])  # TRADEDATE
                    data.append(data_point[2])  # LOW (min_val)
                    data.append(data_point[3])  # HIGH (max_val)  
                    data.append(data_point[4])  # CLOSE (avg_val)
                    data.append(data_point[5])  # VOLUME
                    data.append(data_point[6])  # CURRENCYID
                    
                    try:
                        SetInformation().set(cursor, row[0], data)
                        total_processed += 1
                    except Exception as e:
                        logger.error(f"MOEX Error inserting data for {row[1]}: {e}")
                        health_status = 0
            else:
                print(f"❌ MOEX No data for {row[1]}")
    
        # Комитим изменения и закрываем соединение
        conn.commit()
        cursor.close()
        conn.close()
        
        # Синхронизируем с Elasticsearch
        sync_to_elasticsearch()
        
        # Обновляем статус (используем другой ID для MOEX)
        set_status_robot(1001, health_status, '')
        
        to_log_file("\nFINISH MOEX RUN SCRIPT\n", True)
        #print(f"\n🎉 MOEX COMPLETED: Processed {total_processed} records from {successful_contracts} contracts")
        logger.info(f"MOEX script completed: {total_processed} records from {successful_contracts} contracts")
        
    except Exception as e:
        logger.error("Error in MOEX main", extra={'error': str(e)})
        print(f"MOEX Error: {e}")
        health_status = 0
        set_status_robot(1001, health_status, '')

# Точка входа
if __name__ == "__main__":
    # Инициализация логирования и менеджеров
    logger = setup_logging('moex_script')
    graylog_logger = setup_graylog_logger('moex_script')
    kafka_manager = KafkaManager()
    es_manager = ElasticsearchManager()
    
    main_moex()