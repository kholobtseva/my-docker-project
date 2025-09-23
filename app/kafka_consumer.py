import json
import logging
import csv
import os
import time
from datetime import datetime
from kafka import KafkaConsumer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_to_csv(data, filename='kafka_messages.csv'):
    """Сохраняет данные в CSV файл"""
    try:
        log_dir = '/app/logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        filepath = os.path.join(log_dir, filename)
        file_exists = os.path.isfile(filepath)
        
        with open(filepath, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            
            # Записываем заголовок если файл новый
            if not file_exists:
                headers = [
                    'kafka_timestamp', 'message_offset', 'message_count',
                    'contract', 'date', 'price', 'volume', 'currency',
                    'name_rus', 'source', 'sync_timestamp'
                ]
                writer.writerow(headers)
            
            # Извлекаем данные из payload
            payload = data.get('payload', {})
            row = [
                data.get('kafka_timestamp', ''),
                data.get('message_offset', ''),
                data.get('message_count', ''),
                payload.get('contract', ''),
                payload.get('date', ''),
                payload.get('price', ''),
                payload.get('volume', ''),
                payload.get('currency', ''),
                payload.get('name_rus', ''),
                payload.get('source', ''),
                payload.get('sync_timestamp', '')
            ]
            
            writer.writerow(row)
        
        logger.info(f"💾 Данные сохранены в CSV: {filepath}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения в CSV: {e}")
        return False

def run_consumer():
    try:
        consumer = KafkaConsumer(
            'market-data',
            bootstrap_servers=['kafka:9092'],
            auto_offset_reset='latest',  # ← ИЗМЕНИЛ НА LATEST
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='csv_writer_group'
        )
        
        logger.info("✅ Kafka consumer запущен и ожидает новые сообщения...")
        
        # Создаем CSV файл с заголовком при первом запуске
        csv_file = '/app/logs/kafka_messages.csv'
        if not os.path.exists(csv_file):
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=';')
                headers = [
                    'kafka_timestamp', 'message_offset', 'message_count',
                    'contract', 'date', 'price', 'volume', 'currency',
                    'name_rus', 'source', 'sync_timestamp'
                ]
                writer.writerow(headers)
        
        message_count = 0
        
        # Бесконечный цикл ожидания сообщений
        for message in consumer:
            data = message.value
            message_count += 1
            
            # Подготавливаем данные для CSV
            enriched_data = {
                'kafka_timestamp': datetime.now().isoformat(),
                'message_offset': message.offset,
                'message_count': message_count,
                'payload': data
            }
            
            logger.info(f"📨 Получено сообщение #{message_count}: {data.get('contract', 'Unknown')} - {data.get('date', 'No date')}")
            
            # Сохраняем в CSV
            if save_to_csv(enriched_data):
                logger.debug(f"✅ Сообщение #{message_count} сохранено в CSV")
            else:
                logger.error(f"❌ Ошибка сохранения сообщения #{message_count}")
                
    except KeyboardInterrupt:
        logger.info("🛑 Consumer остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Ошибка consumer: {e}")

if __name__ == "__main__":
    run_consumer()