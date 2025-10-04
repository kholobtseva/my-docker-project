# Test Cases: Kafka Data Pipeline

## Smoke & Integration Tests

### TC-KAFKA-001: Basic Kafka Connectivity
**Priority:** High  
**Type:** Smoke  
**Description:** Проверка доступности Kafka брокера и топиков  
**Preconditions:** 
- Все сервисы запущены: `docker-compose up -d`
- Kafka брокер здоров

**Test Steps:**
1. Проверить статус контейнеров: `docker-compose ps`.  
   ER: Все контейнеры в статусе "Up" 
2. Проверить список топиков: `docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092`.  
   ER: Топик market-data присутствует в списке.
3. Проверить доступность Kafdrop: http://localhost:9000.  
   ER: Kafdrop доступен и отображает топики

**Status:** ✅ Automated in CI  ✅ Manual  

**Evidence:** 
- `TC-KAFKA-001_step1_docker_containers_status.jpg`
- `TC-KAFKA-001_step2_kafka_topics_list.jpg` 
- `TC-KAFKA-001_step3_kafdrop_interface.jpg`

------------------------------------------------------

### TC-KAFKA-002: Manual Message Producing via AKHQ
**Priority:** High  
**Type:** Manual  
**Description:** Ручная отправка тестовых сообщений через AKHQ UI  
**Preconditions:** 
- AKHQ доступен: http://localhost:8080
- Топик `market-data` создан

**Test Steps:**
1. Открыть AKHQ в браузере.    
   ER: Интерфейс AKHQ открывается
2. Перейти в топик `market-data`.    
   ER: Отображается страница топика с информацией о партициях
3. Нажать "Produce to topic".  
   ER: Открывается форма для отправки сообщения
4. Ввести тестовое сообщение и отправить.  
   ER: Сообщение успешно отправлено, появляется подтверждение

**Test Data (читаемый формат):**   
```json
{
  "id_value": 999,
  "date": "2025-01-15",
  "price": 150.75,
  "contract": "MANUAL_TEST",
  "name_rus": "Тест ручного QA",
  "name_eng": "Manual QA Test",
  "source": "manual_test",
  "volume": 1000,
  "currency": "USD",
  "sync_timestamp": "2025-01-15T12:00:00Z"
}
```

**Test Data (для AKHQ):**
```
{"id_value":999,"date":"2025-01-15","price":150.75,"contract":"MANUAL_TEST","name_rus":"Тест ручного QA","name_eng":"Manual QA Test","source":"manual_test","volume":1000,"currency":"USD","sync_timestamp":"2025-01-15T12:00:00Z"}
```
**Evidence:** 
- `TC-KAFKA-002_step1_akhq_main.jpg`
- `TC-KAFKA-002_step2_topic_details.jpg`
- `TC-KAFKA-002_step3_produce_form.jpg`
- `TC-KAFKA-002_step4_message_sent.jpg`


**Status:** ✅ Manual
-----------------------------------------------------
### TC-KAFKA-003: Consumer Data Processing and CSV Export
**Priority:** High  
**Type:** Integration  
**Description:** Проверка обработки сообщений consumer'ом и экспорта в CSV  
**Preconditions:**
- Kafka consumer запущен и работает
- Топик `market-data` содержит сообщения

**Test Steps:**
1. Отправить тестовое сообщение через AKHQ.
   ```json
   {"id_value":999,"date":"2025-10-04","price":150.75,"contract":"MANUAL_TEST","name_rus":"Manual QA Test Data Processing","name_eng":"Manual QA Test Consumer Data Processing and CSV Export","source":"manual_test","volume":1000,"currency":"USD","sync_timestamp":"2025-10-04T12:00:00Z"}
   ```  
   ER: Сообщение появляется в топике market-data
2. Проверить логи consumer: `docker-compose logs kafka-consumer`.  
   ER: В логах присутствует запись о получении сообщения  
   ```bash
   docker-compose logs kafka-consumer --tail=20 > quality-assurance/test_results/TC-KAFKA-003_step2_consumer_logs.txt
   ```
4. Проверить создание CSV файла: `ls -la /app/logs/kafka_messages.csv`.  
   ER: CSV файл существует в указанной папке  
    ```bash
    docker-compose exec kafka-consumer ls -la /app/logs/ > quality-assurance/test_results/TC-KAFKA-003_step3_csv_file_check.txt
    ```
5. Проверить содержимое CSV файла.  
   ER: Файл содержит данные отправленного сообщения
    ```bash
    docker-compose exec kafka-consumer cat /app/logs/kafka_messages.csv > quality-assurance/test_results/TC-KAFKA-003_step5_data_normalization.txt
    ```
6. Проверить нормализацию данных в файле CSV.  
   ER: Все поля корректно нормализованы (без лишних пробелов)

**Evidence:** 
- `TC-KAFKA-003_step1_message_in_topic.jpg` - Тестовое сообщение отправлено через AKHQ UI
- `TC-KAFKA-003_step2_consumer_logs.txt` - Логи Kafka consumer с подтверждением получения сообщения
- `TC-KAFKA-003_step3_csv_file_check.txt` - Проверка существования и прав доступа CSV файла
- `TC-KAFKA-003_step4_csv_content.jpg` - Визуальная проверка структуры данных в CSV файле
- `TC-KAFKA-003_step5_data_normalization.txt` - Текстовый анализ нормализации данных в CSV

**Status:** ✅ Manual (можно автоматизировать позже)

--------
### TC-KAFKA-004: Kafka Service Recovery After Restart
**Priority:** Medium  
**Type:** Recovery  
**Description:** Проверка восстановления работы пайплайна после перезапуска Kafka  
**Preconditions:**
- Все сервисы запущены и работают
- Пайплайн данных функционирует нормально

**Test Steps:**
1. Остановить Kafka брокер:
    ```bash
    docker-compose stop kafka
    ```
   ER: Kafka контейнер останавливается
   
   Получить лог  
   ```bash
   docker-compose ps > quality-assurance/test_results/TC-KAFKA-004_step1_all_containers_status.txt
   ```
2. Запустить python-script при недоступном Kafka:
   ```bash
   docker-compose up python-script
   ```
   ER: Скрипт запускается, но не может подключиться к Kafka  
3. Просмотреть логи producer:  
    ```bash
    docker-compose logs python-script --tail=20
    ```  
   ER: В логах присутствуют сообщения об ошибках подключения к Kafka  
   Получить лог  
   ```bash
   docker-compose logs python-script > quality-assurance/test_results/TC-KAFKA-004_step2_python_script_logs.txt
   ```  
4. Проверить наличие в логах следующих сообщений об ошибках:  
- "DNS lookup failed for kafka:9092"
- "Name or service not known"
- "WARNING Failed to connect to Kafka: NoBrokersAvailable"
- "ERROR DNS lookup failed for kafka:9092"  
   ER: Хотя бы одно из сообщений об ошибках найдено в логах
5. Запустить Kafka:
    ```bash
    docker-compose start kafka
    ```
   ER: Kafka контейнер запускается  
   Получить лог.
   ```bash
   docker-compose ps | findstr "kafka" > quality-assurance/test_results/TC-KAFKA-004_step5_kafka_started.txt
   ```  
6. Подождать 30 секунд для восстановления соединения.
   ```bash
   sleep 30
   ```    
   ER: Соединение восстанавливается в течение 30 секунд
   
7. Отправить тестовое сообщение через AKHQ.
   ```json
   {"id_value": 1001, "date": "2025-10-04", "price": 155.50, "contract": "RECOVERY_TEST ", "name_rus": "Kafka Recovery Test", "source": "recovery_test", "volume": 500, "currency": "USD"}
   ```
   ER: Сообщение успешно отправляется в топик
8. Проверить что consumer обработал сообщение:
     ```bash
     docker-compose logs kafka-consumer --tail=10
     ```
   ER: В логах consumer присутствует запись об обработке нового сообщения  
   Получить лог.
   ```bash
   docker-compose logs kafka-consumer --tail=15 > 'quality-assurance/test_results/TC-KAFKA-004_step8_consumer_processing.txt'
   ```

  **Evidence:** 
- `TC-KAFKA-004_step1_all_containers_status.txt` - Подтверждение остановки Kafka контейнера
- `TC-KAFKA-004_step2_python_script_logs.txt` - Логи producer с ошибками подключения при недоступности Kafka
- `TC-KAFKA-004_step5_kafka_started.txt` - Подтверждение успешного запуска Kafka контейнера
- `TC-KAFKA-004_step8_message_sent.jpg` - Тестовое сообщение отправлено через AKHQ после восстановления
- `TC-KAFKA-004_step8_consumer_recovery.txt` - Логи consumer подтверждающие обработку сообщения после восстановления 

**Status:** ✅ Manual

---
### TC-KAFKA-005: Valid Message Processing
**Priority:** High  
**Type:** Validation  
**Description:** Проверка обработки сообщений с корректным форматом данных  
**Preconditions:**
- Все сервисы запущены
- Kafka пайплайн работает

**Test Steps:**
1. Отправить сообщение с корректным форматом через AKHQ.  
   ER: Сообщение успешно отправляется в топик market-data
   Test Data (для AKHQ):
   ```json
   {"id_value":200,"date":"2025-10-04","price":106.25,"contract":"FEFZ25","name_rus":"Iron Ore 62% Fe","name_eng":"Iron Ore Futures","source":"moex_sgx","volume":1500,"currency":"USD","sync_timestamp":"2025-10-04T12:00:00Z"}
   ```
2. Проверить что сообщение успешно обработано consumer'ом.  
   ER: В логах consumer присутствует запись об обработке сообщения
   ```bash
   docker-compose logs kafka-consumer --tail=20 > quality-assurance/test_results/TC-KAFKA-005_step2_consumer_logs.txt
   ```
3. Проверить что данные сохранены в CSV файле.  
   ER: CSV файл содержит данные отправленного сообщения
   ```bash
   docker-compose exec kafka-consumer cat /app/logs/kafka_messages.csv > quality-assurance/test_results/TC-KAFKA-005_step3_csv_content.txt
   ```
**Evidence:**

- TC-KAFKA-005_step1_message_sent.jpg - Отправка валидного сообщения через AKHQ UI
- TC-KAFKA-005_step2_consumer_logs.txt - Логи Kafka consumer с подтверждением обработки сообщения  
- TC-KAFKA-005_step3_csv_content.txt - Лог проверки данных в CSV файле
- TC-KAFKA-005_step3_csv_content.jpg - Визуальная проверка данных в CSV файле

Status: ✅ Manual

---
### TC-KAFKA-006: Invalid Date Format Handling
**Priority:** High  
**Type:** Validation  
**Description:** Проверка валидации некорректного формата даты  
**Preconditions:**
- Все сервисы запущены
- Kafka пайплайн работает

**Test Steps:**
1. Отправить сообщение с некорректной датой через AKHQ.  
   ER: Сообщение успешно отправляется в топик market-data
2. Проверить логи consumer на наличие предупреждений о невалидных данных.  
   ER: В логах consumer присутствуют предупреждения о невалидном формате даты

**Test Data (для AKHQ):**
```json
{"id_value":201,"date":"invalid-date","price":106.25,"contract":"FEFZ25"}
```
Status: ✅ Manual

---
### TC-KAFKA-007: Required Field Validation
**Priority:** High  
**Type:** Validation  
**Description:** Проверка валидации обязательных полей  
**Preconditions:**
- Все сервисы запущены
- Kafka пайплайн работает

**Test Steps:**
1. Отправить сообщение без обязательного поля "price" через AKHQ.  
   ER: Сообщение успешно отправляется в топик market-data
2. Проверить логи consumer на наличие ошибок валидации.  
   ER: В логах consumer присутствуют ошибки валидации обязательных полей

**Test Data (для AKHQ):**
```json
{"id_value":202,"date":"2025-01-15","contract":"FEFZ25"}
```
Status: ✅ Manual

---
### TC-KAFKA-008: Invalid JSON Handling
**Priority:** High  
**Type:** Error Handling  
**Description:** Проверка обработки невалидного JSON формата  
**Preconditions:**
- Все сервисы запущены
- Kafka пайплайн работает

**Test Steps:**
1. Отправить сообщение с невалидным JSON через AKHQ.  
   ER: Сообщение успешно отправляется в топик market-data
2. Проверить логи consumer на обработку ошибки парсинга.  
   ER: В логах consumer присутствуют ошибки парсинга JSON

**Test Data (для AKHQ):**
```json
{"id_value":203,"date":"2025-01-15","price":106.25,"contract":"FEFZ25","name_rus":"Железная руда 62% Fe","source":"moex_sgx"
```
Status: ✅ Manual

---
### TC-KAFKA-009: Empty Message Handling
**Priority:** Medium  
**Type:** Error Handling  
**Description:** Проверка обработки пустых сообщений  
**Preconditions:**
- Все сервисы запущены
- Kafka пайплайн работает

**Test Steps:**
1. Отправить пустое сообщение через AKHQ.  
   ER: Сообщение успешно отправляется в топик market-data
2. Проверить логи consumer на обработку пустого сообщения.  
   ER: В логах consumer присутствуют ошибки валидации пустого сообщения

**Test Data (для AKHQ):**
```json
{}
```
Status: ✅ Manual

---
### TC-KAFKA-010: Large Message Handling
**Priority:** Low  
**Type:** Performance  
**Description:** Проверка обработки сообщений большого объема  
**Preconditions:**
- Все сервисы запущены
- Kafka пайплайн работает

**Test Steps:**
1. Отправить сообщение с большим объемом данных через AKHQ.  
   ER: Сообщение успешно отправляется в топик market-data
2. Проверить что сообщение обработано без ошибок.  
   ER: В логах consumer отсутствуют ошибки обработки большого сообщения

**Test Data (для AKHQ):**
```json
{"id_value":204,"date":"2025-01-15","price":106.25,"contract":"FEFZ25","name_rus":"Железная руда 62% Fe - тест большого объема данных с дополнительным текстом","source":"moex_sgx","extra_field":"дополнительное_поле_с_длинным_значением"}
```

Status: ✅ Manual

---
### TC-KAFKA-011: Security Data Handling
**Priority:** High  
**Type:** Security  
**Description:** Проверка обработки потенциально опасных данных  
**Preconditions:**
- Все сервисы запущены
- Kafka пайплайн работает

**Test Steps:**
1. Отправить сообщение с потенциально опасными данными через AKHQ.  
   ER: Сообщение успешно отправляется в топик market-data
2. Проверить что данные экранируются или отклоняются.  
   ER: В CSV файле потенциально опасные данные корректно экранированы

**Test Data (для AKHQ):**
```json
{"id_value":205,"date":"2025-01-15; DROP TABLE agriculture_moex; --","price":106.25,"contract":"FEFZ25","name_rus":"<script>alert('xss')</script>","source":"moex_sgx"}
```

Status: ✅ Manual













