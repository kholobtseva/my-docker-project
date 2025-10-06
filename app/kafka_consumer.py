import json
import logging
import csv
import os
import time
import signal
import sys
from datetime import datetime
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import NoBrokersAvailable
import jsonschema
from jsonschema import validate
from elasticsearch import Elasticsearch


# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Структурированный форматтер для Elasticsearch
class ElasticsearchJSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': record.levelname,
            'logger': 'kafka_consumer',
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName
        }
        
        # Добавляем extra данные если есть
        if hasattr(record, 'extra_data'):
            log_entry.update(record.extra_data)
            
        return json.dumps(log_entry)
        
# Клиент для логов (отдельный от основного)
es_logs = Elasticsearch(['http://elasticsearch:9200'])

class ElasticsearchLogHandler(logging.Handler):
    def emit(self, record):
        try:
            log_entry = json.loads(self.format(record))
            es_logs.index(index='kafka-consumer-logs', body=log_entry)
        except Exception as e:
            # Если не получится отправить в ES - логи просто пропадут, но пайплайн продолжит работу
            pass

# Добавляем хендлер (основное логирование в stdout останется)
es_handler = ElasticsearchLogHandler()
es_handler.setFormatter(ElasticsearchJSONFormatter())
logger.addHandler(es_handler)
        


# Настройка JSON логгера
json_handler = logging.StreamHandler()
json_handler.setFormatter(ElasticsearchJSONFormatter())
logger.addHandler(json_handler)

# Data validation schema
DATA_SCHEMA = {
    "type": "object",
    "properties": {
        "id_value": {"type": "number"},
        "date": {"type": "string", "format": "date"},
        "price": {"type": "number"},
        "contract": {"type": "string"},
        "name_rus": {"type": "string"},
        "source": {"type": "string"},
        "volume": {"type": ["number", "null"]},
        "currency": {"type": "string"},
        "sync_timestamp": {"type": "string"}
    },
    "required": ["id_value", "date", "price", "contract", "name_rus", "source", "currency", "sync_timestamp"]
}

def validate_date_format(date_str):
    """Validate date format (YYYY-MM-DD)"""
    if not date_str or not isinstance(date_str, str):
        return False
        
    try:
        # Пробуем распарсить дату в формате YYYY-MM-DD
        parsed_date = datetime.strptime(date_str, '%Y-%m-%d')
        
        # Дополнительная проверка что это реальная дата (не 2024-02-30)
        if (parsed_date.year < 1900 or parsed_date.year > 2100 or
            parsed_date.month < 1 or parsed_date.month > 12 or
            parsed_date.day < 1 or parsed_date.day > 31):
            return False
            
        return True
    except ValueError:
        return False

class DeadLetterQueueProducer:
    def __init__(self, bootstrap_servers):
        self.producer = None
        self.bootstrap_servers = bootstrap_servers
        self._initialize_producer()
    
    def _initialize_producer(self):
        """Initialize DLQ producer"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8')
            )
            logger.info("SUCCESS DLQ producer initialized", extra={
                'extra_data': {
                    'event_type': 'dlq_producer_initialized',
                    'status': 'success'
                }
            })
        except Exception as e:
            logger.error("ERROR Failed to initialize DLQ producer", extra={
                'extra_data': {
                    'event_type': 'dlq_producer_error',
                    'error': str(e),
                    'status': 'failed'
                }
            })
            self.producer = None
    
    def send_to_dlq(self, original_message, error_reason, raw_value=None):
        """Send invalid message to DLQ"""
        if not self.producer:
            logger.error("DLQ producer not available", extra={
                'extra_data': {
                    'event_type': 'dlq_send_failed',
                    'reason': 'producer_not_available'
                }
            })
            return False
            
        dlq_message = {
            "original_message": original_message if original_message else "Unable to parse",
            "raw_value": raw_value if raw_value else "Not available",
            "error_reason": error_reason,
            "timestamp": datetime.now().isoformat(),
            "dlq_topic": "market-data-dlq"
        }
        
        try:
            future = self.producer.send('market-data-dlq', dlq_message)
            future.get(timeout=10)
            logger.warning("DLQ Sent invalid message to DLQ", extra={
                'extra_data': {
                    'event_type': 'dlq_message_sent',
                    'error_reason': error_reason,
                    'dlq_topic': 'market-data-dlq'
                }
            })
            return True
        except Exception as e:
            logger.error("ERROR Failed to send to DLQ", extra={
                'extra_data': {
                    'event_type': 'dlq_send_error',
                    'error': str(e),
                    'error_reason': error_reason
                }
            })
            return False

def normalize_value(value, default=''):
    """Normalizes value - trimming and converting to string"""
    if value is None:
        return default
    return str(value).strip()

def validate_payload(payload):
    """Validate required fields in payload including date format"""
    if not payload:
        logger.error("ERROR Empty payload", extra={
            'extra_data': {
                'event_type': 'validation_error',
                'error_type': 'empty_payload'
            }
        })
        return False, "Empty payload"
    
    # Проверка обязательных полей
    required_fields = ['contract', 'date', 'price']
    for field in required_fields:
        if field not in payload:
            logger.warning("WARNING Missing required field", extra={
                'extra_data': {
                    'event_type': 'validation_warning',
                    'missing_field': field,
                    'payload_keys': list(payload.keys())
                }
            })
            return False, f"Missing required field: {field}"
    
    # Валидация формата даты
    date_value = payload.get('date')
    if not validate_date_format(date_value):
        logger.warning("WARNING Invalid date format", extra={
            'extra_data': {
                'event_type': 'validation_warning',
                'error_type': 'invalid_date_format',
                'date_value': date_value
            }
        })
        return False, f"Invalid date format: {date_value}. Expected YYYY-MM-DD"
    
    # Валидация по JSON схеме
    try:
        validate(instance=payload, schema=DATA_SCHEMA)
        return True, "Valid"
    except jsonschema.ValidationError as e:
        logger.warning("WARNING Schema validation failed", extra={
            'extra_data': {
                'event_type': 'schema_validation_failed',
                'error': e.message,
                'validator': e.validator
            }
        })
        return False, f"Schema validation failed: {e.message}"
    except Exception as e:
        logger.warning("WARNING Validation error", extra={
            'extra_data': {
                'event_type': 'validation_error',
                'error_type': 'general_validation_error',
                'error': str(e)
            }
        })
        return False, f"Validation error: {str(e)}"

def save_to_csv(data, filename='kafka_messages.csv'):
    """Save data to CSV file with validation and normalization"""
    try:
        log_dir = '/app/logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        filepath = os.path.join(log_dir, filename)
        
        # Check required fields
        payload = data.get('payload', {})
        is_valid, validation_msg = validate_payload(payload)
        if not is_valid:
            logger.error("ERROR Invalid payload", extra={
                'extra_data': {
                    'event_type': 'csv_save_failed',
                    'reason': 'invalid_payload',
                    'validation_msg': validation_msg,
                    'contract': payload.get('contract')
                }
            })
            return False
        
        # Improved file check - always write headers for empty file
        file_exists = os.path.isfile(filepath)
        if file_exists:
            is_empty = os.path.getsize(filepath) == 0
            mode = 'a' if not is_empty else 'w'
        else:
            mode = 'w'
            is_empty = True
        
        with open(filepath, mode, newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            
            # Write headers if file is new OR empty
            if mode == 'w' or is_empty:
                headers = [
                    'kafka_timestamp', 'message_offset', 'message_count',
                    'contract', 'date', 'price', 'volume', 'currency',
                    'name_rus', 'source', 'sync_timestamp'
                ]
                writer.writerow(headers)
                logger.info("INFO CSV headers written", extra={
                    'extra_data': {
                        'event_type': 'csv_headers_written',
                        'filepath': filepath,
                        'headers': headers
                    }
                })
            
            # Normalized data extraction
            row = [
                normalize_value(data.get('kafka_timestamp'), datetime.now().isoformat()),
                normalize_value(data.get('message_offset')),
                normalize_value(data.get('message_count')),
                normalize_value(payload.get('contract'), 'MISSING'),
                normalize_value(payload.get('date'), 'MISSING'),
                normalize_value(payload.get('price'), 'MISSING'),
                normalize_value(payload.get('volume')),
                normalize_value(payload.get('currency')),
                normalize_value(payload.get('name_rus')),
                normalize_value(payload.get('source')),
                normalize_value(payload.get('sync_timestamp'), datetime.now().isoformat())
            ]
            
            writer.writerow(row)
        
        logger.info("SAVED Data saved to CSV", extra={
            'extra_data': {
                'event_type': 'csv_save_success',
                'filepath': filepath,
                'contract': payload.get('contract'),
                'date': payload.get('date'),
                'price': payload.get('price')
            }
        })
        return True
        
    except Exception as e:
        logger.error("ERROR CSV save error", extra={
            'extra_data': {
                'event_type': 'csv_save_error',
                'error': str(e),
                'filepath': filepath,
                'contract': payload.get('contract') if payload else 'unknown'
            }
        })
        return False

def process_message(message, message_count, dlq_producer):
    """Process single Kafka message with error handling"""
    start_time = datetime.now()
    try:
        # РУЧНОЙ ПАРСИНГ JSON с обработкой ошибок
        try:
            data = json.loads(message.value.decode('utf-8'))
        except json.JSONDecodeError as e:
            logger.error("ERROR JSON decode error", extra={
                'extra_data': {
                    'event_type': 'json_decode_error',
                    'message_count': message_count,
                    'error': str(e),
                    'raw_value_preview': message.value.decode('utf-8', errors='replace')[:200]
                }
            })
            dlq_producer.send_to_dlq(
                original_message=None,
                error_reason=f"JSON decode error: {str(e)}",
                raw_value=message.value.decode('utf-8', errors='replace')[:500]
            )
            return False
        
        logger.info("Message received", extra={
            'extra_data': {
                'event_type': 'kafka_message_received',
                'contract': data.get('contract'),
                'date': data.get('date'),
                'price': data.get('price'),
                'message_count': message_count,
                'offset': message.offset
            }
        })
        
        # Validate data schema
        is_valid, validation_msg = validate_payload(data)
        if not is_valid:
            dlq_producer.send_to_dlq(
                original_message=data,
                error_reason=validation_msg,
                raw_value=str(data)[:500]
            )
            return False
        
        # Prepare data for CSV
        enriched_data = {
            'kafka_timestamp': datetime.now().isoformat(),
            'message_offset': message.offset,
            'message_count': message_count,
            'payload': data
        }
        
        # Save to CSV
        if save_to_csv(enriched_data):
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            logger.info("Message processed successfully", extra={
                'extra_data': {
                    'event_type': 'kafka_message_processed',
                    'contract': data.get('contract'),
                    'date': data.get('date'),
                    'price': data.get('price'),
                    'message_count': message_count,
                    'processing_time_ms': processing_time,
                    'status': 'success'
                }
            })
            return True
        else:
            logger.error("ERROR Failed to save message", extra={
                'extra_data': {
                    'event_type': 'message_processing_failed',
                    'contract': data.get('contract'),
                    'message_count': message_count,
                    'reason': 'csv_save_failed'
                }
            })
            return False
            
    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        logger.error("ERROR Message processing error", extra={
            'extra_data': {
                'event_type': 'message_processing_error',
                'message_count': message_count,
                'error_type': type(e).__name__,
                'error': str(e),
                'processing_time_ms': processing_time,
                'contract': data.get('contract') if 'data' in locals() else 'unknown'
            }
        })
        dlq_producer.send_to_dlq(
            original_message=None,
            error_reason=f"Processing error: {str(e)}",
            raw_value=message.value.decode('utf-8', errors='replace')[:500] if hasattr(message, 'value') else "No message value"
        )
        return False

def run_consumer():
    """Main consumer function with robust error handling"""
    logger.info("Starting Kafka consumer", extra={
        'extra_data': {
            'event_type': 'consumer_startup',
            'timestamp': datetime.now().isoformat()
        }
    })
    
    dlq_producer = DeadLetterQueueProducer(['kafka:9092'])
    
    # Retry logic for consumer initialization
    max_retries = 5
    retry_delay = 10
    
    for attempt in range(max_retries):
        try:
            consumer = KafkaConsumer(
                'market-data',
                bootstrap_servers=['kafka:9092'],
                auto_offset_reset='earliest',
                value_deserializer=lambda m: m,  # СЫРЫЕ БАЙТЫ вместо автоматического парсинга
                group_id='csv_writer_group',
                enable_auto_commit=True,
                session_timeout_ms=30000,
                heartbeat_interval_ms=10000
            )
            
            logger.info("STARTED Kafka consumer started", extra={
                'extra_data': {
                    'event_type': 'consumer_initialized',
                    'status': 'success',
                    'attempt': attempt + 1,
                    'topic': 'market-data',
                    'group_id': 'csv_writer_group'
                }
            })
            break
            
        except NoBrokersAvailable as e:
            logger.warning("WARNING Kafka brokers not available", extra={
                'extra_data': {
                    'event_type': 'broker_connection_retry',
                    'attempt': attempt + 1,
                    'max_retries': max_retries,
                    'error': str(e)
                }
            })
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                logger.error("ERROR Failed to connect to Kafka after all retries", extra={
                    'extra_data': {
                        'event_type': 'broker_connection_failed',
                        'retries': max_retries,
                        'final_error': str(e)
                    }
                })
                return
        except Exception as e:
            logger.error("ERROR Consumer initialization error", extra={
                'extra_data': {
                    'event_type': 'consumer_init_error',
                    'error': str(e)
                }
            })
            return
    
    # Graceful shutdown handler
    def shutdown_handler(signum, frame):
        logger.info("STOP Consumer shutdown initiated", extra={
            'extra_data': {
                'event_type': 'consumer_shutdown',
                'signal': signum,
                'total_messages_processed': message_count
            }
        })
        consumer.close()
        if dlq_producer.producer:
            dlq_producer.producer.close()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)
    
    message_count = 0
    
    try:
        # Main message processing loop
        for message in consumer:
            message_count += 1
            try:
                success = process_message(message, message_count, dlq_producer)
                if success:
                    logger.debug("Message processed successfully", extra={
                        'extra_data': {
                            'event_type': 'message_processing_complete',
                            'message_count': message_count,
                            'status': 'success'
                        }
                    })
                else:
                    logger.warning("SKIPPED Message skipped due to errors", extra={
                        'extra_data': {
                            'event_type': 'message_skipped',
                            'message_count': message_count,
                            'status': 'skipped'
                        }
                    })
            except Exception as e:
                logger.error("ERROR Failed to process message", extra={
                    'extra_data': {
                        'event_type': 'message_processing_critical_error',
                        'message_count': message_count,
                        'error': str(e)
                    }
                })
                # Отправляем в DLQ
                raw_value = message.value.decode('utf-8', errors='replace')[:500] if hasattr(message, 'value') else "No message value"
                dlq_producer.send_to_dlq(
                    original_message=None,
                    error_reason=f"Message processing failed: {str(e)}",
                    raw_value=raw_value
                )
                continue  # Продолжаем работу
                
    except KeyboardInterrupt:
        logger.info("STOP Consumer stopped by user", extra={
            'extra_data': {
                'event_type': 'consumer_stopped_by_user',
                'total_messages_processed': message_count
            }
        })
    except Exception as e:
        logger.error("ERROR Critical consumer error", extra={
            'extra_data': {
                'event_type': 'consumer_critical_error',
                'error': str(e),
                'total_messages_processed': message_count
            }
        })
    finally:
        consumer.close()
        if dlq_producer.producer:
            dlq_producer.producer.close()
        logger.info("STOP Consumer stopped gracefully", extra={
            'extra_data': {
                'event_type': 'consumer_stopped',
                'total_messages_processed': message_count,
                'final_status': 'completed'
            }
        })

if __name__ == "__main__":
    run_consumer()