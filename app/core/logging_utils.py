# app/core/logging_utils.py
import logging
import json
from datetime import datetime
from elasticsearch import Elasticsearch

class ElasticsearchJSONFormatter(logging.Formatter):
    def __init__(self, logger_name):
        self.logger_name = logger_name
        super().__init__()
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': record.levelname,
            'logger': self.logger_name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName
        }
        
        if hasattr(record, 'extra_data'):
            log_entry.update(record.extra_data)
            
        return json.dumps(log_entry)

class ElasticsearchLogHandler(logging.Handler):
    def __init__(self, es_hosts, index_name):
        super().__init__()
        self.es_logs = Elasticsearch(es_hosts)
        self.index_name = index_name
    
    def emit(self, record):
        try:
            log_entry = json.loads(self.format(record))
            self.es_logs.index(index=self.index_name, body=log_entry)
        except Exception:
            # Fail silently to not break main functionality
            pass

def setup_logging(logger_name, es_hosts=['http://elasticsearch:9200']):
    """Настройка логирования с Elasticsearch"""
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    
    # JSON форматтер для Elasticsearch
    json_formatter = ElasticsearchJSONFormatter(logger_name)
    
    # Хендлер для Elasticsearch
    es_handler = ElasticsearchLogHandler(es_hosts, f'{logger_name}-logs')
    es_handler.setFormatter(json_formatter)
    logger.addHandler(es_handler)
    
    # Стандартный хендлер для консоли
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    logger.addHandler(console_handler)
    
    return logger