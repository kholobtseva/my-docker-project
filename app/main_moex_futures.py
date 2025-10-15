import sys
import os
import time
from datetime import datetime, timedelta, date
import requests
import json
import psycopg2
from core.logging_utils import setup_logging
from core.kafka_utils import KafkaManager
from core.elastic_utils import ElasticsearchManager
from core.logging_utils import setup_graylog_logger

# Константы и настройки
health_status = 100
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

class Api:
    @staticmethod
    def get_data_json(url, contract_name):
        global health_status
        try:
            logger.info(f"Fetching MOEX-FUTURES data for {contract_name}")
            response = requests.get(url)
            
            # Проверяем статус ответа
            if response.status_code != 200:
                logger.error(f"HTTP {response.status_code} for {contract_name}")
                return []
            
            # Проверяем что ответ не пустой
            if not response.text.strip():
                logger.warning(f"Empty response for {contract_name}")
                return []
                
            data = json.loads(response.text)
            
            # Проверяем структуру исторических данных
            if 'history' not in data:
                logger.warning(f"No history data found for {contract_name}")
                return []
                
            if 'data' not in data['history']:
                logger.warning(f"No data array in history for {contract_name}")
                return []
                
            if len(data['history']['data']) == 0:
                logger.warning(f"No historical data available for {contract_name}")
                return []

            logger.info(f"Found {len(data['history']['data'])} historical records for {contract_name}")
            return data['history']['data']

        except json.JSONDecodeError as e:
            logger.error(f'MOEX-FUTURES JSON decode error for {contract_name}: {e}')
            # Показываем начало ответа для отладки
            if 'response' in locals():
                logger.error(f'Response preview: {response.text[:200]}')
            return []
        except Exception as e:
            logger.error(f'Unexpected MOEX-FUTURES error for {contract_name}: {str(e)}')
            return []

# Функции
def to_log_file(str_to_log, flag_print=False):
    """Функция логирования в файл"""
    if flag_print:
        print(str_to_log)
    path = "/app/logs"
    if not os.path.exists(path):
        os.makedirs(path)
    file_name = path + "/log_moex_futures_" + str(date.today()) + ".txt"
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
        
        logger.info("MOEX-FUTURES health status updated", extra={
            'extra_data': {
                'event_type': 'health_status_updated',
                'health_status': health_status,
                'add_text': add_text
            }
        })

        cursor.close()
        conn.close()

    except Exception as e:
        logger.error(f"Error updating MOEX-FUTURES health status: {e}")

def generate_names(input_date):
    """Генерация имен фьючерсов по дате (W4 и BR) - только 8 ближайших месяцев"""
    dict_month = {1: "F", 2: "G", 3: "H", 4: "J", 5: "K", 6: "M", 
                  7: "N", 8: "Q", 9: "U", 10: "V", 11: "X", 12: "Z"}
    names = []

    current_date = input_date

    # ТОЛЬКО 8 ближайших месяцев вместо 13
    for i in range(8):
        year = str(current_date.year)[-1]  # Последняя цифра года
        month = current_date.month
        name_w4 = f"W4{dict_month[month]}{year}"
        name_br = f"BR{dict_month[month]}{year}"
        names.extend([name_w4, name_br])

        if month == 12:  # Если декабрь, переходим на следующий год
            current_date = current_date.replace(year=current_date.year+1, month=1, day=1)
        else:
            current_date = current_date.replace(month=current_date.month+1, day=1)

    logger.info(f"Generated {len(names)} active futures: {names}")
    return names

def insert_futures_if_not_exists():
    """Вставка фьючерсов в www_data_idx если их нет"""
    try:
        logger.info("Checking and inserting MOEX-FUTURES contracts")
        
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Генерируем список имен фьючерсов от вчерашней даты
        name_list = generate_names(datetime.now() - timedelta(days=1))
        logger.info(f"Generated {len(name_list)} futures names: {name_list}")

        inserted_count = 0
        
        for name in name_list:
            # Проверяем существует ли уже такой фьючерс
            cursor.execute(
                "SELECT id FROM public.www_data_idx WHERE name_eng = %s AND source = 'MOEX-FUTURES'", 
                (name,)
            )
            record = cursor.fetchone()

            if record is None:
                # Получаем максимальный ID
                cursor.execute("SELECT MAX(id) FROM public.www_data_idx")
                max_result = cursor.fetchone()
                max_id = max_result[0] if max_result[0] is not None else 0
                new_id = max_id + 1
                
                # Определяем русское название
                if name.startswith('W4'):
                    name_rus = 'Пшеница'
                else:  # BR
                    name_rus = 'Нефть Brent'
                
                # Правильный URL с board ID RFUD
                url_template = 'https://iss.moex.com/iss/history/engines/futures/markets/forts/boards/RFUD/securities/'
                
                # Вставляем новый фьючерс
                cursor.execute("""
                    INSERT INTO public.www_data_idx 
                    (id, mask, name_rus, name_eng, source, url, descr, date_upd) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    new_id, 
                    None,  # mask
                    name_rus, 
                    name,  # name_eng
                    'MOEX-FUTURES',  # source
                    url_template,  # url
                    f'Фьючерс {name_rus} {name}',  # descr
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # date_upd
                ))
                
                inserted_count += 1
                logger.info(f"INSERTED new futures contract: {name} with id {new_id}")

        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Completed futures insertion: {inserted_count} new contracts")
        return inserted_count

    except Exception as error:
        logger.error(f"Error inserting futures contracts: {error}")
        return 0

def sync_to_elasticsearch():
    """Синхронизация MOEX-FUTURES данных с Elasticsearch"""
    try:
        logger.info("Starting MOEX-FUTURES Elasticsearch synchronization...")
        
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT am.id_value, am.date_val, am.avg_val, am.volume, am.currency,
                   wdi.name_eng, wdi.name_rus
            FROM agriculture_moex am
            JOIN www_data_idx wdi ON am.id_value = wdi.id
            WHERE wdi.source = 'MOEX-FUTURES'
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
                'source': 'moex_futures',
                'sync_timestamp': datetime.now().isoformat()
            }
            
            # Отправка в Elasticsearch
            es_result = es_manager.send_data(doc, 'agriculture-data')
            
            # Отправка в Kafka в отдельный топик
            kafka_result = kafka_manager.send_message('moex-futures-data', doc)
            if kafka_result:
                kafka_sent_count += 1
                logger.info(f"SUCCESS MOEX-FUTURES data sent to Kafka: {doc.get('contract', 'Unknown')} - {doc.get('date', 'No date')}")
            
            synced_count += 1
        
        kafka_manager.flush()
        logger.info(f"SUCCESS MOEX-FUTURES synchronization completed! ES: {synced_count}, Kafka: {kafka_sent_count}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"ERROR MOEX-FUTURES Elasticsearch synchronization error: {e}")

# Основная функция MOEX-FUTURES
def main_moex_futures():
    global health_status, kafka_manager, es_manager
     
    logger.info("MOEX-FUTURES script started")
    
    try:
        to_log_file("\n\n\nSTART MOEX-FUTURES RUN SCRIPT\n", True)
        to_log_file(get_current_date(), True)
        
        health_status = 100
        
        # 1. Сначала вставляем фьючерсы если их нет
        inserted_count = insert_futures_if_not_exists()
        logger.info(f"Inserted {inserted_count} new futures contracts")
        
        # 2. Подключаемся к БД для получения данных
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        logger.info("MOEX-FUTURES database connection established")
        to_log_file("\nMOEX-FUTURES Connect to DB PostgreSQL: YES!!!\n", True)
        
        # 3. Получаем все MOEX-FUTURES контракты
        cursor.execute("SELECT id, name_eng, url FROM public.www_data_idx where source='MOEX-FUTURES'")
        rows = cursor.fetchall()
        
        # 4. Генерируем список актуальных имен для фильтрации (от вчерашней даты)
        current_name_list = generate_names(datetime.now() - timedelta(days=1))
        logger.info(f"Filtering by {len(current_name_list)} current contracts: {current_name_list}")
        
        total_processed = 0
        successful_contracts = 0
        
        # Период для данных - актуальные даты от сегодня
        d1 = date.today() - timedelta(days=40)  # 40 дней назад
        d2 = date.today()                       # Сегодня
        
        for row in rows:
            # Фильтруем только актуальные контракты (исключаем последние 2 как в оригинале)
            if row[1] in current_name_list[:-2]:
                # Правильный URL с board ID RFUD и косой чертой перед .json
                url = f"{row[2]}{row[1]}/.json?from={str(d1)}&till={str(d2)}&history.columns=SECID,TRADEDATE,LOW,HIGH,SETTLEPRICE,VOLUME"
                
                to_log_file(f"\n-----\n{url}\n", True)  
                
                data_points = Api.get_data_json(url, row[1])
                
                if data_points:
                    successful_contracts += 1
                    logger.info(f"Processing {len(data_points)} records for {row[1]}")
                    
                    # Определяем валюту по типу контракта
                    currency = "RUB" if row[1].startswith("W4") else "USD"
                    
                    # Вставляем данные в БД
                    for data_point in data_points:
                        data = []
                        data.append(row[0])  # id
                        data.append(data_point[1])  # TRADEDATE
                        data.append(data_point[2])  # LOW (min_val)
                        data.append(data_point[3])  # HIGH (max_val)  
                        data.append(data_point[4])  # SETTLEPRICE (avg_val)
                        data.append(data_point[5])  # VOLUME
                        data.append(currency)  # определяем валюту
                        
                        try:
                            SetInformation().set(cursor, row[0], data)
                            total_processed += 1
                        except Exception as e:
                            logger.error(f"MOEX-FUTURES Error inserting data for {row[1]}: {e}")
                            health_status = 0
                else:
                    logger.warning(f"No data for {row[1]}")
    
        # Комитим изменения и закрываем соединение
        conn.commit()
        cursor.close()
        conn.close()
        
        # Синхронизируем с Elasticsearch
        sync_to_elasticsearch()
        
        # Обновляем статус (используем отдельный ID для MOEX-FUTURES)
        set_status_robot(1008, health_status, '')
        
        to_log_file("\nFINISH MOEX-FUTURES RUN SCRIPT\n", True)
        logger.info(f"MOEX-FUTURES script completed: {total_processed} records from {successful_contracts} contracts")
        
    except Exception as e:
        logger.error("Error in MOEX-FUTURES main", extra={'error': str(e)})
        print(f"MOEX-FUTURES Error: {e}")
        health_status = 0
        set_status_robot(1008, health_status, '')

# Точка входа
if __name__ == "__main__":
    # Инициализация логирования и менеджеров
    logger = setup_logging('moex_futures_script')
    graylog_logger = setup_graylog_logger('moex_futures_script')
    kafka_manager = KafkaManager()
    es_manager = ElasticsearchManager()
    
    main_moex_futures()