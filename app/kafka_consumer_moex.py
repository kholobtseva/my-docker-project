# app/kafka_consumer_moex.py
import json
import csv
import os
import time
from datetime import datetime
from kafka import KafkaConsumer

def run_moex_consumer():
    print("🚀 Starting MOEX Kafka Consumer...")
    
    # Создаем консюмер для MOEX топика
    consumer = KafkaConsumer(
        'moex-market-data',
        bootstrap_servers=['kafka:9092'],
        group_id='moex_csv_writer_group',
        auto_offset_reset='earliest',
        enable_auto_commit=True
    )
    
    print("✅ Connected to Kafka")
    print("📊 Waiting for MOEX messages...")
    
    # Создаем папку для логов если нет
    log_dir = '/app/logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    csv_file = os.path.join(log_dir, 'kafka_messages_moex.csv')
    
    # Счетчик сообщений
    message_count = 0
    
    try:
        for message in consumer:
            message_count += 1
            
            # Парсим сообщение
            data = json.loads(message.value.decode('utf-8'))
            
            print(f"📨 Message {message_count}: {data.get('contract')} - {data.get('date')} - {data.get('price')}")
            
            # Записываем в CSV
            file_exists = os.path.isfile(csv_file)
            
            with open(csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=';')
                
                # Записываем заголовок если файл новый
                if not file_exists:
                    writer.writerow([
                        'kafka_timestamp', 'message_offset', 'message_count',
                        'contract', 'date', 'price', 'volume', 'currency',
                        'name_rus', 'source', 'sync_timestamp'
                    ])
                
                # Записываем данные
                writer.writerow([
                    datetime.now().isoformat(),
                    message.offset,
                    message_count,
                    data.get('contract', ''),
                    data.get('date', ''),
                    data.get('price', ''),
                    data.get('volume', ''),
                    data.get('currency', ''),
                    data.get('name_rus', ''),
                    data.get('source', ''),
                    data.get('sync_timestamp', '')
                ])
            
            print(f"✅ Saved to CSV: {csv_file}")
            
    except KeyboardInterrupt:
        print(f"🛑 Consumer stopped. Processed {message_count} messages")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        consumer.close()

if __name__ == "__main__":
    run_moex_consumer()