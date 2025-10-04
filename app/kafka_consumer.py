import json
import logging
import csv
import os
import time
from datetime import datetime
from kafka import KafkaConsumer
import sys
import io


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if sys.stdout.encoding != 'UTF-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'UTF-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def normalize_value(value, default=''):
    """Normalizes value - trimming and converting to string"""
    if value is None:
        return default
    return str(value).strip()

def validate_payload(payload):
    """Validate required fields in payload"""
    if not payload:
        logger.error("ERROR Empty payload")
        return False
        
    required_fields = ['contract', 'date', 'price']
    for field in required_fields:
        if field not in payload:
            logger.warning(f"WARNING Missing required field: {field}")
            return False
            
    # Additional data type validation
    if not isinstance(payload.get('contract'), str):
        logger.warning("WARNING Contract field must be string")
        return False
        
    return True

def save_to_csv(data, filename='kafka_messages.csv'):
    """Save data to CSV file with validation and normalization"""
    try:
        log_dir = '/app/logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        filepath = os.path.join(log_dir, filename)
        
        # Check required fields
        payload = data.get('payload', {})
        if not validate_payload(payload):
            logger.error("ERROR Invalid payload, skipping message")
            return False
        
        # Improved file check - always write headers for empty file
        file_exists = os.path.isfile(filepath)
        if file_exists:
            # Check if file is empty
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

def process_message(message, message_count):
    """Process single Kafka message"""
    try:
        data = message.value
        logger.info(f"RECEIVED Message #{message_count}: {data.get('contract', 'Unknown')} - {data.get('date', 'No date')}")
        
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
        return False

def run_consumer():
    """Main consumer function"""
    try:
        consumer = KafkaConsumer(
            'market-data',
            bootstrap_servers=['kafka:9092'],
            auto_offset_reset='latest',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='csv_writer_group',
            enable_auto_commit=True
        )
        
        logger.info("STARTED Kafka consumer started and waiting for messages...")
        
        # Create CSV file with headers on first run
        csv_file = '/app/logs/kafka_messages.csv'
        try:
            # Remove old file to create new one with headers
            if os.path.exists(csv_file):
                os.remove(csv_file)
                logger.info("CLEANED Old CSV file removed for fresh start with headers")
        except Exception as e:
            logger.warning(f"WARNING Failed to remove old CSV: {e}")
        
        message_count = 0
        
        # Infinite message loop
        for message in consumer:
            message_count += 1
            process_message(message, message_count)
                
    except KeyboardInterrupt:
        logger.info("STOP Consumer stopped by user")
    except Exception as e:
        logger.error(f"ERROR Critical consumer error: {e}")
        raise

if __name__ == "__main__":
    run_consumer()