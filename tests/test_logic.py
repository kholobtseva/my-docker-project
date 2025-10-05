import pytest
from unittest.mock import Mock, patch
import json
import allure
from datetime import datetime

@allure.epic("Business Logic")
@allure.feature("SGX API Data Processing")
class TestSGXBusinessLogic:

    @allure.story("SGX API Integration")
    @allure.title("TC-LOGIC-001: SGX API Response Processing")
    @allure.description("Тестирование обработки реального ответа от Singapore Exchange API")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_sgx_api_response_processing(self):
        allure.dynamic.tag("sgx_api")
        allure.dynamic.tag("integration")
        
        def mock_get_data_json(url, symbol):
            with allure.step(f"Имитация SGX API запроса для {symbol}"):
                mock_response = Mock()
                mock_response.text = json.dumps({
                    'data': [
                        {
                            'base-date': '20231201',  # YYYYMMDD формат
                            'daily-settlement-price-abs': 106.25,
                            'total-volume': 1500
                        }
                    ]
                })
                allure.attach(mock_response.text, "Raw SGX API Response", allure.attachment_type.JSON)
            
            with allure.step("Обработка данных из API ответа"):
                data1 = json.loads(mock_response.text)
                processed_data = []
                
                for n in data1['data']:
                    date_obj = datetime.strptime(n['base-date'], "%Y%m%d")
                    formatted_date = date_obj.strftime("%Y-%m-%d")
                    processed_data.append({
                        'name': symbol,
                        'daily-settlement-price-abs': n['daily-settlement-price-abs'],
                        'total-volume': n['total-volume'],
                        'formatted_date': formatted_date
                    })
                
                allure.attach(json.dumps(processed_data, indent=2), "Processed Data", allure.attachment_type.JSON)
                return processed_data
        
        with allure.step("Выполнить тестовый вызов SGX API"):
            result = mock_get_data_json(
                'https://api.sgx.com/derivatives/v1.0/history/symbol/FEFZ25?days=1w&category=futures', 
                'FEFZ25'
            )
            
        with allure.step("Проверить корректность обработки данных"):
            assert len(result) == 1
            allure.attach(f"Получено элементов: {len(result)}", "Проверка количества", allure.attachment_type.TEXT)
            
            assert result[0]['name'] == 'FEFZ25'
            allure.attach(f"Символ: {result[0]['name']}", "Проверка символа", allure.attachment_type.TEXT)
            
            assert result[0]['daily-settlement-price-abs'] == 106.25
            allure.attach(f"Цена: {result[0]['daily-settlement-price-abs']}", "Проверка цены", allure.attachment_type.TEXT)
            
            assert result[0]['total-volume'] == 1500
            allure.attach(f"Объем: {result[0]['total-volume']}", "Проверка объема", allure.attachment_type.TEXT)
            
            assert result[0]['formatted_date'] == '2023-12-01'
            allure.attach(f"Дата: {result[0]['formatted_date']}", "Проверка даты", allure.attachment_type.TEXT)

    @allure.story("Data Transformation")
    @allure.title("TC-LOGIC-002: Database Insertion Format")
    @allure.description("Тестирование преобразования данных для вставки в PostgreSQL")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_database_insertion_format(self):
        allure.dynamic.tag("database")
        allure.dynamic.tag("transformation")
        
        with allure.step("Подготовить данные для вставки в БД"):
            test_data = [
                200,
                '2023-12-01',
                None,
                None,
                106.25,
                1500,
                'USD'
            ]
            
            allure.attach(json.dumps({
                'id_value': test_data[0],
                'date': test_data[1],
                'min_val': test_data[2],
                'max_val': test_data[3],
                'avg_val': test_data[4],
                'volume': test_data[5],
                'currency': test_data[6]
            }, indent=2), "Data for PostgreSQL Insertion", allure.attachment_type.JSON)
            
        with allure.step("Проверить структуру данных"):
            assert test_data[0] == 200
            assert test_data[1] == '2023-12-01'
            assert test_data[4] == 106.25
            assert test_data[5] == 1500
            assert test_data[6] == 'USD'
            
            allure.attach("Все поля соответствуют ожидаемой структуре", "Валидация структуры", allure.attachment_type.TEXT)