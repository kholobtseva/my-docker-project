import pytest
import os

def test_required_files_exist():
    """Тест что все необходимые файлы существуют"""
    required_files = [
        'Dockerfile',
        'docker-compose.yml', 
        'requirements.txt',
        'app/main.py'
    ]
    
    for file in required_files:
        assert os.path.exists(file), f"Файл {file} не найден"

def test_dockerfile_content():
    """Тест содержимого Dockerfile"""
    with open('Dockerfile', 'r') as f:
        content = f.read()
        assert 'FROM python' in content
        assert 'requirements.txt' in content
        assert 'app/main.py' in content