# My Docker Project

## Описание  
Python-скрипт для сбора данных с **MOEX ISS API** и сохранения в PostgreSQL

## Особенности
- Сбор данных по фьючерсам на сельхозтовары с Московской Биржи
- Автоматическое создание таблиц в PostgreSQL
- Docker-контейнеризация приложения

## Как запустить

git clone https://github.com/kholobtseva/my-docker-project.git
cd my-docker-project
docker-compose up --build

## Технологии

**Backend:**  
<img src="https://img.shields.io/badge/Python-3.9-blue?logo=python" alt="Python"> 
<img src="https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql" alt="PostgreSQL"> 
<img src="https://img.shields.io/badge/Docker-✓-blue?logo=docker" alt="Docker"> 
<img src="https://img.shields.io/badge/Docker_Compose-✓-blue?logo=docker" alt="Docker Compose">

**API:**  
<img src="https://img.shields.io/badge/MOEX_ISS_API-✓-orange" alt="MOEX ISS API">

**Инструменты:**  
<img src="https://img.shields.io/badge/Git-✓-lightgrey?logo=git" alt="Git"> 
<img src="https://img.shields.io/badge/GitHub-✓-lightgrey?logo=github" alt="GitHub">

## 🐳 Docker Image

**Доступно на Docker Hub:**  
[![Docker Hub](https://img.shields.io/badge/Docker_Hub-Repository-2496ED?logo=docker&logoColor=white)](https://hub.docker.com/r/kholobtseva/my-python-script:1.0)

## 🚀 CI/CD Pipeline

![CI](https://github.com/kholobtseva/my-docker-project/actions/workflows/ci.yml/badge.svg)

Проект использует **GitHub Actions** для автоматизации тестирования и сборки:

### ✅ Автоматические тесты
- **14+ Unit-тестов** на pytest
- **Проверка зависимостей** и структуры проекта  
- **Валидация Dockerfile** и конфигураций
- **Тестирование окружения** и логики приложения

### 🔄 Workflow
При каждом `git push` автоматически:
1. Запускается виртуальная машина Ubuntu
2. Устанавливаются зависимости Python
3. Выполняются **14+ тестов**
4. Проверяется корректность сборки
5. Генерируется отчет о результатах

### 📊 Мониторинг
- Статус сборки отображается в бейдже выше ✅
- Подробные логи доступны во вкладке **Actions**
- Уведомления о успешной/неуспешной сборке
- История всех запусков с детальной статистикой

## 🧪 Запуск тестов локально

### Установить зависимости
pip install -r requirements.txt

### Запустить все тесты (14+ тестов)
pytest tests/ -v

### Запустить конкретные тесты
pytest tests/test_ci.py -v
pytest tests/test_simple.py -v

