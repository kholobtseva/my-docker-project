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

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            logger.info("SUCCESS DLQ producer initialized")
        except Exception as e:
            logger.error(f"ERROR Failed to initialize DLQ producer: {e}")
            self.producer = None
    
    def send_to_dlq(self, original_message, error_reason, raw_value=None):
        """Send invalid message to DLQ"""
        if not self.producer:
            logger.error("DLQ producer not available")
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
            logger.warning(f"DLQ Sent invalid message to DLQ: {error_reason}")
            return True
        except Exception as e:
            logger.error(f"ERROR Failed to send to DLQ: {e}")
            return False

def normalize_value(value, default=''):
    """Normalizes value - trimming and converting to string"""
    if value is None:
        return default
    return str(value).strip()

def validate_payload(payload):
    """Validate required fields in payload including date format"""
    if not payload:
        logger.error("ERROR Empty payload")
        return False, "Empty payload"
    
    # Проверка обязательных полей
    required_fields = ['contract', 'date', 'price']
    for field in required_fields:
        if field not in payload:
            logger.warning(f"WARNING Missing required field: {field}")
            return False, f"Missing required field: {field}"
    
    # Валидация формата даты
    date_value = payload.get('date')
    if not validate_date_format(date_value):
        logger.warning(f"WARNING Invalid date format: {date_value}")
        return False, f"Invalid date format: {date_value}. Expected YYYY-MM-DD"
    
    # Валидация по JSON схеме
    try:
        validate(instance=payload, schema=DATA_SCHEMA)
        return True, "Valid"
    except jsonschema.ValidationError as e:
        logger.warning(f"WARNING Schema validation failed: {e.message}")
        return False, f"Schema validation failed: {e.message}"
    except Exception as e:
        logger.warning(f"WARNING Validation error: {e}")
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
            logger.error(f"ERROR Invalid payload: {validation_msg}")
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
                logger.info("INFO CSV headers written")
            
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
        
        logger.info(f"SAVED Data saved to CSV: {filepath}")
        return True
        
    except Exception as e:
        logger.error(f"ERROR CSV save error: {e}")
        return False

def process_message(message, message_count, dlq_producer):
    """Process single Kafka message with error handling"""
    try:
        # РУЧНОЙ ПАРСИНГ JSON с обработкой ошибок
        try:
            data = json.loads(message.value.decode('utf-8'))
        except json.JSONDecodeError as e:
            logger.error(f"ERROR JSON decode error in message #{message_count}: {e}")
            dlq_producer.send_to_dlq(
                original_message=None,
                error_reason=f"JSON decode error: {str(e)}",
                raw_value=message.value.decode('utf-8', errors='replace')[:500]
            )
            return False
        
        logger.info(f"RECEIVED Message #{message_count}: {data.get('contract', 'Unknown')} - {data.get('date', 'No date')}")
        
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
            logger.debug(f"SAVED Message #{message_count} saved to CSV")
            return True
        else:
            logger.error(f"ERROR Failed to save message #{message_count}")
            return False
            
    except Exception as e:
        logger.error(f"ERROR Message processing error #{message_count}: {e}")
        dlq_producer.send_to_dlq(
            original_message=None,
            error_reason=f"Processing error: {str(e)}",
            raw_value=message.value.decode('utf-8', errors='replace')[:500] if hasattr(message, 'value') else "No message value"
        )
        return False

def run_consumer():
    """Main consumer function with robust error handling"""
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
            
            logger.info("STARTED Kafka consumer started and waiting for messages...")
            break
            
        except NoBrokersAvailable as e:
            logger.warning(f"WARNING Kafka brokers not available (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                logger.error("ERROR Failed to connect to Kafka after all retries")
                return
        except Exception as e:
            logger.error(f"ERROR Consumer initialization error: {e}")
            return
    
    # Graceful shutdown handler
    def shutdown_handler(signum, frame):
        logger.info("STOP Consumer shutdown initiated")
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
                    logger.info(f"PROCESSED Message #{message_count} processed successfully")
                else:
                    logger.warning(f"SKIPPED Message #{message_count} skipped due to errors")
            except Exception as e:
                logger.error(f"ERROR Failed to process message #{message_count}: {e}")
                # Отправляем в DLQ
                raw_value = message.value.decode('utf-8', errors='replace')[:500] if hasattr(message, 'value') else "No message value"
                dlq_producer.send_to_dlq(
                    original_message=None,
                    error_reason=f"Message processing failed: {str(e)}",
                    raw_value=raw_value
                )
                continue  # Продолжаем работу
                
    except KeyboardInterrupt:
        logger.info("STOP Consumer stopped by user")
    except Exception as e:
        logger.error(f"ERROR Critical consumer error: {e}")
    finally:
        consumer.close()
        if dlq_producer.producer:
            dlq_producer.producer.close()
        logger.info("STOP Consumer stopped gracefully")

if __name__ == "__main__":
    run_consumer()