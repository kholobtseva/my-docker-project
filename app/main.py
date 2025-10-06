import logging
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
from elasticsearch import Elasticsearch
from kafka import KafkaProducer
from decimal import Decimal


# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Структурированный форматтер для Elasticsearch
class ElasticsearchJSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': record.levelname,
            'logger': 'main_script',
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName
        }
        
        # Добавляем extra данные если есть
        if hasattr(record, 'extra_data'):
            log_entry.update(record.extra_data)
            
        return json.dumps(log_entry)

# Клиент для логов
es_logs = Elasticsearch(['http://elasticsearch:9200'])

class ElasticsearchLogHandler(logging.Handler):
    def emit(self, record):
        try:
            log_entry = json.loads(self.format(record))
            es_logs.index(index='main-script-logs', document=log_entry)
        except Exception as e:
            # Если не получится отправить в ES - логи просто пропадут
            pass

# Добавляем хендлер для Elasticsearch
json_formatter = ElasticsearchJSONFormatter()
es_handler = ElasticsearchLogHandler()
es_handler.setFormatter(json_formatter)
logger.addHandler(es_handler)

es = Elasticsearch(['http://elasticsearch:9200'])

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (Decimal,)):
            return float(obj)
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

try:
   
    producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=lambda v: json.dumps(v, ensure_ascii=False, cls=CustomJSONEncoder).encode('utf-8')
)
    
    logger.info("SUCCESS Kafka producer initialized", extra={
        'extra_data': {
            'event_type': 'kafka_producer_initialized',
            'status': 'success'
        }
    })
except Exception as e:
    logger.warning(f"WARNING Failed to connect to Kafka: {e}", extra={
        'extra_data': {
            'event_type': 'kafka_producer_failed',
            'status': 'failed',
            'error': str(e)
        }
    })
    producer = None

def send_to_elasticsearch(data, index_name):
    try:
        es.index(index=index_name, body=data)
        logger.info(f"Data sent to Elasticsearch index: {index_name}", extra={
            'extra_data': {
                'event_type': 'elasticsearch_send_success',
                'index_name': index_name,
                'contract': data.get('contract', 'unknown')
            }
        })
        if producer is not None:
            producer.flush(timeout=30)
    except Exception as e:
        logger.error(f"Error sending to Elasticsearch: {e}", extra={
            'extra_data': {
                'event_type': 'elasticsearch_send_error',
                'index_name': index_name,
                'error': str(e)
            }
        })

def send_to_kafka(data):
    if producer is not None:
        try:
            # Create data copy and convert Decimal to float
            kafka_data = data.copy()
            
            # Convert all Decimal values to float
            for key, value in kafka_data.items():
                if isinstance(value, Decimal):
                    kafka_data[key] = float(value)
            
            # Ensure data is dict
            if isinstance(kafka_data, dict):
                future = producer.send('market-data', value=kafka_data)
                future.get(timeout=10)
                logger.info(f"SUCCESS Data sent to Kafka: {kafka_data.get('contract', 'Unknown')} - {kafka_data.get('date', 'No date')}", extra={
                    'extra_data': {
                        'event_type': 'kafka_send_success',
                        'contract': kafka_data.get('contract'),
                        'date': kafka_data.get('date'),
                        'price': kafka_data.get('price')
                    }
                })
            else:
                logger.warning(f"WARNING Invalid data format for Kafka: {type(kafka_data)} - {str(kafka_data)[:100]}", extra={
                    'extra_data': {
                        'event_type': 'kafka_send_invalid_format',
                        'data_type': str(type(kafka_data))
                    }
                })
        except Exception as e:
            logger.warning(f"WARNING Kafka send error: {e}", extra={
                'extra_data': {
                    'event_type': 'kafka_send_error',
                    'error': str(e)
                }
            })


# Database connection settings from environment variables
DB_CONFIG = {
    "host": "postgres",
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
        
        logger.info("Data fetched from Singapore Exchange", extra={
            'extra_data': {
                'event_type': 'api_data_fetched',
                'contract': i,
                'data_points': len(data1['data']),
                'url': url
            }
        })
        
        for n in data1['data']:
            date_obj = datetime.strptime(n['base-date'], "%Y%m%d")
            formatted_date = date_obj.strftime("%Y-%m-%d")
            data.append({'name': i,
                'daily-settlement-price-abs': n['daily-settlement-price-abs'],
                'total-volume': n['total-volume'],
                'formatted_date': formatted_date
            })
    except requests.exceptions.RequestException as er:
        logger.error('Network error: %s', er, extra={
            'extra_data': {
                'event_type': 'api_request_failed',
                'contract': i,
                'error_type': 'network_error',
                'error': str(er)
            }
        })
        health_status = 0
        to_log_file('\nNetwork error!\n')
        set_status_robot(1012, health_status, '')
    except ValueError as err:
        logger.error('ValueError: %s', err, extra={
            'extra_data': {
                'event_type': 'api_data_parse_error',
                'contract': i,
                'error_type': 'value_error',
                'error': str(err)
            }
        })
        health_status = 0
        to_log_file('\nNo data available for the requested date\n')
    return data

def insert_record_if_not_exists():
    try:
        # Database connection via psycopg2
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        logger.info("Database connection established", extra={
            'extra_data': {
                'event_type': 'db_connection_success',
                'status': 'connected',
                'operation': 'insert_records'
            }
        })

        for name in name_list:
            # Find record by name
            cursor.execute("SELECT id FROM public.www_data_idx WHERE name_eng = %s AND source = 'ore_futures'", (name,))
            record = cursor.fetchone()

            if record is None:  # If record not found, insert new
                cursor.execute("SELECT MAX(id) FROM public.www_data_idx")
                max_id = cursor.fetchone()[0]

                if max_id is None:
                    max_id = 0

                new_id = max_id + 1
                current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Insert new record
                cursor.execute("INSERT INTO public.www_data_idx (id, mask, name_rus, name_eng, source, url, descr, date_upd) VALUES (%s, NULL, 'Iron Ore 62% Fe', %s, 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, %s)",
                               (new_id, name, current_date))
                logger.info("Record successfully added", extra={
                    'extra_data': {
                        'event_type': 'db_record_added',
                        'contract': name,
                        'new_id': new_id
                    }
                })

        conn.commit()

    except (Exception, psycopg2.Error) as error:
        logger.error("PostgreSQL error: %s", error, extra={
            'extra_data': {
                'event_type': 'db_operation_error',
                'operation': 'insert_records',
                'error': str(error)
            }
        })

    finally:
        # Close database connection
        if conn:
            cursor.close()
            conn.close()
            logger.info("PostgreSQL connection closed", extra={
                'extra_data': {
                    'event_type': 'db_connection_closed',
                    'operation': 'insert_records'
                }
            })

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
        
        logger.debug("Data inserted/updated in agriculture_moex", extra={
            'extra_data': {
                'event_type': 'db_data_upserted',
                'id_value': id_value,
                'date': data[1],
                'price': data[4]
            }
        })

def set_status_robot(id, health_status, add_text):
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

    except psycopg2.DatabaseError as e:
        print("Error at execute:")
        logger.error("Error at execute query: %s", query, extra={
            'extra_data': {
                'event_type': 'health_status_update_error',
                'error': str(e)
            }
        })
        logger.error("Database error: %s", e)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_current_date():
    
     # UTC+3 (Moscow time)
    current_time = datetime.now(timezone.utc) + timedelta(hours=3)
    return current_time.strftime("%Y-%m-%d %H:%M:%S MSK") + '\n'
    
    
def sync_to_elasticsearch():
    """Automatic data synchronization with Elasticsearch"""
    try:
        
        import psycopg2
        
        logger.info("Starting Elasticsearch synchronization...", extra={
            'extra_data': {
                'event_type': 'elasticsearch_sync_started'
            }
        })
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Select data from table
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
            
            # Send to Elasticsearch
            es.index(index='agriculture-data', document=doc)
            
            send_to_kafka(doc)
            synced_count += 1
            
        logger.info(f"SUCCESS Synchronization completed! Processed records: {synced_count}", extra={
            'extra_data': {
                'event_type': 'elasticsearch_sync_completed',
                'records_processed': synced_count,
                'status': 'success'
            }
        })
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"ERROR Elasticsearch synchronization error: {e}", extra={
            'extra_data': {
                'event_type': 'elasticsearch_sync_error',
                'error': str(e),
                'status': 'failed'
            }
        })



# Main code
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
    
    logger.info("Main script execution started", extra={
        'extra_data': {
            'event_type': 'main_script_started',
            'contracts_count': len(name_list),
            'interval': interval
        }
    })

    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    logger.info("Database connection established", extra={
        'extra_data': {
            'event_type': 'db_connection_success',
            'status': 'connected',
            'operation': 'main_data_processing'
        }
    })
    
    to_log_file("\nConnect to DB PostgreSQL: YES!!!\n", True)

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
                        logger.error('IndexError when processing data: %s', data, extra={
                            'extra_data': {
                                'event_type': 'data_processing_error',
                                'error_type': 'index_error',
                                'contract': row[1]
                            }
                        })
                        health_status = 0

            except Exception as e:
                logger.error("Exception: %s", e, extra={
                    'extra_data': {
                        'event_type': 'contract_processing_error',
                        'contract': row[1],
                        'error': str(e)
                    }
                })
                health_status = 0
                continue

    cursor.close()
    conn.commit()
    conn.close()

    to_log_file("\nFINISH RUN SCRIPT\n", True)
    logger.info("Health status: %s", health_status, extra={
        'extra_data': {
            'event_type': 'script_execution_completed',
            'health_status': health_status,
            'final_status': 'success' if health_status == 100 else 'with_errors'
        }
    })
    set_status_robot(1012, health_status, '')
    sync_to_elasticsearch()
    
    logger.info("Main script execution finished", extra={
        'extra_data': {
            'event_type': 'main_script_finished',
            'health_status': health_status,
            'status': 'completed'
        }
    })

except psycopg2.DatabaseError as e:
    health_status = 0
    to_log_file("\nConnect to DB PostgreSQL: NO!!!\n", True)
    to_log_file(str(e), True)
    
    logger.error("Database connection failed", extra={
        'extra_data': {
            'event_type': 'db_connection_failed',
            'error': str(e),
            'health_status': health_status
        }
    })
    
    set_status_robot(1012, health_status, '')