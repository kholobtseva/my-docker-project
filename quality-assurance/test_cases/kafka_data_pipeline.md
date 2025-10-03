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
1. Проверить статус контейнеров: `docker-compose ps`
2. Проверить список топиков: `docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092`
3. Убедиться что топик `market-data` существует
4. Проверить доступность Kafdrop: http://localhost:9000

**Expected Results:**
- Все контейнеры в статусе "Up" 
- Топик `market-data` присутствует в списке
- Kafdrop доступен и отображает топики

**Status:** ✅ Automated in CI

------------------------------------------------------

### TC-KAFKA-002: Manual Message Producing via AKHQ
**Priority:** High  
**Type:** Manual  
**Description:** Ручная отправка тестовых сообщений через AKHQ UI  
**Preconditions:** 
- AKHQ доступен: http://localhost:8080
- Топик `market-data` создан

**Test Steps:**
1. Открыть AKHQ в браузере
2. Перейти в топик `market-data`
3. Нажать "Produce message"
4. Ввести тестовое сообщение:

**Test Data (читаемый формат):**   
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

**Test Data (для AKHQ):**
```
{"id_value":999,"date":"2024-01-15","price":150.75,"contract":"MANUAL_TEST","name_rus":"Тест ручного QA","source":"manual_test"}
```
-----------------------------------------------------
### TC-KAFKA-003: Consumer Data Processing and CSV Export
**Priority:** High  
**Type:** Integration  
**Description:** Проверка обработки сообщений consumer'ом и экспорта в CSV  
**Preconditions:**
- Kafka consumer запущен и работает
- Топик `market-data` содержит сообщения

**Test Steps:**
1. Отправить тестовое сообщение через AKHQ (как в TC-KAFKA-002)
2. Проверить логи consumer: `docker-compose logs kafka-consumer`
3. Проверить создание CSV файла: `ls -la /app/logs/kafka_messages.csv`
4. Проверить содержимое CSV файла
5. Убедиться что данные корректно нормализованы

**Expected Results:**
- Consumer логирует получение сообщения
- CSV файл создан/обновлен в папке `/app/logs/`
- Данные в CSV содержат все обязательные поля
- Поля нормализованы (без лишних пробелов)

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
1. Остановить Kafka брокер: `docker-compose stop kafka`
2. Просмотреть логи producer: `docker-compose logs python-script --tail=20`
3. Проверить наличие в логах следующих сообщений об ошибках:
   - "Не удалось подключиться к Kafka"
   - "Kafka connection error" 
   - "NoBrokersAvailable"
   - "Failed to connect to Kafka"
4. Запустить Kafka обратно: `docker-compose start kafka`
5. Подождать 30 секунд для восстановления соединения
6. Отправить тестовое сообщение через AKHQ
7. Проверить что consumer обработал сообщение: `docker-compose logs kafka-consumer --tail=10`

**Expected Results:**
- После остановки Kafka в логах producer появляются сообщения об ошибках подключения
- Producer автоматически восстанавливает соединение после запуска Kafka
- Consumer продолжает обработку сообщений после восстановления
- CSV файл пополняется новыми сообщениями

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
1. Отправить сообщение с корректным форматом через AKHQ
2. Проверить что сообщение успешно обработано consumer'ом
3. Проверить что данные сохранены в CSV файле

**Test Data (для AKHQ):**
```json
{"id_value":200,"date":"2025-01-15","price":106.25,"contract":"FEFZ25","name_rus":"Железная руда 62% Fe","source":"moex_sgx"}
```
**Expected Results:**
- Сообщение успешно обрабатывается consumer'ом
- Данные корректно сохраняются в CSV файл
- В логах нет ошибок валидации

Status: ✅ Manual

---
### TC-KAFKA-06: Invalid Date Format Handling
**Priority:** High  
**Type:** Validation  
**Description:** Проверка валидации некорректного формата даты  
**Preconditions:**
- Все сервисы запущены
- Kafka пайплайн работает

**Test Steps:**
1. Отправить сообщение с некорректной датой через AKHQ
2. Проверить логи consumer на наличие предупреждений о невалидных данных

**Test Data (для AKHQ):**
```json
{"id_value":201,"date":"invalid-date","price":106.25,"contract":"FEFZ25"}
```
**Expected Results:**
- Сообщение с некорректной датой логируется с предупреждением
- Система валидации обнаруживает ошибку формата даты
- Некорректные данные не сохраняются в CSV

Status: ✅ Manual

---
### TC-KAFKA-07: Required Field Validation
**Priority:** High  
**Type:** Validation  
**Description:** Проверка валидации обязательных полей  
**Preconditions:**
- Все сервисы запущены
- Kafka пайплайн работает

**Test Steps:**
1. Отправить сообщение без обязательного поля "price" через AKHQ
2. Проверить логи consumer на наличие ошибок валидации

**Test Data (для AKHQ):**
```json
{"id_value":202,"date":"2025-01-15","contract":"FEFZ25"}
```
**Expected Results:**
- Отсутствие обязательного поля обнаруживается системой валидации
- Сообщение логируется с ошибкой missing required field
- Данные без обязательных полей не сохраняются в CSV

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
1. Отправить сообщение с невалидным JSON через AKHQ
2. Проверить логи consumer на обработку ошибки парсинга

**Test Data (для AKHQ):**
```json
{"id_value":203,"date":"2025-01-15","price":106.25,"contract":"FEFZ25","name_rus":"Железная руда 62% Fe","source":"moex_sgx"
```
**Expected Results:**
- Consumer не падает при получении невалидного JSON
- Ошибка парсинга логируется с понятным сообщением
- Система продолжает обрабатывать последующие корректные сообщения
  
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
1. Отправить пустое сообщение через AKHQ
2. Проверить логи consumer на обработку пустого сообщения

**Test Data (для AKHQ):**
```json
{}
```
**Expected Results:**

- Пустые сообщения не ломают consumer
- Ошибка валидации логируется с понятным сообщением
- Система продолжает работать корректно

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
1. Отправить сообщение с большим объемом данных через AKHQ
2. Проверить что сообщение обработано без ошибок

**Test Data (для AKHQ):**
```json
{"id_value":204,"date":"2025-01-15","price":106.25,"contract":"FEFZ25","name_rus":"Железная руда 62% Fe - тест большого объема данных с дополнительным текстом","source":"moex_sgx","extra_field":"дополнительное_поле_с_длинным_значением"}
```
**Expected Results:**
- Большие сообщения успешно обрабатываются
- Не возникает ошибок памяти или времени выполнения
- Данные корректно сохраняются в CSV

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
1. Отправить сообщение с потенциально опасными данными через AKHQ
2. Проверить что данные экранируются или отклоняются

**Test Data (для AKHQ):**
```json
{"id_value":205,"date":"2025-01-15; DROP TABLE agriculture_moex; --","price":106.25,"contract":"FEFZ25","name_rus":"<script>alert('xss')</script>","source":"moex_sgx"}
```
**Expected Results:**
- Потенциально опасные данные не вызывают уязвимостей
- Специальные символы экранируются в CSV
- Система не подвержена SQL-инъекциям или XSS атакам

Status: ✅ Manual

