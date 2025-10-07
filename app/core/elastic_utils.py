# app/core/elastic_utils.py
from elasticsearch import Elasticsearch
from datetime import datetime

class ElasticsearchManager:
    def __init__(self, hosts=['http://elasticsearch:9200']):
        self.es = Elasticsearch(hosts)
    
    def send_data(self, data, index_name):
        """Отправка данных в Elasticsearch"""
        try:
            self.es.index(index=index_name, body=data)
            return True
        except Exception as e:
            print(f"ERROR: Failed to send data to Elasticsearch: {e}")
            return False
    
    def sync_from_postgres(self, db_conn, logger=None):
        """Синхронизация данных из PostgreSQL в Elasticsearch"""
        try:
            cursor = db_conn.cursor()
            cursor.execute("""
                SELECT am.id_value, am.date_val, am.avg_val, am.volume, am.currency,
                       wdi.name_eng, wdi.name_rus
                FROM agriculture_moex am
                JOIN www_data_idx wdi ON am.id_value = wdi.id
            """)
            
            synced_count = 0
            for row in cursor.fetchall():
                doc = {
                    'id_value': row[0],
                    'date': row[1].isoformat(),
                    'price': float(row[2]) if row[2] else None,
                    'volume': float(row[3]) if row[3] else None,
                    'currency': row[4],
                    'contract': row[5],
                    'name_rus': row[6],
                    'source': 'moex_sgx',
                    'sync_timestamp': datetime.now().isoformat()
                }
                
                if self.send_data(doc, 'agriculture-data'):
                    synced_count += 1
            
            if logger:
                logger.info(f"Synchronized {synced_count} records to Elasticsearch")
            
            return synced_count
            
        except Exception as e:
            if logger:
                logger.error(f"Elasticsearch sync error: {e}")
            return 0