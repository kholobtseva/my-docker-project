import pytest
import allure
import sys

@allure.epic("Smoke Tests")
@allure.feature("Basic Environment Checks")
class TestSimpleSmoke:

    @allure.story("Basic Functionality")
    @allure.title("TC-SIMPLE-001: Basic Arithmetic Validation")
    @allure.description("Простая проверка базовой функциональности Python")
    @allure.severity(allure.severity_level.MINOR)
    def test_always_passes(self):
        allure.dynamic.tag("smoke")
        allure.dynamic.tag("basic")
        
        with allure.step("Проверить простое сложение"):
            result = 1 + 1
            assert result == 2
            allure.attach(f"1 + 1 = {result}", "Результат сложения", allure.attachment_type.TEXT)
            
        with allure.step("Проверить простые математические операции"):
            operations = [
                ("2 * 2", 2 * 2, 4),
                ("10 / 2", 10 / 2, 5),
                ("2 ** 3", 2 ** 3, 8)
            ]
            
            for op, actual, expected in operations:
                assert actual == expected, f"{op} должно быть {expected}, но получилось {actual}"
                allure.attach(f"{op} = {actual} ✓", "Проверка операции", allure.attachment_type.TEXT)

    @allure.story("Python Environment")
    @allure.title("TC-SIMPLE-002: Python Environment Check")
    @allure.description("Проверка версии Python и базового окружения")
    @allure.severity(allure.severity_level.NORMAL)
    def test_environment(self):
        allure.dynamic.tag("environment")
        allure.dynamic.tag("python")
        
        with allure.step("Получить информацию о версии Python"):
            version_info = f"Python {sys.version}"
            allure.attach(version_info, "Версия Python", allure.attachment_type.TEXT)
            
        with allure.step("Проверить что используется Python 3"):
            assert sys.version_info.major == 3
            allure.attach("Используется Python 3", "Проверка версии", allure.attachment_type.TEXT)
            
        with allure.step("Проверить доступные модули"):
            available_modules = [
                "os", "sys", "json", "datetime", "logging"
            ]
            
            for module in available_modules:
                try:
                    __import__(module)
                    allure.attach(f"{module} - доступен", "Проверка модуля", allure.attachment_type.TEXT)
                except ImportError:
                    allure.attach(f"{module} - НЕ доступен", "Проверка модуля", allure.attachment_type.TEXT)

    @allure.story("Dependencies")
    @allure.title("TC-SIMPLE-003: Core Dependencies Check")
    @allure.description("Проверка наличия основных зависимостей проекта")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_imports(self):
        allure.dynamic.tag("dependencies")
        allure.dynamic.tag("imports")
        
        core_dependencies = [
            "requests",      # Для API запросов к SGX
            "psycopg2",      # Для PostgreSQL
            "pytest",        # Для тестирования
            "elasticsearch", # Для Elasticsearch
            "kafka"          # Для Apache Kafka
        ]
        
        imported_modules = []
        missing_modules = []
        
        with allure.step("Проверить импорт каждой зависимости"):
            for dep in core_dependencies:
                try:
                    __import__(dep)
                    imported_modules.append(dep)
                    allure.attach(f"{dep} - успешно импортирован", "Импорт модуля", allure.attachment_type.TEXT)
                except ImportError as e:
                    missing_modules.append(dep)
                    allure.attach(f"{dep} - ошибка импорта: {e}", "Импорт модуля", allure.attachment_type.TEXT)
                    
        with allure.step("Проверить наличие всех критических зависимостей"):
            critical_deps = ["requests", "psycopg2", "pytest"]
            for critical_dep in critical_deps:
                assert critical_dep in imported_modules, f"Критическая зависимость {critical_dep} отсутствует"
                
        with allure.step("Сформировать итоговый отчет по зависимостям"):
            summary = f"""
            Успешно импортировано: {len(imported_modules)}/{len(core_dependencies)}
            Отсутствуют: {', '.join(missing_modules) if missing_modules else 'нет'}
            """
            allure.attach(summary.strip(), "Итог проверки зависимостей", allure.attachment_type.TEXT)