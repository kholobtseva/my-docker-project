import json
from datetime import datetime
from decimal import Decimal
from core.logging_utils import setup_logging

logger = setup_logging('validation_utils')

class UniversalDataValidator:
    """Универсальный валидатор для всех источников данных"""
    
    def __init__(self, kafka_manager, script_name):
        self.kafka_manager = kafka_manager
        self.script_name = script_name
        self.dead_letter_topic = 'dead-letter-queue'
    
    def validate_basic_structure(self, data, data_type='generic'):
        """Базовая валидация структуры данных"""
        errors = []
        
        if not data:
            errors.append("Empty data received")
            return False, errors
        
        if data_type == 'moex_api':
            if not isinstance(data, list) or len(data) < 7:
                errors.append("MOEX API data must be list with 7 elements")
            elif not data[0]:
                errors.append("Missing SECID in MOEX data")
            elif not data[1]:
                errors.append("Missing TRADEDATE in MOEX data")
            elif not data[6]:
                errors.append("Missing CURRENCYID in MOEX data")
        
        elif data_type == 'moex_futures_api': 
            # Валидация для MOEX Futures API - 6 элементов
            if not isinstance(data, list) or len(data) != 6:
                errors.append("MOEX Futures API data must be list with 6 elements")
            elif not data[0]:  # SECID
                errors.append("Missing SECID in MOEX Futures data")
            elif not data[1]:  # TRADEDATE
                errors.append("Missing TRADEDATE in MOEX Futures data")
        
        elif data_type == 'structured':
            if not isinstance(data, dict):
                errors.append("Structured data must be dict")
            else:
                required_fields = ['id_value', 'date_val', 'currency']
                for field in required_fields:
                    if field not in data:
                        errors.append(f"Missing required field: {field}")
                    elif data[field] is None:
                        errors.append(f"Required field {field} is null")
        
        return len(errors) == 0, errors
    
    def validate_date_field(self, date_str, field_name):
        """Валидация поля даты"""
        if not date_str:
            return False, f"{field_name} is empty"
        
        try:
            datetime.strptime(str(date_str), '%Y-%m-%d')
            return True, ""
        except ValueError:
            return False, f"{field_name} must be in format YYYY-MM-DD"
    
    def validate_numeric_field(self, value, field_name):
        """Валидация числового поля (может быть None)"""
        if value is None:
            return True, ""
        
        try:
            float(value)
            return True, ""
        except (TypeError, ValueError):
            return False, f"{field_name} must be numeric or null"
    
    def validate_for_kafka(self, data):
        """Валидация данных для отправки в Kafka"""
        errors = []
        
        # Преобразование id_value к int если возможно
        if 'id_value' in data and data['id_value'] is not None:
            try:
                data['id_value'] = int(data['id_value'])
            except (TypeError, ValueError):
                errors.append("id_value must be numeric and convertible to integer")
        
        # Обязательные поля
        required_fields = ['id_value', 'date', 'currency']
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field for Kafka: {field}")
            elif data[field] is None:
                errors.append(f"Required field for Kafka {field} is null")
        
        # Валидация даты
        if 'date' in data and data['date'] is not None:
            is_valid_date, date_error = self.validate_date_field(data['date'], 'date')
            if not is_valid_date:
                errors.append(date_error)
        
        # Числовые поля могут быть None
        numeric_fields = ['price', 'volume']
        for field in numeric_fields:
            if field in data:
                is_valid_numeric, numeric_error = self.validate_numeric_field(data[field], field)
                if not is_valid_numeric:
                    errors.append(numeric_error)
        
        return len(errors) == 0, errors
    
    def convert_moex_api_to_structured(self, raw_data, contract_id):
        """Конвертация данных MOEX API в структурированный формат"""
        try:
            return {
                'id_value': contract_id,
                'date_val': raw_data[1],
                'min_val': float(raw_data[2]) if raw_data[2] is not None else None,
                'max_val': float(raw_data[3]) if raw_data[3] is not None else None,
                'avg_val': float(raw_data[4]) if raw_data[4] is not None else None,
                'volume': float(raw_data[5]) if raw_data[5] is not None else None,
                'currency': raw_data[6]
            }
        except (TypeError, ValueError) as e:
            raise ValueError(f"Error converting MOEX data: {e}")
    
    def convert_moex_futures_to_structured(self, raw_data, contract_id, currency):
        """Конвертация данных MOEX Futures API в структурированный формат"""
        try:
            return {
                'id_value': contract_id,
                'date_val': raw_data[1],
                'min_val': float(raw_data[2]) if raw_data[2] is not None else None,
                'max_val': float(raw_data[3]) if raw_data[3] is not None else None,
                'avg_val': float(raw_data[4]) if raw_data[4] is not None else None,
                'volume': float(raw_data[5]) if raw_data[5] is not None else None,
                'currency': currency
            }
        except (TypeError, ValueError) as e:
            raise ValueError(f"Error converting MOEX Futures data: {e}")
    
    def prepare_for_kafka(self, db_row):
        """Подготовка данных из БД для отправки в Kafka"""
        return {
            'id_value': int(db_row[0]) if db_row[0] is not None else None,
            'date': db_row[1].isoformat() if db_row[1] else None,
            'price': float(db_row[2]) if db_row[2] else None,
            'volume': float(db_row[3]) if db_row[3] else None,
            'currency': db_row[4],
            'contract': db_row[5],
            'name_rus': db_row[6],
            'source': 'moex',
            'sync_timestamp': datetime.now().isoformat()
        }
    
    def send_to_dead_letter_queue(self, invalid_data, error_messages, original_topic="market-data", data_source="unknown"):
        """Отправка невалидных данных в мертвую очередь"""
        try:
            dead_letter_message = {
                'original_data': invalid_data,
                'error_messages': error_messages,
                'validation_timestamp': datetime.now().isoformat(),
                'original_topic': original_topic,
                'script_name': self.script_name,
                'data_source': data_source
            }
            
            success = self.kafka_manager.send_message(self.dead_letter_topic, dead_letter_message)
            
            if success:
                logger.warning(f"Data sent to dead letter queue: {error_messages}")
                
            return success
            
        except Exception as e:
            logger.error(f"Error sending to dead letter queue: {e}")
            return False