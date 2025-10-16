import sys
import os
import time
from datetime import datetime, timedelta, date
import requests
import json
import psycopg2
from core.logging_utils import setup_logging, setup_graylog_logger
from core.kafka_utils import KafkaManager
from core.elastic_utils import ElasticsearchManager
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

class Api:
    @staticmethod
    def get_data_json(url, contract_name):
        global health_status
        try:
            logger.info(f"Fetching MOEX data for {contract_name}")
            response = requests.get(url)
            
            if response.status_code != 200:
                logger.warning(f"MOEX API returned status {response.status_code} for {contract_name}")
                health_status = 0
                return []
            
            response_data = response.text
            if not response_data:
                logger.warning(f"Empty MOEX response for {contract_name}")
                health_status = 0
                return []
                
            data = json.loads(response_data)
            
            if 'history' not in data:
                logger.warning(f"No 'history' field in MOEX response for {contract_name}")
                health_status = 0
                return []
                
            if 'data' not in data['history']:
                logger.warning(f"No 'data' field in MOEX history for {contract_name}")
                health_status = 0
                return []
                
            if data['history']['data'] is None:
                logger.warning(f"MOEX Data is None for {contract_name}")
                health_status = 0
                return []
                
            if not isinstance(data['history']['data'], list):
                logger.warning(f"MOEX Data is not a list for {contract_name}, type: {type(data['history']['data'])}")
                health_status = 0
                return []
                
            if len(data['history']['data']) == 0:
                logger.warning(f"Empty MOEX data list for {contract_name}")
                health_status = 0
                return []

            logger.info(f"Successfully retrieved {len(data['history']['data'])} MOEX records for {contract_name}")
            return data['history']['data']

        except requests.exceptions.RequestException as er:
            health_status = 0
            logger.error(f'MOEX Network error for {contract_name}: {er}')
            return []
        except json.JSONDecodeError as e:
            health_status = 0
            logger.error(f"MOEX JSON decode error for {contract_name}: {e}")
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

def sync_to_elasticsearch(validator):
    """Синхронизация MOEX данных с Elasticsearch"""
    try:
        logger.info("🚀 Starting MOEX Elasticsearch synchronization...")
  
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
        validation_errors = 0
        
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
            
            # ВАЛИДАЦИЯ перед отправкой
            is_valid, errors = validator.validate_for_kafka(doc)

            if not is_valid:
                # Отправка в dead letter queue
                dlq_result = validator.send_to_dead_letter_queue(
                    doc,
                    errors,
                    'moex-market-data',
                    'moex'
                )
                validation_errors += 1
                logger.warning(f"Validation failed for {doc.get('contract')}: {errors}")
                continue
            
            
            es_result = es_manager.send_data(doc, 'agriculture-data')
            if es_result:
                synced_count += 1
                logger.info(f"✅ ES SUCCESS: {doc.get('contract')} - {doc.get('date')}")
            else:
                logger.error(f"❌ ES FAILED: {doc.get('contract')}")
            
            # Отправка в Kafka
            kafka_result = kafka_manager.send_message('moex-market-data', doc)
            if kafka_result:
                kafka_sent_count += 1
                logger.info(f"✅ KAFKA SUCCESS: {doc.get('contract')} - {doc.get('date')}")
            
        kafka_manager.flush()
        logger.info(f"🎉 MOEX SYNC COMPLETE! ES: {synced_count}, Kafka: {kafka_sent_count}, Validation errors: {validation_errors}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"💥 MOEX Elasticsearch synchronization error: {e}")
        
        
# Основная функция MOEX
def main_moex():
    global health_status, kafka_manager, es_manager
    
    logger.info("MOEX script started")
    
    # Инициализация валидатора
    validator = UniversalDataValidator(kafka_manager, 'moex_script')
    
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
        validation_errors = 0
        
        # Период для данных (последние 7 дней)
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
                
                # ОБРАБОТКА ДАННЫХ С ВАЛИДАЦИЕЙ
                for data_point in data_points:
                    # ВАЛИДАЦИЯ СТРУКТУРЫ MOEX API данных
                    is_valid_structure, structure_errors = validator.validate_basic_structure(data_point, 'moex_api')
                    
                    if not is_valid_structure:
                        validator.send_to_dead_letter_queue(
                            {'contract': row[1], 'raw_data': data_point},
                            structure_errors,
                            'moex-market-data',
                            'moex_api'
                        )
                        validation_errors += 1
                        logger.warning(f"MOEX API structure validation failed for {row[1]}: {structure_errors}")
                        continue
                    
                    # ВАЛИДАЦИЯ ДАТЫ
                    is_valid_date, date_error = validator.validate_date_field(data_point[1], 'TRADEDATE')
                    if not is_valid_date:
                        validator.send_to_dead_letter_queue(
                            {'contract': row[1], 'raw_data': data_point},
                            [date_error],
                            'moex-market-data',
                            'moex_api'
                        )
                        validation_errors += 1
                        logger.warning(f"MOEX date validation failed for {row[1]}: {date_error}")
                        continue
                    
                    # КОНВЕРТАЦИЯ В СТРУКТУРИРОВАННЫЙ ФОРМАТ
                    try:
                        structured_data = validator.convert_moex_api_to_structured(data_point, row[0])
                    except ValueError as e:
                        validator.send_to_dead_letter_queue(
                            {'contract': row[1], 'raw_data': data_point},
                            [str(e)],
                            'moex-market-data',
                            'moex_api'
                        )
                        validation_errors += 1
                        logger.warning(f"MOEX data conversion failed for {row[1]}: {e}")
                        continue
                    
                    # ВАЛИДАЦИЯ СТРУКТУРИРОВАННЫХ ДАННЫХ
                    is_valid_structured, structured_errors = validator.validate_basic_structure(structured_data, 'structured')
                    if not is_valid_structured:
                        validator.send_to_dead_letter_queue(
                            structured_data,
                            structured_errors,
                            'moex-market-data',
                            'moex_structured'
                        )
                        validation_errors += 1
                        logger.warning(f"MOEX structured data validation failed for {row[1]}: {structured_errors}")
                        continue
                    
                    # СОХРАНЕНИЕ В БД
                    try:
                        data = [
                            structured_data['id_value'],
                            structured_data['date_val'],
                            structured_data['min_val'],
                            structured_data['max_val'],
                            structured_data['avg_val'],
                            structured_data['volume'],
                            structured_data['currency']
                        ]
                        
                        SetInformation().set(cursor, row[0], data)
                        total_processed += 1
                        logger.debug(f"MOEX data inserted/updated for {row[1]}", extra={
                            'extra_data': {
                                'event_type': 'moex_data_upserted',
                                'contract': row[1],
                                'date': structured_data['date_val'],
                                'price': structured_data['avg_val']
                            }
                        })
                    except Exception as e:
                        logger.error(f"MOEX Error inserting data for {row[1]}: {e}")
                        health_status = 0
            else:
                print(f"❌ MOEX No data for {row[1]}")
                logger.warning(f"No MOEX data retrieved for contract: {row[1]}")
    
        # Комитим изменения и закрываем соединение
        conn.commit()
        cursor.close()
        conn.close()
        
        # Синхронизируем с Elasticsearch (передаем валидатор)
        sync_to_elasticsearch(validator)
        
        # Обновляем статус
        status_text = f'Processed: {total_processed}, Validation errors: {validation_errors}'
        set_status_robot(1001, health_status, status_text)
        
        to_log_file("\nFINISH MOEX RUN SCRIPT\n", True)
        print(f"\n🎉 MOEX COMPLETED: Processed {total_processed} records from {successful_contracts} contracts, validation errors: {validation_errors}")
        logger.info(f"MOEX script completed: {total_processed} records from {successful_contracts} contracts, validation errors: {validation_errors}")
        
    except psycopg2.Error as db_error:
        logger.error(f"MOEX Database error: {db_error}")
        health_status = 0
        set_status_robot(1001, health_status, f'Database error: {db_error}')
    except Exception as e:
        logger.error("Error in MOEX main", extra={'error': str(e)})
        print(f"MOEX Error: {e}")
        health_status = 0
        set_status_robot(1001, health_status, f'Runtime error: {e}')

# Точка входа
if __name__ == "__main__":
    # Инициализация логирования и менеджеров
    logger = setup_logging('moex_script')
    graylog_logger = setup_graylog_logger('moex_script')
    kafka_manager = KafkaManager()
    es_manager = ElasticsearchManager()
    
    main_moex()