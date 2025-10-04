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

Status: ✅ Manual ✅ PASSED
---
### TC-KAFKA-002: Manual Message Producing via AKHQ

| Step | Action | Expected Result | Actual Result | Status | Evidence |
|------|--------|-----------------|---------------|--------|----------|
| 1 | Открыть AKHQ | Интерфейс AKHQ открывается | ✅ AKHQ доступен | PASS | ![AKHQ](../screenshots/kafka_pipeline/TC-KAFKA-002_step1_akhq_main.jpg) |
| 2 | Перейти в топик market-data | Отображается страница топика | ✅ Топик найден | PASS | ![Топик](../screenshots/kafka_pipeline/TC-KAFKA-002_step2_topic_details.jpg) |
| 3 | Нажать "Produce message" | Открывается форма отправки | ✅ Форма открыта | PASS | ![Форма](../screenshots/kafka_pipeline/TC-KAFKA-002_step3_produce_form.jpg) |
| 4 | Ввести и отправить сообщение | Сообщение успешно отправлено | ✅ Сообщение отправлено | PASS | ![Отправка](../screenshots/kafka_pipeline/TC-KAFKA-002_step4_message_sent.jpg) |

Status: ✅ Manual ✅ PASSED
---
### TC-KAFKA-003: Consumer Data Processing and CSV Export

| Step | Action | Expected Result | Actual Result | Status | Evidence |
|------|--------|-----------------|---------------|--------|----------|
| 1 | Отправить тестовое сообщение через AKHQ | Сообщение появляется в топике market-data | ✅ Сообщение успешно отправлено | PASS | ![AKHQ](../screenshots/kafka_pipeline/TC-KAFKA-003_step1_message_in_topic.jpg) |
| 2 | Проверить логи consumer | В логах присутствует запись о получении сообщения | ✅ Consumer получил сообщение | PASS | [Логи](../test_results/TC-KAFKA-003_step2_consumer_logs.txt) |
| 3 | Проверить создание CSV файла | CSV файл существует в папке /app/logs/ | ✅ Файл создан | PASS | [Проверка](../test_results/TC-KAFKA-003_step3_csv_file_check.txt) |
| 4 | Проверить содержимое CSV файла | Файл содержит данные отправленного сообщения | ✅ Данные присутствуют | PASS | ![CSV](../screenshots/kafka_pipeline/TC-KAFKA-003_step4_csv_content.jpg) |
| 5 | Проверить нормализацию данных | Все поля корректно нормализованы | ✅ Проблема с кириллицей в name_rus | WARNING | [Нормализация](../test_results/TC-KAFKA-003_step5_data_normalization.txt) |

Status: ✅ Manual ✅ PASSED
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

Status: ✅ Manual ✅ PASSED
---
### TC-KAFKA-005: Valid Message Processing

| Step | Action | Expected Result | Actual Result | Status | Evidence |
|------|--------|-----------------|---------------|--------|----------|
| 1 | Send valid message via AKHQ | Message successfully sent to market-data topic | Message successfully sent to topic | ✅ PASS | ![Step1](../screenshots/kafka_pipeline/TC-KAFKA-005_step1_message_sent.jpg) |
| 2 | Check consumer logs | Consumer log shows message processing record | Message #630 processed: FEFZ25 - 2025-10-04 | ✅ PASS | [Logs](../test_results/TC-KAFKA-005_step2_consumer_logs.txt) |
| 3 | Check CSV file data | CSV file contains sent message data | Data saved to CSV: /app/logs/kafka_messages.csv | ✅ PASS | [CSV Content](../test_results/TC-KAFKA-005_step3_csv_content.txt) ![CSV Visual](../screenshots/kafka_pipeline/TC-KAFKA-005_step3_csv_content.jpg) |

Status: ✅ Manual ✅ PASSED
---

### TC-KAFKA-006: Invalid Date Format Handling

| Step | Action | Expected Result | Actual Result | Status | Evidence |
|------|--------|-----------------|---------------|--------|----------|
| 1 | Send message with invalid date via AKHQ | Message successfully sent to market-data topic | Message successfully sent to topic | ✅ PASS | ![Step1](../screenshots/kafka_pipeline/TC-KAFKA-006_step1_message_sent.jpg) |
| 2 | Check consumer logs for validation warnings | Consumer logs show warnings about invalid date format | No validation warnings - invalid date accepted without errors | ❌ FAIL | [Logs](../test_results/TC-KAFKA-006_step2_consumer_logs.txt) |

Status: ✅ Manual ❌ FAILED - Missing date validation (Bug BUG-KAFKA-006)  
Bug Reference: BUG-KAFKA-006_missing_date_validation.md

---

### TC-KAFKA-007: Required Field Validation

| Step | Action | Expected Result | Actual Result | Status | Evidence |
|------|--------|-----------------|---------------|--------|----------|
| 1 | Send message without required "price" field via AKHQ | Message successfully sent to market-data topic | Message successfully sent to topic | ✅ PASS | ![Step1](../screenshots/kafka_pipeline/TC-KAFKA-007_step1_message_sent.jpg) |
| 2 | Check consumer logs for validation errors | Consumer logs show validation errors for required fields | WARNING: Missing required field: price. Message skipped | ✅ PASS | [Logs](../test_results/TC-KAFKA-007_step2_consumer_logs.txt) |

Status: ✅ Manual ✅ PASSED
---

**Результаты TC-KAFKA-008:**

| Step | Action | Expected Result | Actual Result | Status | Evidence |
|------|--------|-----------------|---------------|--------|----------|
| 1 | Send message with invalid JSON via AKHQ | Message successfully sent to market-data topic | Message successfully sent | ✅ PASS | ![Step1](../screenshots/kafka_pipeline/TC-KAFKA-008_step1_message_sent.jpg) |
| 2 | Check consumer logs for parsing errors | Consumer logs show JSON parsing errors | Consumer crashed with JSONDecodeError | ❌ FAIL | [Logs](../test_results/TC-KAFKA-008_step2_consumer_logs.txt) |

Status: ✅ Manual ❌ FAILED - Critical bug found (BUG-KAFKA-008)

---
# ШАБЛОНЫ
✅ PASS - все ок  
❌ FAIL - тест не прошел  
⏹️ BLOCKED - заблокирован багом/зависимостью  
🟡 WARNING - есть проблемы, но не критичные  

---

## 🐛 Bugs Found


## 📈 Metrics
- **Test Coverage**: 
- **Execution Progress**: 
- **Critical Issues**: 
