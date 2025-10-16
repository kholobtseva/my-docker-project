import json
import csv
import os
from datetime import datetime
from kafka import KafkaConsumer

from core.validation_utils import UniversalDataValidator
from core.kafka_utils import KafkaManager

def run_moex_consumer():
    print("🚀 Starting MOEX Kafka Consumer...")
    
    kafka_manager = KafkaManager()
    validator = UniversalDataValidator(kafka_manager, 'moex_consumer')
    
    try:
        consumer = KafkaConsumer(
            'moex-market-data',
            bootstrap_servers=['kafka:9092'],
            group_id='moex_csv_writer_group',
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        
        print("Connected to Kafka")
        print("Waiting for MOEX messages...")
        
        log_dir = '/app/logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        csv_file = os.path.join(log_dir, 'kafka_messages_moex.csv')
        
        message_count = 0
        valid_count = 0
        invalid_count = 0
        
        if not os.path.exists(csv_file):
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow([
                    'kafka_timestamp', 'message_offset', 'message_count',
                    'id_value', 'contract', 'date', 'price', 'volume', 'currency',
                    'name_rus', 'source', 'sync_timestamp'
                ])
            print(f"Created new CSV file: {csv_file}")
        
        for message in consumer:
            message_count += 1
            
            data = message.value
            
            print(f"\nReceived Message #{message_count}")
            print(f"   ID: {data.get('id_value', 'N/A')} (type: {type(data.get('id_value'))})")
            print(f"   Contract: {data.get('contract', 'MISSING')}")
            print(f"   Date: {data.get('date', 'N/A')}")
            print(f"   Price: {data.get('price', 'N/A')}")
            
            is_valid, errors = validator.validate_for_kafka(data)
            
            if not is_valid:
                print(f"VALIDATION FAILED: {errors}")
                
                dlq_result = validator.send_to_dead_letter_queue(
                    data,
                    errors,
                    'moex-market-data',
                    'moex'
                )
                
                if dlq_result:
                    print(f"✅ Sent to DLQ")
                else:
                    print(f"❌ FAILED to send to DLQ")
                
                invalid_count += 1
                print(f"📊 Stats: Total: {message_count}, Valid: {valid_count}, Invalid: {invalid_count}")
                continue
            
            print("✅ VALIDATION PASSED")
            
            try:
                with open(csv_file, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f, delimiter=';')
                    writer.writerow([
                        datetime.now().isoformat(),
                        message.offset,
                        message_count,
                        data.get('id_value', ''),
                        data.get('contract', ''),
                        data.get('date', ''),
                        data.get('price', ''),
                        data.get('volume', ''),
                        data.get('currency', ''),
                        data.get('name_rus', ''),
                        data.get('source', ''),
                        data.get('sync_timestamp', '')
                    ])
                print(f"💾 Saved to CSV: {csv_file}")
            except Exception as e:
                print(f"❌ FAILED to save to CSV: {e}")
            
            valid_count += 1
            print(f"📊 Stats: Total: {message_count}, Valid: {valid_count}, Invalid: {invalid_count}")
            
    except KeyboardInterrupt:
        print(f"\n🛑 Consumer stopped by user")
    except Exception as e:
        print(f"\n💥 FATAL ERROR: {e}")
    finally:
        print(f"\n📈 FINAL STATS: Total: {message_count}, Valid: {valid_count}, Invalid: {invalid_count}")
        try:
            consumer.close()
            print("🔌 Connections closed")
        except:
            pass

if __name__ == "__main__":
    run_moex_consumer()