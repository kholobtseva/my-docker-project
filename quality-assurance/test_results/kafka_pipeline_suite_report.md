# Test Suite Report: Kafka Data Pipeline

## 📊 Executive Summary
- **Test Suite**: Kafka Data Pipeline  
- **Execution Date**: 
- **Total Test Cases**: 
- **Passed**: 
- **Failed**:  
- **Blocked**: 
- **Bugs Found**: 

---

## 🧪 Test Case Results

### TC-KAFKA-001: Basic Kafka Connectivity

| Step | Action | Expected Result | Actual Result | Status | Evidence |
|------|--------|-----------------|---------------|--------|----------|
| 1 | `docker-compose ps` | Все контейнеры "Up" | ✅ Все контейнеры запущены | PASS | ![Контейнеры](../screenshots/kafka_pipeline/TC-KAFKA-001_step1_docker_containers_status.JPG) |
| 2 | `docker-compose exec kafka...` | Топик market-data существует | ✅ Топик найден | PASS | ![Топики](../screenshots/kafka_pipeline/TC-KAFKA-001_step2_kafka_topics_list.jpg) |
| 3 | Открыть Kafdrop | Интерфейс доступен | ✅ Kafdrop открыт | PASS | ![Kafdrop](../screenshots/kafka_pipeline/TC-KAFKA-001_step3_kafdrop_interface.jpg) |

---
### TC-KAFKA-002: Manual Message Producing via AKHQ

| Step | Action | Expected Result | Actual Result | Status | Evidence |
|------|--------|-----------------|---------------|--------|----------|
| 1 | Открыть AKHQ | Интерфейс AKHQ открывается | ✅ AKHQ доступен | PASS | ![AKHQ](../screenshots/kafka_pipeline/TC-KAFKA-002_step1_akhq_main.jpg) |
| 2 | Перейти в топик market-data | Отображается страница топика | ✅ Топик найден | PASS | ![Топик](../screenshots/kafka_pipeline/TC-KAFKA-002_step2_topic_details.jpg) |
| 3 | Нажать "Produce message" | Открывается форма отправки | ✅ Форма открыта | PASS | ![Форма](../screenshots/kafka_pipeline/TC-KAFKA-002_step3_produce_form.jpg) |
| 4 | Ввести и отправить сообщение | Сообщение успешно отправлено | ✅ Сообщение отправлено | PASS | ![Отправка](../screenshots/kafka_pipeline/TC-KAFKA-002_step4_message_sent.jpg) |

---
### TC-KAFKA-003: Consumer Data Processing and CSV Export

| Step | Action | Expected Result | Actual Result | Status | Evidence |
|------|--------|-----------------|---------------|--------|----------|
| 1 | Отправить тестовое сообщение через AKHQ | Сообщение появляется в топике market-data | ✅ Сообщение успешно отправлено | PASS | ![AKHQ](../screenshots/kafka_pipeline/TC-KAFKA-003_step1_message_in_topic.jpg) |
| 2 | Проверить логи consumer | В логах присутствует запись о получении сообщения | ✅ Consumer получил сообщение | PASS | [Логи](../test_results/TC-KAFKA-003_step2_consumer_logs.txt) |
| 3 | Проверить создание CSV файла | CSV файл существует в папке /app/logs/ | ✅ Файл создан | PASS | [Проверка](../test_results/TC-KAFKA-003_step3_csv_file_check.txt) |
| 4 | Проверить содержимое CSV файла | Файл содержит данные отправленного сообщения | ✅ Данные присутствуют | PASS | ![CSV](../screenshots/kafka_pipeline/TC-KAFKA-003_step4_csv_content.jpg) |
| 5 | Проверить нормализацию данных | Все поля корректно нормализованы | ✅ Проблема с кириллицей в name_rus | WARNING | [Нормализация](../test_results/TC-KAFKA-003_step5_data_normalization.txt) |

---
### TC-KAFKA-004: Kafka Service Recovery After Restart

| Step | Action | Expected Result | Actual Result | Status | Evidence |
|------|--------|-----------------|---------------|--------|----------|
| 1 | Остановить Kafka брокер | Kafka контейнер останавливается | ✅ Kafka успешно остановлен | PASS | [Статус](../test_results/TC-KAFKA-004_step1_all_containers_status.txt) |
| 2 | Запустить python-script при недоступном Kafka | Скрипт запускается, но не может подключиться к Kafka | ✅ Скрипт запущен, ошибки подключения | PASS | [Логи](../test_results/TC-KAFKA-004_step2_python_script_logs.txt) |
| 3-4 | Проверить логи на ошибки подключения | Найдены ошибки: DNS failed, NoBrokersAvailable | ✅ Все ошибки найдены в логах | PASS | [Анализ логов](../test_results/TC-KAFKA-004_step2_python_script_logs.txt) |
| 5 | Запустить Kafka обратно | Kafka контейнер запускается | ✅ Kafka запущен и healthy | PASS | [Статус](../test_results/TC-KAFKA-004_step5_kafka_started.txt) |
| 6 | Подождать 30 секунд | Соединение восстанавливается | ✅ Соединение восстановлено | PASS | - |
| 7 | Отправить тестовое сообщение через AKHQ | Сообщение успешно отправляется в топик | ✅ Сообщение отправлено | PASS | ![AKHQ](../screenshots/kafka_pipeline/TC-KAFKA-004_step7_message_sent.jpg) |
| 8 | Проверить обработку consumer | Consumer обрабатывает новое сообщение | ✅ Сообщение #628 получено и сохранено | PASS | [Логи](../test_results/TC-KAFKA-004_step8_consumer_processing.txt) |

---
# ШАБЛОНЫ
✅ PASS - все ок  
❌ FAIL - тест не прошел  
⏹️ BLOCKED - заблокирован багом/зависимостью  
🟡 WARNING - есть проблемы, но не критичные  

### ✅ TC-KAFKA-001: Basic Kafka Connectivity

| Step | Action | Expected Result | Actual Result | Status | Evidence |
|------|--------|-----------------|---------------|--------|----------|
| 1 | `docker-compose ps` | Все контейнеры "Up" | ✅ Все контейнеры запущены | PASS | ![Контейнеры](../screenshots/kafka/TC-KAFKA-001/step1-containers.png) |
| 2 | `docker-compose exec kafka...` | Топик market-data существует | ✅ Топик найден | PASS | ![Топики](../screenshots/kafka/TC-KAFKA-001/step2-topics.png) |
| 3 | Открыть Kafdrop | Интерфейс доступен | ✅ Kafdrop открыт | PASS | ![Kafdrop](../screenshots/kafka/TC-KAFKA-001/step3-kafdrop.png) |

**Overall Status**: ✅ PASS  
**Notes**: Все компоненты Kafka работают корректно

---

### ✅ TC-KAFKA-002: Manual Message Producing via AKHQ

| Step | Action | Expected Result | Actual Result | Status | Evidence |
|------|--------|-----------------|---------------|--------|----------|
| 1 | Открыть AKHQ | Интерфейс доступен | ✅ AKHQ открыт | PASS | ![AKHQ](../screenshots/kafka/TC-KAFKA-002/step1-akhq.png) |
| 2 | Перейти в топик market-data | Топик отображается | ✅ Топик доступен | PASS | ![Топик](../screenshots/kafka/TC-KAFKA-002/step2-topic.png) |
| 3 | Нажать "Produce message" | Форма отправки открывается | ✅ Форма открыта | PASS | ![Форма](../screenshots/kafka/TC-KAFKA-002/step3-form.png) |
| 4 | Ввести тестовое сообщение | Сообщение отправляется | ✅ Сообщение отправлено | PASS | ![Сообщение](../screenshots/kafka/TC-KAFKA-002/step4-message.png) |

**Overall Status**: ✅ PASS  
**Notes**: Ручная отправка сообщений через AKHQ работает корректно

---

### ❌ TC-KAFKA-003: Consumer Data Processing and CSV Export

| Step | Action | Expected Result | Actual Result | Status | Evidence |
|------|--------|-----------------|---------------|--------|----------|
| 1 | Отправить сообщение через AKHQ | Сообщение в топике | ✅ Сообщение доставлено | PASS | ![Сообщение](../screenshots/kafka/TC-KAFKA-003/step1-message.png) |
| 2 | Проверить логи consumer | Лог о получении сообщения | ✅ Сообщение получено | PASS | ![Логи](../screenshots/kafka/TC-KAFKA-003/step2-logs.png) |
| 3 | Проверить CSV файл | Файл создан/обновлен | ❌ Файл отсутствует | FAIL | ![Отсутствует CSV](../screenshots/kafka/TC-KAFKA-003/step3-missing-csv.png) |
| 4 | Проверить содержимое CSV | Данные присутствуют | ❌ Не применимо | BLOCKED | - |

**Overall Status**: ❌ FAIL  
**Bug**: [BUG-001 - CSV файл не создается](../bug_reports/bug_csv_headers.md)  
**Notes**: Consumer получает сообщения, но не создает CSV файл

---

## 🐛 Bugs Found
1. [BUG-001](../bug_reports/bug_csv_headers.md) - CSV файл не создается
2. [BUG-002](../bug_reports/bug_data_normalization.md) - Проблемы с валидацией данных

## 📈 Metrics
- **Test Coverage**: 
- **Execution Progress**: 
- **Critical Issues**: 
