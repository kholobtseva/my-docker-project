# My Docker Project

## Описание  
Python-скрипт для сбора данных с **Singapore Exchange** и сохранения в PostgreSQL

## Особенности
- Сбор данных по фьючерсам на железную руду с Singapore Exchange
- Автоматическое создание таблиц в PostgreSQL  
- Полный пайплайн данных: PostgreSQL → Elasticsearch → Kafka → CSV
- Docker-контейнеризация всех сервисов
- Мониторинг в Kibana и потоковая обработка в Kafka

## 📊 Elasticsearch & Kibana Integration

**Мониторинг данных в реальном времени через Kibana:**

- **Автоматическая синхронизация** данных из PostgreSQL в Elasticsearch
- **Визуализация** цен и объемов фьючерсов

## 🔄 Apache Kafka Integration

**Обработка данных**
- **Producer:** Отправка данных в топик `market-data`
- **Consumer:** Сохранение сообщений в CSV формате
- **Полный цикл:** Сбор → Обработка → Экспорт

## Как запустить

git clone https://github.com/kholobtseva/my-docker-project.git
cd my-docker-project
docker-compose up --build

# Запуск полного стека
docker-compose up --build -d

### Доступ к интерфейсам:
- Kibana (визуализация): http://localhost:5601
- Elasticsearch (данные): http://localhost:9200  
- PostgreSQL (БД): http://localhost:5432
- Kafka (брокер): http://localhost:9092

## Технологии

**Backend:**  
<img src="https://img.shields.io/badge/Python-3.9-blue?logo=python" alt="Python"> 
<img src="https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql" alt="PostgreSQL"> 
<img src="https://img.shields.io/badge/Docker-✓-blue?logo=docker" alt="Docker"> 
<img src="https://img.shields.io/badge/Docker_Compose-✓-blue?logo=docker" alt="Docker Compose">

## Monitoring & Analytics:
<img src="https://img.shields.io/badge/Elasticsearch-7.17.0-green?logo=elasticsearch" alt="Elasticsearch">
<img src="https://img.shields.io/badge/Kibana-7.17.0-green?logo=kibana" alt="Kibana">
<img src="https://img.shields.io/badge/Apache_Kafka-✓-green?logo=apachekafka" alt="Kafka">

## Message Broker:
<img src="https://img.shields.io/badge/Kafka_Producer-✓-orange" alt="Kafka Producer">
<img src="https://img.shields.io/badge/Kafka_Consumer-✓-orange" alt="Kafka Consumer">
<img src="https://img.shields.io/badge/Zookeeper-✓-orange" alt="Zookeeper">

**API:**  
<img src="https://img.shields.io/badge/Singapore_Exchange-✓-orange" alt="Singapore Exchange">

**Инструменты:**  
<img src="https://img.shields.io/badge/Git-✓-lightgrey?logo=git" alt="Git"> 
<img src="https://img.shields.io/badge/GitHub-✓-lightgrey?logo=github" alt="GitHub">

## 🐳 Docker Image

**Автоматически собирается и публикуется на Docker Hub:**  
[![Docker Hub](https://img.shields.io/badge/Docker_Hub-kholobtseva/my--python--script-2496ED?logo=docker)](https://hub.docker.com/r/kholobtseva/my-python-script)
[![Latest Version](https://img.shields.io/docker/v/kholobtseva/my-python-script/latest)](https://hub.docker.com/r/kholobtseva/my-python-script/tags)

### Использование готового образа:

docker pull kholobtseva/my-python-script:latest
docker run -d kholobtseva/my-python-script:latest

## 🚀 CI/CD Pipeline

![CI](https://github.com/kholobtseva/my-docker-project/actions/workflows/ci.yml/badge.svg)
![CD](https://github.com/kholobtseva/my-docker-project/actions/workflows/deploy.yml/badge.svg)

Проект использует **полный цикл CI/CD** на GitHub Actions:

### ✅ Continuous Integration (CI)
- **14+ Unit-тестов** на pytest
- **Проверка зависимостей** и структуры проекта  
- **Валидация Dockerfile** и конфигураций

### 🚀 Continuous Delivery (CD) 
- **Автоматическая сборка** Docker образа при каждом коммите
- **Публикация в Docker Hub** с тегами latest и 1.0
- **Версионирование** образов для возможности отката

### 🔄 Data Pipeline
**Полный цикл обработки данных:**
- ✅ **Data Collection:** Сбор данных с Singapore Exchange API
- ✅ **Database:** Сохранение в PostgreSQL с автоматическим созданием схемы
- ✅ **Search & Analytics:** Синхронизация в Elasticsearch для полнотекстового поиска
- ✅ **Real-time Processing:** Отправка в Apache Kafka для потоковой обработки
- ✅ **Data Export:** Консюмер сохраняет данные в CSV для анализа
- ✅ **Monitoring:** Визуализация в Kibana
  
### 📊 Мониторинг
- **Автоматические email-уведомления** о результатах CI/CD
- **Визуальный статус** через бейджи в README  
- **Детальные логи** в GitHub Actions
- **Полная история** всех запусков

## 🧪 Запуск тестов локально

### Установить зависимости
pip install -r requirements.txt

### Запустить все тесты (14+ тестов)
pytest tests/ -v

### Запустить конкретные тесты
pytest tests/test_ci.py -v
pytest tests/test_simple.py -v








