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
from core.logging_utils import setup_logging
from core.kafka_utils import KafkaManager
from core.elastic_utils import ElasticsearchManager
from core.logging_utils import setup_graylog_logger
from core.validation_utils import UniversalDataValidator

# Константы и настройки
health_status = 100
DB_CONFIG = {
    "host": "postgres",
    "database": "my_db", 
    "user": "user",
    "password": "password",
    "port": "5432"
}

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

def get_data_json(url, contract_name, validator):
    """Получение данных с Singapore Exchange с валидацией"""
    global health_status
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
            # Отправляем в DLQ
            validator.send_to_dead_letter_queue(
                {'url': url, 'contract': contract_name, 'raw_response': response_data[:500]},
                [f"JSON decode error: {e}"],
                'market-data',
                'sgx_api'
            )
            return []
        
        # Проверка кода ответа
        if 'meta' in data1:
            error_code = data1['meta'].get('code')
            error_msg = data1['meta'].get('message', 'Unknown message')
            
            if error_code != '200':
                logger.warning(f"API error for {contract_name}: {error_msg} (code: {error_code})")
                validator.send_to_dead_letter_queue(
                    {'url': url, 'contract': contract_name, 'api_error': error_msg},
                    [f"API error: {error_msg} (code: {error_code})"],
                    'market-data',
                    'sgx_api'
                )
                return []
        
        # Проверяем структуру данных
        if 'data' not in data1:
            logger.warning(f"No 'data' field in response for {contract_name}")
            validator.send_to_dead_letter_queue(
                {'url': url, 'contract': contract_name, 'response_structure': data1.keys()},
                ["No 'data' field in API response"],
                'market-data',
                'sgx_api'
            )
            return []
            
        if data1['data'] is None:
            logger.warning(f"Data is None for {contract_name}")
            return []
            
        if not isinstance(data1['data'], list):
            logger.warning(f"Data is not a list for {contract_name}, type: {type(data1['data'])}")
            validator.send_to_dead_letter_queue(
                {'url': url, 'contract': contract_name, 'data_type': str(type(data1['data']))},
                [f"Data is not a list, type: {type(data1['data'])}"],
                'market-data',
                'sgx_api'
            )
            return []
            
        if len(data1['data']) == 0:
            logger.warning(f"Empty data list for {contract_name}")
            return []
            
        logger.info(f"Successfully retrieved {len(data1['data'])} records for {contract_name}")
        
        # Обрабатываем данные с валидацией
        for n in data1['data']:
            if 'base-date' not in n:
                logger.warning(f"Missing 'base-date' in record for {contract_name}")
                validator.send_to_dead_letter_queue(
                    {'contract': contract_name, 'record': n},
                    ["Missing 'base-date' in record"],
                    'market-data',
                    'sgx_record'
                )
                continue
                
            # Валидация даты
            try:
                date_obj = datetime.strptime(n['base-date'], "%Y%m%d")
                formatted_date = date_obj.strftime("%Y-%m-%d")
            except ValueError as e:
                logger.warning(f"Invalid date format for {contract_name}: {n['base-date']}")
                validator.send_to_dead_letter_queue(
                    {'contract': contract_name, 'raw_date': n['base-date'], 'record': n},
                    [f"Invalid date format: {n['base-date']}"],
                    'market-data',
                    'sgx_record'
                )
                continue
            
            # Валидация числовых полей
            price = n.get('daily-settlement-price-abs')
            volume = n.get('total-volume')
            
            if price is not None:
                try:
                    float(price)
                except (TypeError, ValueError):
                    validator.send_to_dead_letter_queue(
                        {'contract': contract_name, 'price': price, 'record': n},
                        [f"Invalid price format: {price}"],
                        'market-data',
                        'sgx_record'
                    )
                    continue
            
            if volume is not None:
                try:
                    float(volume)
                except (TypeError, ValueError):
                    validator.send_to_dead_letter_queue(
                        {'contract': contract_name, 'volume': volume, 'record': n},
                        [f"Invalid volume format: {volume}"],
                        'market-data',
                        'sgx_record'
                    )
                    continue
            
            data.append({
                'name': contract_name,
                'daily-settlement-price-abs': price,
                'total-volume': volume,
                'formatted_date': formatted_date
            })
        
        return data
        
    except requests.exceptions.RequestException as er:
        health_status = 0
        validator.send_to_dead_letter_queue(
            {'url': url, 'contract': contract_name, 'error': str(er)},
            [f"Request error: {str(er)}"],
            'market-data',
            'sgx_api'
        )
        return []
    except ValueError as err: 
        logger.error(f'Data parsing error for {contract_name}: {err}')
        health_status = 0
        return []
    except Exception as e:
        logger.error(f'Unexpected error for {contract_name}: {str(e)}')
        health_status = 0
        validator.send_to_dead_letter_queue(
            {'url': url, 'contract': contract_name, 'error': str(e)},
            [f"Unexpected error: {str(e)}"],
            'market-data',
            'sgx_api'
        )
        return []

def insert_record_if_not_exists():
    """Вставка записей в www_data_idx если их нет"""
    try:
        
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Формируем список контрактов
        name_list = []
        current_date = datetime.now() - timedelta(days=1)
        dict_month = ["F", "G", "H", "J", "K", "M", "N", "Q", "U", "V", "X", "Z"]
        for i in range(0, 37):
            next_date = current_date + relativedelta(months=i)
            name_list.append(f"FEF{dict_month[next_date.month-1]}{str(next_date.year)[-2:]}")

        
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
                
                cursor.execute("""
                    INSERT INTO public.www_data_idx 
                    (id, mask, name_rus, name_eng, source, url, descr, date_upd) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    new_id, 
                    None,  # mask
                    'Железная руда 62% Fe', 
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
        

    except Exception as error:
        print(f"❌ ERROR: {error}")

def set_status_robot(id, health_status, add_text):
    """Обновление статуса в health_monitor"""
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

def sync_to_elasticsearch(validator):
    """Синхронизация данных с Elasticsearch с валидацией"""
    try:
        logger.info("🚀 Starting Elasticsearch synchronization...")
        
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT am.id_value, am.date_val, am.avg_val, am.volume, am.currency,
                   wdi.name_eng, wdi.name_rus
            FROM agriculture_moex am
            JOIN www_data_idx wdi ON am.id_value = wdi.id
            WHERE wdi.source = 'ore_futures'
            ORDER BY am.date_val, wdi.name_eng
        """)
        
        synced_count = 0
        kafka_sent_count = 0
        validation_errors = 0
        
        for row in cursor.fetchall():
            # Подготавливаем данные для Kafka
            doc = validator.prepare_for_kafka(row)
            
            # ВАЛИДАЦИЯ перед отправкой
            is_valid, errors = validator.validate_for_kafka(doc)
            
            if not is_valid:
                # Отправка в dead letter queue
                dlq_result = validator.send_to_dead_letter_queue(
                    doc,
                    errors,
                    'market-data',
                    'sgx'
                )
                validation_errors += 1
                logger.warning(f"Validation failed for {doc.get('contract')}: {errors}")
                continue
            
            
            es_result = es_manager.send_data(doc, 'agriculture-data')
            if es_result:
                synced_count += 1
                logger.info(f"✅ ES SUCCESS: {doc.get('contract', 'Unknown')} - {doc.get('date', 'No date')}")
            else:
                logger.warning(f"❌ ES FAILED: {doc.get('contract', 'Unknown')}")
            
            # Отправка в Kafka
            kafka_result = kafka_manager.send_message('market-data', doc)
            if kafka_result:
                kafka_sent_count += 1
                logger.info(f"✅ KAFKA SUCCESS: {doc.get('contract', 'Unknown')}")
            
        kafka_manager.flush()
        logger.info(f"🎉 SYNC COMPLETE! ES: {synced_count}, Kafka: {kafka_sent_count}, Validation errors: {validation_errors}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"💥 Elasticsearch synchronization error: {e}")

def get_current_date():
    """Получение текущей даты для логов"""
    return str(datetime.fromtimestamp(int(time.time()))) + '\n'

# Основная функция
def main():
    global health_status, kafka_manager, es_manager
    
    logger.info("Script started")
    
    # Инициализация валидатора
    validator = UniversalDataValidator(kafka_manager, 'sgx_script')
    
    try:
        to_log_file("\n\n\nSTART RUN SCRIPT\n", True)
        to_log_file(get_current_date(), True)
        
        health_status = 100
        
        # Вставляем записи если их нет
        insert_record_if_not_exists()
        
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
        
        # Получаем все контракты
        cursor.execute("SELECT id, name_eng, url FROM public.www_data_idx where source='ore_futures'")
        rows = cursor.fetchall()
        
        total_processed = 0
        successful_contracts = 0
        validation_errors = 0
        
        for row in rows:
            # ФИЛЬТРАЦИЯ 
            if row[1] in name_list:  
                url = f"{row[2]}{row[1]}?days=8w&category=futures&params=base-date%2Cbase-date%2Ctotal-volume%2Cdaily-settlement-price-abs"
                to_log_file(f"\n-----\n{url}\n", True)  
                
                data_points = get_data_json(url, row[1], validator)
                
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
        
        # Синхронизируем с Elasticsearch (передаем валидатор)
        sync_to_elasticsearch(validator)
        
        # Обновляем статус
        status_text = f'Processed: {total_processed}, Validation errors: {validation_errors}'
        set_status_robot(1012, health_status, status_text)
        
        to_log_file("\nFINISH RUN SCRIPT\n", True)
        print(f"\n🎉 COMPLETED: Processed {total_processed} records from {successful_contracts} contracts, validation errors: {validation_errors}")
        logger.info(f"Script completed: {total_processed} records from {successful_contracts} contracts, validation errors: {validation_errors}")
        
    except Exception as e:
        logger.error("Error in main", extra={'error': str(e)})
        print(f"Error: {e}")
        health_status = 0
        set_status_robot(1012, health_status, f'Runtime error: {e}')

# Точка входа
if __name__ == "__main__":
    # Инициализация логирования и менеджеров
    logger = setup_logging('main_script')
    graylog_logger = setup_graylog_logger('main_script')
    kafka_manager = KafkaManager()
    es_manager = ElasticsearchManager()
    
    main()