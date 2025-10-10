import allure
import pytest
import psycopg2
import os

@allure.epic("Database Tests")
@allure.feature("PostgreSQL")
class TestPostgreSQLSimple:
    
    def get_db_connection(self):
        """Простая функция вместо фикстуры"""
        return psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'my_db'),  
            user=os.getenv('DB_USER', 'user'),       
            password=os.getenv('DB_PASSWORD', 'password')
        )
    
    @allure.story("Database Connectivity")
    def test_simple_connection(self):
        """Простой тест подключения"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        assert "PostgreSQL" in version
        
        cursor.close()
        conn.close()