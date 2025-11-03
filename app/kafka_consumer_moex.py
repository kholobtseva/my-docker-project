import json
import csv
import os
from datetime import datetime
from kafka import KafkaConsumer

from core.validation_utils import UniversalDataValidator
from core.kafka_utils import KafkaManager
from core.logging_utils import setup_logging, setup_graylog_logger

# Настройка логирования для Graylog
logger = setup_logging('moex_consumer')
graylog_logger = setup_graylog_logger('moex_consumer')

def run_moex_consumer():
    logger.info("Starting MOEX Kafka Consumer", extra={
        'extra_data': {
            'event_type': 'consumer_startup',
            'timestamp': datetime.now().isoformat()
        }
    })
    
    kafka_manager = KafkaManager()
    validator = UniversalDataValidator(kafka_manager, 'moex_consumer')
    
    try:
        consumer = KafkaConsumer(
            'moex-market-data',
            bootstrap_servers=['kafka:9092'],
            group_id='moex_csv_writer_group',
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')) if x is not None else None
        )
        
        logger.info("Connected to Kafka", extra={
            'extra_data': {
                'event_type': 'kafka_connected',
                'topic': 'moex-market-data'
            }
        })
        
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
            logger.info("Created new CSV file", extra={
                'extra_data': {
                    'event_type': 'csv_file_created',
                    'filepath': csv_file
                }
            })
        
        for message in consumer:
            message_count += 1
            
            # Обработка пустых сообщений
            if message.value is None:
                logger.warning("Received empty message", extra={
                    'extra_data': {
                        'event_type': 'empty_message_received',
                        'message_count': message_count,
                        'offset': message.offset
                    }
                })
                
                dlq_result = validator.send_to_dead_letter_queue(
                    {"error": "empty_message", "offset": message.offset},
                    ["Empty message (None value)"],
                    'moex-market-data',
                    'moex'
                )
                
                if dlq_result:
                    logger.info("Empty message sent to DLQ", extra={
                        'extra_data': {
                            'event_type': 'dlq_message_sent',
                            'message_count': message_count,
                            'error_reason': 'Empty message (None value)'
                        }
                    })
                else:
                    logger.error("Failed to send empty message to DLQ", extra={
                        'extra_data': {
                            'event_type': 'dlq_send_failed',
                            'message_count': message_count
                        }
                    })
                
                invalid_count += 1
                logger.info("Message statistics", extra={
                    'extra_data': {
                        'event_type': 'message_stats',
                        'total': message_count,
                        'valid': valid_count,
                        'invalid': invalid_count
                    }
                })
                continue
            
            data = message.value
            
            logger.info("Message received", extra={
                'extra_data': {
                    'event_type': 'kafka_message_received',
                    'message_count': message_count,
                    'id_value': data.get('id_value', 'N/A'),
                    'contract': data.get('contract', 'MISSING'),
                    'offset': message.offset
                }
            })
            
            is_valid, errors = validator.validate_for_kafka(data)
            
            if not is_valid:
                logger.warning("Validation failed", extra={
                    'extra_data': {
                        'event_type': 'validation_failed',
                        'message_count': message_count,
                        'errors': errors,
                        'contract': data.get('contract')
                    }
                })
                
                dlq_result = validator.send_to_dead_letter_queue(
                    data,
                    errors,
                    'moex-market-data',
                    'moex'
                )
                
                if dlq_result:
                    logger.info("Sent to DLQ", extra={
                        'extra_data': {
                            'event_type': 'dlq_message_sent',
                            'message_count': message_count,
                            'error_reason': f"Validation errors: {', '.join(errors)}"
                        }
                    })
                else:
                    logger.error("Failed to send to DLQ", extra={
                        'extra_data': {
                            'event_type': 'dlq_send_failed',
                            'message_count': message_count
                        }
                    })
                
                invalid_count += 1
                logger.info("Message statistics", extra={
                    'extra_data': {
                        'event_type': 'message_stats',
                        'total': message_count,
                        'valid': valid_count,
                        'invalid': invalid_count
                    }
                })
                continue
            
            logger.info("Validation passed", extra={
                'extra_data': {
                    'event_type': 'validation_passed',
                    'message_count': message_count,
                    'contract': data.get('contract')
                }
            })
            
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
                logger.info("Data saved to CSV", extra={
                    'extra_data': {
                        'event_type': 'csv_save_success',
                        'message_count': message_count,
                        'contract': data.get('contract'),
                        'filepath': csv_file
                    }
                })
            except Exception as e:
                logger.error("Failed to save to CSV", extra={
                    'extra_data': {
                        'event_type': 'csv_save_error',
                        'message_count': message_count,
                        'error': str(e),
                        'contract': data.get('contract')
                    }
                })
            
            valid_count += 1
            logger.info("Message statistics", extra={
                'extra_data': {
                    'event_type': 'message_stats',
                    'total': message_count,
                    'valid': valid_count,
                    'invalid': invalid_count
                }
            })
            
    except KeyboardInterrupt:
        logger.info("Consumer stopped by user", extra={
            'extra_data': {
                'event_type': 'consumer_stopped_by_user',
                'total_messages_processed': message_count
            }
        })
    except Exception as e:
        logger.error("Fatal error", extra={
            'extra_data': {
                'event_type': 'consumer_fatal_error',
                'error': str(e),
                'total_messages_processed': message_count
            }
        })
    finally:
        logger.info("Final statistics", extra={
            'extra_data': {
                'event_type': 'final_stats',
                'total': message_count,
                'valid': valid_count,
                'invalid': invalid_count
            }
        })
        try:
            consumer.close()
            logger.info("Connections closed", extra={
                'extra_data': {
                    'event_type': 'connections_closed'
                }
            })
        except:
            pass

if __name__ == "__main__":
    run_moex_consumer()