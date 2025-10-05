import pytest
import os
import sys
import allure

@allure.epic("CI/CD Pipeline")
@allure.feature("Basic Project Validation")
class TestCIPipeline:

    @allure.story("Python Environment")
    @allure.title("TC-CI-001: Python Version Check")
    @allure.description("Проверка соответствия версии Python требованиям проекта")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_python_version(self):
        allure.dynamic.tag("environment")
        allure.dynamic.tag("python")
        
        with allure.step("Получить информацию о версии Python"):
            version_info = f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            allure.attach(version_info, "Версия Python", allure.attachment_type.TEXT)
            
        with allure.step("Проверить мажорную версию Python"):
            assert sys.version_info.major == 3, "Требуется Python 3.x"
            allure.attach("✓ Мажорная версия: 3", "Проверка версии", allure.attachment_type.TEXT)
            
        with allure.step("Проверить минимальную минорную версию"):
            assert sys.version_info.minor >= 9, "Требуется Python 3.9 или выше"
            allure.attach(f"✓ Минорная версия: {sys.version_info.minor} (>= 9)", "Проверка версии", allure.attachment_type.TEXT)

    @allure.story("Project Structure") 
    @allure.title("TC-CI-002: Required Files Validation")
    @allure.description("Проверка наличия всех необходимых файлов проекта")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_required_files(self):
        allure.dynamic.tag("structure")
        allure.dynamic.tag("files")
        
        required_files = [
            'Dockerfile',
            'docker-compose.yml', 
            'requirements.txt',
            'app/main.py',
            'init.sql'
        ]
        
        with allure.step("Определить список обязательных файлов"):
            files_list = "\n".join([f"• {file}" for file in required_files])
            allure.attach(files_list, "Обязательные файлы проекта", allure.attachment_type.TEXT)
            
        missing_files = []
        
        with allure.step("Проверить существование каждого файла"):
            for file in required_files:
                if os.path.exists(file):
                    allure.attach(f"✓ {file} - найден", "Статус файла", allure.attachment_type.TEXT)
                else:
                    missing_files.append(file)
                    allure.attach(f"✗ {file} - ОТСУТСТВУЕТ", "Статус файла", allure.attachment_type.TEXT)
                    
        with allure.step("Проверить отсутствие пропущенных файлов"):
            assert len(missing_files) == 0, f"Отсутствующие файлы: {', '.join(missing_files)}"
            allure.attach("✓ Все обязательные файлы присутствуют", "Итог проверки", allure.attachment_type.TEXT)

    @allure.story("Dependencies")
    @allure.title("TC-CI-003: Requirements Dependencies Check")
    @allure.description("Проверка доступности зависимостей из requirements.txt")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_requirements_dependencies(self):
        allure.dynamic.tag("dependencies")
        allure.dynamic.tag("imports")
        
        dependencies = ['requests', 'psycopg2', 'pytest']
        imported_modules = []
        failed_imports = []
        
        with allure.step("Попытка импорта каждой зависимости"):
            for dep in dependencies:
                try:
                    __import__(dep)
                    imported_modules.append(dep)
                    allure.attach(f"✓ {dep} - успешно импортирован", "Импорт модуля", allure.attachment_type.TEXT)
                except ImportError as e:
                    failed_imports.append(f"{dep}: {e}")
                    allure.attach(f"✗ {dep} - ошибка импорта: {e}", "Импорт модуля", allure.attachment_type.TEXT)
                    
        with allure.step("Проверить результаты импорта"):
            assert len(failed_imports) == 0, f"Ошибки импорта: {', '.join(failed_imports)}"
            allure.attach(f"✓ Все {len(imported_modules)} зависимостей доступны", "Итог проверки", allure.attachment_type.TEXT)

    @allure.story("Docker Configuration")
    @allure.title("TC-CI-004: Dockerfile Content Validation")
    @allure.description("Проверка содержимого Dockerfile на соответствие требованиям")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_dockerfile_content(self):
        allure.dynamic.tag("docker")
        allure.dynamic.tag("configuration")
        
        with allure.step("Прочитать содержимое Dockerfile"):
            with open('Dockerfile', 'r', encoding='utf-8') as f:
                content = f.read()
            allure.attach(content, "Содержимое Dockerfile", allure.attachment_type.TEXT)
            
        with allure.step("Проверить базовый образ Python"):
            assert 'FROM python' in content, "Dockerfile должен использовать базовый образ Python"
            allure.attach("✓ Базовый образ Python найден", "Проверка Dockerfile", allure.attachment_type.TEXT)
            
        with allure.step("Проверить копирование requirements.txt"):
            assert 'requirements.txt' in content, "Dockerfile должен копировать requirements.txt"
            allure.attach("✓ requirements.txt упомянут", "Проверка Dockerfile", allure.attachment_type.TEXT)
            
        with allure.step("Проверить копирование основного скрипта"):
            assert 'app/main.py' in content, "Dockerfile должен копировать app/main.py"
            allure.attach("✓ app/main.py упомянут", "Проверка Dockerfile", allure.attachment_type.TEXT)

    @allure.story("Docker Configuration")
    @allure.title("TC-CI-005: Docker Compose Content Validation")
    @allure.description("Проверка содержимого docker-compose.yml на наличие ключевых сервисов")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_docker_compose_content(self):
        allure.dynamic.tag("docker")
        allure.dynamic.tag("compose")
        
        with allure.step("Прочитать содержимое docker-compose.yml"):
            with open('docker-compose.yml', 'r', encoding='utf-8') as f:
                content = f.read()
            allure.attach(content, "Содержимое docker-compose.yml", allure.attachment_type.TEXT)
            
        with allure.step("Проверить наличие сервиса PostgreSQL"):
            assert 'postgres' in content, "docker-compose.yml должен содержать сервис postgres"
            allure.attach("✓ Сервис postgres найден", "Проверка docker-compose", allure.attachment_type.TEXT)
            
        with allure.step("Проверить наличие сервиса python-script"):
            assert 'python-script' in content, "docker-compose.yml должен содержать сервис python-script"
            allure.attach("✓ Сервис python-script найден", "Проверка docker-compose", allure.attachment_type.TEXT)

    @allure.story("Basic Functionality")
    @allure.title("TC-CI-006: Simple Arithmetic Validation")
    @allure.description("Базовая проверка математических операций")
    @allure.severity(allure.severity_level.NORMAL)
    def test_simple_arithmetic(self):
        allure.dynamic.tag("basic")
        allure.dynamic.tag("arithmetic")
        
        with allure.step("Проверить простое сложение"):
            result = 2 + 2
            assert result == 4, f"2 + 2 должно быть 4, но получилось {result}"
            allure.attach(f"2 + 2 = {result} ✓", "Проверка сложения", allure.attachment_type.TEXT)
            
        with allure.step("Проверить умножение"):
            result = 10 * 10
            assert result == 100, f"10 * 10 должно быть 100, но получилось {result}"
            allure.attach(f"10 * 10 = {result} ✓", "Проверка умножения", allure.attachment_type.TEXT)

    @allure.story("Environment")
    @allure.title("TC-CI-007: Environment Variables Check")
    @allure.description("Проверка доступности модуля os и переменных окружения")
    @allure.severity(allure.severity_level.NORMAL)
    def test_environment_variables(self):
        allure.dynamic.tag("environment")
        allure.dynamic.tag("os")
        
        with allure.step("Импортировать модуль os"):
            import os
            allure.attach("✓ Модуль os успешно импортирован", "Импорт модуля", allure.attachment_type.TEXT)
            
        with allure.step("Проверить наличие атрибута environ"):
            assert hasattr(os, 'environ'), "Модуль os должен иметь атрибут environ"
            allure.attach("✓ Атрибут environ присутствует", "Проверка атрибутов", allure.attachment_type.TEXT)
            
        with allure.step("Показать доступные переменные окружения"):
            env_vars = "\n".join([f"{key}: {value}" for key, value in os.environ.items() if not key.startswith('_')][:10])
            allure.attach(env_vars, "Первые 10 переменных окружения", allure.attachment_type.TEXT)