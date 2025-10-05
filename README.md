# My Microservices Data Pipeline - Educational Project

## Описание  
Практическая реализация микросервисной архитектуры для демонстрации работы с современным стеком технологий. Проект использует сбор данных с Singapore Exchange как use-case для отработки полного цикла обработки данных в распределенной системе.

**Почему микросервисы для простой задачи?**  
Осознанный выбор архитектуры для обучения: каждая технология в проекте представляет отдельный сервис с четкими границами ответственности, что соответствует принципам микросервисного подхода.

**Ключевые компетенции:**
- Понимание пайплайнов данных в реальном времени
- Опыт интеграции разнородных систем  
- Навыки контейнеризации и оркестрации
- Практика работы с message brokers (Kafka)
- Автоматизация тестирования: pytest, интеграция с CI/CD
- Ручное тестирование: Kafka, сквозная проверка пайплайна данных
- Тестирование производительности: мониторинг Docker контейнеров
- Отслеживание багов: выявление и документирование реальных дефектов

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

## 🖥️ Kafka Monitoring with Kafdrop

**Визуальный мониторинг Kafka топиков**

- **Просмотр сообщений:** Чтение данных из топика `market-data` в формате JSON
- **Мониторинг топиков:** Информация о партициях, офсетах и репликации
- **Consumer groups:** Отслеживание работы консьюмеров

### Доступ к Kafdrop:
- **URL:** http://localhost:9000
- **Топик для просмотра:** `market-data`

### Пример данных в Kafdrop:
```json
{
  "id_value": 200.0,
  "date": "2025-09-19", 
  "price": 106.25,
  "contract": "FEFZ25",
  "name_rus": "Железная руда 62% Fe",
  "source": "moex_sgx"
}
```

## Как запустить

- git clone https://github.com/kholobtseva/my-docker-project.git
- cd my-docker-project
- docker-compose up --build

# Запуск полного стека
docker-compose up --build -d

### Доступ к интерфейсам:
- Kibana (визуализация): http://localhost:5601
- Elasticsearch (данные): http://localhost:9200  
- PostgreSQL (БД): http://localhost:5432
- Kafka (брокер): http://localhost:9092
- Kafdrop (мониторинг): http://localhost:9000
- AKHQ (управление и тестирование): http://localhost:8080

## Технологии

**Backend:**  
<img src="https://img.shields.io/badge/Python-3.9-blue?logo=python" alt="Python"> 
<img src="https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql" alt="PostgreSQL"> 
<img src="https://img.shields.io/badge/Docker-✓-blue?logo=docker" alt="Docker"> 
<img src="https://img.shields.io/badge/Docker_Compose-✓-blue?logo=docker" alt="Docker Compose">

**UI Tools:**  
<img src="https://img.shields.io/badge/Kafdrop-✓-lightblue?logo=apachekafka" alt="Kafdrop"> *(мониторинг)*
<img src="https://img.shields.io/badge/AKHQ-✓-lightblue?logo=apachekafka" alt="AKHQ"> *(управление + тестирование)*

## Monitoring & Analytics:
<img src="https://img.shields.io/badge/Elasticsearch-7.17.0-green?logo=elasticsearch" alt="Elasticsearch">
<img src="https://img.shields.io/badge/Kibana-7.17.0-green?logo=kibana" alt="Kibana">
<img src="https://img.shields.io/badge/Apache_Kafka-✓-green?logo=apachekafka" alt="Kafka">
<img src="https://img.shields.io/badge/Kafdrop-✓-green?logo=apachekafka" alt="Kafdrop">

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
![Allure Report](https://img.shields.io/badge/Allure-Reports-orange?logo=allure)

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

## 🔧 Troubleshooting

**Распространенные проблемы:**
- **Нет подключения к Kafka**: Проверьте что все контейнеры запущены: `docker-compose ps`
- **Нет сообщений в топике**: Убедитесь что producer отправляет данные, проверьте логи: `docker-compose logs python-script`
- **CSV файл не обновляется**: Проверьте логи consumer: `docker-compose logs kafka-consumer`

## 🧪 Testing

### Установить зависимости
pip install -r requirements.txt

### Запустить все тесты (14+ тестов)
pytest tests/ -v

### Запустить конкретные тесты
- pytest tests/test_ci.py -v
- pytest tests/test_simple.py -v

### Система отчетности ручного тестирования Kafka

#### Allure Reports - Документирование процесса
```bash
pytest tests/ --alluredir=allure-results
allure serve allure-results
```
- Тест-кейсы в Allure служат для удобного просмотра структуры тестирования в одном месте  
- Прикрепленные артефакты: скриншоты, логи, JSON сообщения с привязкой к шагам тест-кейсов  
- Фактически это документация процесса ручного тестирования, а не автоматические тесты  

---

**Markdown Report - Реальные результаты**

**📊 [Markdown Report с реальными результатами тестирования](quality-assurance/test_results/kafka_pipeline_suite_report.md)**

### Ручное тестирование Kafka
- **Kafdrop**: Мониторинг топиков и сообщений (http://localhost:9000)
- **AKHQ**: Полнофункциональный интерфейс Kafka с отправкой сообщений (http://localhost:8080)
- **Ручное тестирование**: Отправка тестовых сообщений для проверки пайплайна данных

### Test Kafka Message Example:
```json
{
  "id_value": 999,
  "date": "2024-01-15",
  "price": 150.75,
  "contract": "MANUAL_TEST",
  "name_rus": "Тест ручного QA",
  "source": "manual_test"
}

```
## 📊 Allure Test Reports

### 🚀 Онлайн отчет (GitHub Pages)
После каждого коммита актуальный тестовый отчет автоматически публикуется:  
**👉 https://kholobtseva.github.io/my-docker-project/**

### 💻 Локальный отчет
Для генерации и просмотра отчетов локально:

### Запустить тесты с Allure
```bash
pytest tests/ --alluredir=allure-results
```
### Просмотреть отчет в браузере
```bash
allure serve allure-results
```
### 📋 Что включено в отчет
- **25 автоматизированных тестов** (11 ручных Kafka + 14 unit-тестов)
- **Реальные доказательства тестирования:** логи, скриншоты, JSON сообщения
- **Пошаговое выполнение тестов**
- **Категоризация тестов** по Epic/Feature/Story
- **Уровни серьезности и теги**

### 🎯 Покрытие тестирования
- **Kafka Connectivity** - брокер, топики, мониторинг
- **Message Processing** - workflows продюсера/консьюмера
- **Data Validation** - формат данных, обязательные поля, обработка ошибок
- **Error Recovery** - сценарии перезапуска сервисов
- **Security** - санитизация данных и защита от инъекций

## 🚀 Quick Start for QA Engineers

### Тестирование Kafka пайплайна:
1. **Отправьте тестовое сообщение** через AKHQ (http://localhost:8080)
2. **Проверьте в Kafdrop** (http://localhost:9000)
3. **Проверьте CSV вывод** в `/app/logs/kafka_messages.csv`
4. **Мониторьте логи**: `docker-compose logs kafka-consumer`

Проект задуман как учебный стенд: сначала реализован базовый пайплайн (сбор → обработка → хранение → визуализация).  
Дальнейшее развитие — постепенное расширение QA-практиками
















