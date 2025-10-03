import json
import logging
import csv
import os
import time
from datetime import datetime
from kafka import KafkaConsumer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def normalize_value(value, default=''):
    """Нормализует значение - тримминг и приведение к строке"""
    if value is None:
        return default
    return str(value).strip()

def validate_payload(payload):
    """Валидация обязательных полей в payload"""
    if not payload:
        logger.error("❌ Пустой payload")
        return False
        
    required_fields = ['contract', 'date', 'price']
    for field in required_fields:
        if field not in payload:
            logger.warning(f"⚠️ Отсутствует обязательное поле: {field}")
            return False
            
    # Дополнительная проверка типов данных
    if not isinstance(payload.get('contract'), str):
        logger.warning("⚠️ Поле contract должно быть строкой")
        return False
        
    return True

def save_to_csv(data, filename='kafka_messages.csv'):
    """Сохраняет данные в CSV файл с валидацией и нормализацией"""
    try:
        log_dir = '/app/logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        filepath = os.path.join(log_dir, filename)
        
        # Проверяем обязательные поля
        payload = data.get('payload', {})
        if not validate_payload(payload):
            logger.error("❌ Некорректный payload, пропускаем сообщение")
            return False
        
        # Улучшенная проверка файла - всегда пишем заголовки для пустого файла
        file_exists = os.path.isfile(filepath)
        if file_exists:
            # Проверяем не пустой ли файл
            is_empty = os.path.getsize(filepath) == 0
            mode = 'a' if not is_empty else 'w'
        else:
            mode = 'w'
            is_empty = True
        
        with open(filepath, mode, newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            
            # Записываем заголовок если файл новый ИЛИ пустой
            if mode == 'w' or is_empty:
                headers = [
                    'kafka_timestamp', 'message_offset', 'message_count',
                    'contract', 'date', 'price', 'volume', 'currency',
                    'name_rus', 'source', 'sync_timestamp'
                ]
                writer.writerow(headers)
                logger.info("📄 Заголовки CSV записаны")
            
            # Нормализованное извлечение данных
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
        
        logger.info(f"💾 Данные сохранены в CSV: {filepath}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения в CSV: {e}")
        return False

def process_message(message, message_count):
    """Обработка одного сообщения из Kafka"""
    try:
        data = message.value
        logger.info(f"📨 Получено сообщение #{message_count}: {data.get('contract', 'Unknown')} - {data.get('date', 'No date')}")
        
        # Подготавливаем данные для CSV
        enriched_data = {
            'kafka_timestamp': datetime.now().isoformat(),
            'message_offset': message.offset,
            'message_count': message_count,
            'payload': data
        }
        
        # Сохраняем в CSV
        if save_to_csv(enriched_data):
            logger.debug(f"✅ Сообщение #{message_count} сохранено в CSV")
            return True
        else:
            logger.error(f"❌ Ошибка сохранения сообщения #{message_count}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Ошибка обработки сообщения #{message_count}: {e}")
        return False

def run_consumer():
    """Основная функция запуска consumer"""
    try:
        consumer = KafkaConsumer(
            'market-data',
            bootstrap_servers=['kafka:9092'],
            auto_offset_reset='latest',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='csv_writer_group',
            enable_auto_commit=True
        )
        
        logger.info("✅ Kafka consumer запущен и ожидает новые сообщения...")
        
        # Создаем CSV файл с заголовком при первом запуске
        csv_file = '/app/logs/kafka_messages.csv'
        try:
            # Удаляем старый файл чтобы создать новый с заголовками
            if os.path.exists(csv_file):
                os.remove(csv_file)
                logger.info("🗑️ Удален старый CSV файл для создания нового с заголовками")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось удалить старый CSV: {e}")
        
        message_count = 0
        
        # Бесконечный цикл ожидания сообщений
        for message in consumer:
            message_count += 1
            process_message(message, message_count)
                
    except KeyboardInterrupt:
        logger.info("🛑 Consumer остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка consumer: {e}")
        raise

if __name__ == "__main__":
    run_consumer()