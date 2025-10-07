# app/core/kafka_utils.py
import json
import time
from datetime import datetime
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import NoBrokersAvailable
from decimal import Decimal

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (Decimal,)):
            return float(obj)
        elif isinstance(obj, (datetime,)):
            return obj.isoformat()
        return super().default(obj)

class KafkaManager:
    def __init__(self, bootstrap_servers=['kafka:9092']):
        self.bootstrap_servers = bootstrap_servers
        self.producer = None
        self._initialize_producer()
    
    def _initialize_producer(self):
        """Инициализация Kafka Producer"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(
                    v, ensure_ascii=False, cls=CustomJSONEncoder
                ).encode('utf-8')
            )
            return True
        except Exception as e:
            print(f"WARNING: Failed to initialize Kafka producer: {e}")
            return False
    
    def send_message(self, topic, data):  # ← ДОЛЖЕН БЫТЬ ВНУТРИ КЛАССА!
        """Отправка сообщения в Kafka"""
        if not self.producer:
            return False
        
        try:
            future = self.producer.send(topic, value=data)
            future.get(timeout=10)
            return True
        except Exception as e:
            print(f"WARNING: Kafka send error: {e}")
            return False
    
    def flush(self):  # ← ДОЛЖЕН БЫТЬ ВНУТРИ КЛАССА!
        """Принудительная отправка сообщений из буфера"""
        if self.producer:
            try:
                self.producer.flush(timeout=30)
                return True
            except Exception as e:
                print(f"WARNING: Kafka flush error: {e}")
                return False

def create_kafka_consumer(topic, group_id, auto_offset_reset='earliest'):
    """Создание Kafka Consumer с retry логикой"""
    max_retries = 5
    retry_delay = 10
    
    for attempt in range(max_retries):
        try:
            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=['kafka:9092'],
                auto_offset_reset=auto_offset_reset,
                value_deserializer=lambda m: m,  # Raw bytes
                group_id=group_id,
                enable_auto_commit=True,
                session_timeout_ms=30000,
                heartbeat_interval_ms=10000
            )
            return consumer
        except NoBrokersAvailable:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                raise
    return None