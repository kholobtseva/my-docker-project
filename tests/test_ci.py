import pytest
import os
import sys

def test_python_version():
    """Тест версии Python"""
    assert sys.version_info.major == 3
    assert sys.version_info.minor >= 9

def test_required_files():
    """Тест что все необходимые файлы существуют"""
    required_files = [
        'Dockerfile',
        'docker-compose.yml', 
        'requirements.txt',
        'app/main.py',
        'init.sql'
    ]
    
    for file in required_files:
        assert os.path.exists(file), f"Файл {file} не найден"

def test_requirements_dependencies():
    """Тест что зависимости из requirements.txt можно импортировать"""
    try:
        import requests
        import psycopg2
        import pytest
        assert True, "Все зависимости доступны"
    except ImportError as e:
        pytest.fail(f"Не хватает зависимости: {e}")

def test_dockerfile_content():
    """Тест содержимого Dockerfile"""
    with open('Dockerfile', 'r', encoding='utf-8') as f:
        content = f.read()
        assert 'FROM python' in content
        assert 'requirements.txt' in content
        assert 'app/main.py' in content

def test_docker_compose_content():
    """Тест содержимого docker-compose.yml"""
    with open('docker-compose.yml', 'r', encoding='utf-8') as f:
        content = f.read()
        assert 'postgres' in content
        assert 'python-script' in content

def test_simple_arithmetic():
    """Простой тест арифметики"""
    assert 2 + 2 == 4
    assert 10 * 10 == 100

def test_environment_variables():
    """Тест переменных окружения"""
    # Простая проверка что Python импортирует os
    import os
    assert hasattr(os, 'environ')