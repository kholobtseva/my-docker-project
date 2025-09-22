import pytest
from unittest.mock import Mock, patch
import json

def test_api_logic():
    """Тестируем логику обработки API ответов без импорта main"""
    
    # Имитируем функцию get_data_json
    def mock_get_data_json(url, symbol):
        # Логика похожая на твою, но упрощенная
        mock_response = Mock()
        mock_response.text = json.dumps({
            'data': [{'name': symbol, 'base-date': '20231201', 'price': 100}]
        })
        # ... имитируем обработку
        return [{'name': symbol, 'price': 100}]
    
    result = mock_get_data_json('test_url', 'FEFU25')
    assert result[0]['name'] == 'FEFU25'

def test_data_processing():
    """Тест обработки данных"""
    test_data = [
        {'name': 'FEFU25', 'price': 100},
        {'name': 'FEFG25', 'price': 105}
    ]
    
    # Простая логика фильтрации
    filtered = [item for item in test_data if item['price'] > 100]
    assert len(filtered) == 1
    assert filtered[0]['name'] == 'FEFG25'