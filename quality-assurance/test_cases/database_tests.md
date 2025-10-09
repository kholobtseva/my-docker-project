# Test Cases: Database Operations

## PostgreSQL Integration Tests

### TC-DB-001: Database Connection and Basic Operations
**Priority:** High  
**Type:** Database Smoke  
**Description:** Проверка подключения к PostgreSQL и базовых операций  
**Preconditions:**
- Все сервисы запущены: `docker-compose up -d`
- PostgreSQL контейнер здоров

**Test Steps:**
1. Проверить доступность PostgreSQL:
   ```powershell
   docker-compose exec postgres pg_isready
  ER: PostgreSQL доступен (возвращает "accepting connections")  
2. Проверить список таблиц:
  ```powershell
  docker-compose exec postgres psql -U user -d my_db -c "\dt"
  ```
  ER: Отображается список таблиц в базе данных  
3. Проверить существование основных таблиц:
  ```powershell
  docker-compose exec postgres psql -U user -d my_db -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name IN ('www_data_idx', 'agriculture_moex', 'health_monitor');"
  ```
  ER: Все основные таблицы существуют (www_data_idx, agriculture_moex, health_monitor)  
4. Проверить количество записей в таблицах:
  ```powershell
  docker-compose exec postgres psql -U user -d my_db -c "SELECT COUNT(*) FROM www_data_idx;"
  ```
  ER: Таблица www_data_idx содержит записи (COUNT > 0)

**Evidence:**

- TC-DB-001_step1_postgres_availability.JPG
- TC-DB-001_step2_table_list.JPG  
- TC-DB-001_step3_main_tables.JPG
- TC-DB-001_step4_record_count.JPG

Status: ✅ Manual
  
---
### TC-DB-002: Data Integrity and Constraints Validation
**Priority:** High  
**Type:** Database Integrity  
**Description:** Проверка целостности данных и работы constraints в PostgreSQL  
**Preconditions:**

- База данных содержит тестовые данные
- Все таблицы созданы

**Test Steps:**
1. Проверить UNIQUE constraint в agriculture_moex:
     
   ```powershell
   docker-compose exec postgres psql -U user -d my_db -c "SELECT id_value, date_val, COUNT(*) FROM agriculture_moex GROUP BY id_value, date_val HAVING COUNT(*) > 1;"
   ```
  ER: Нет дубликатов по UNIQUE constraint (id_value, date_val)  

2. Проверить PRIMARY KEY в www_data_idx:  
   ```powershell
    docker-compose exec postgres psql -U user -d my_db -c "SELECT id, COUNT(*) FROM www_data_idx GROUP BY id HAVING COUNT(*) > 1;"
   ```
  ER: Нет дубликатов PRIMARY KEY в www_data_idx  
  
3. Проверить что все обязательные поля заполнены:  
       
  ```powershell
    docker-compose exec postgres psql -U user -d my_db -c "SELECT COUNT(*) FROM agriculture_moex WHERE id_value IS NULL OR date_val IS NULL;"
  ```  
  ER: Все обязательные поля содержат значения (COUNT = 0 для NULL проверок)    

**Evidence:**

- TC-DB-002_step1_unique_constraint.JPG
- TC-DB-002_step2_primary_key.JPG
- TC-DB-002_step3_null_check.JPG

**Status:** ✅ Manual

---

### TC-DB-003: ON CONFLICT Mechanism Validation
**Priority:** High  
**Type:** Database Integrity  
**Description:** Проверка работы механизма ON CONFLICT при вставке дублирующихся данных  
**Preconditions:**

- В таблице agriculture_moex есть существующие записи
- PostgreSQL доступен

**Test Steps:**
1. Выбрать существующую запись для теста:  
   ```powershell
   docker-compose exec postgres psql -U user -d my_db -c "SELECT id_value, date_val, avg_val FROM agriculture_moex LIMIT 1;"
   ```
   ER: Возвращает существующую запись

2. Запомнить id_value и date_val из шага 1, затем вставить дубликат:
   ```powershell
   docker-compose exec postgres psql -U user -d my_db -c "INSERT INTO agriculture_moex (id_value, date_val, min_val, max_val, avg_val, volume, currency) VALUES (id_value_real, 'date_val_real', 100, 200, 150, 1000, 'USD') ON CONFLICT (id_value, date_val) DO UPDATE SET min_val = EXCLUDED.min_val, max_val = EXCLUDED.max_val, avg_val = EXCLUDED.avg_val, volume = EXCLUDED.volume, currency = EXCLUDED.currency, date_upd = now();"
   ```
   ER: При вставке дубликата не возникает ошибки UNIQUE violation

3. Проверить что запись обновилась:
   ```powershell
   docker-compose exec postgres psql -U user -d my_db -c "SELECT avg_val, date_upd FROM agriculture_moex WHERE id_value = id_value_real AND date_val = 'date_val_real';"
   ```
   ER: Значение avg_val изменилось на 150, поле date_upd обновилось

**Evidence:**

- TC-DB-003_step1_select_record.JPG
- TC-DB-003_step2_insert_conflict.JPG
- TC-DB-003_step3_verify_update.JPG

**Status:** ✅ Manual

---

### TC-DB-004: Data Update Operations Validation
**Priority:** High  
**Type:** Database Operations  
**Description:** Проверка корректности операций обновления данных в таблицах  
**Preconditions:**

- В таблицах есть тестовые данные
- health_monitor содержит запись с id = 1012

**Test Steps:**
1. Проверить текущее значение health_status:
   ```powershell
   docker-compose exec postgres psql -U user -d my_db -c "SELECT health_status, date_upd FROM health_monitor WHERE id = 1012;"
   ```
   ER: health_status = 100

2. Выполнить обновление health_status:
   ```powershell
     docker-compose exec postgres psql -U user -d my_db -c "UPDATE health_monitor SET health_status = 0, date_upd = NOW() WHERE id = 1012;"
   ```
   ER: Операция UPDATE выполняется без ошибок

3. Проверить что значение обновилось:
   ```powershell
   docker-compose exec postgres psql -U user -d my_db -c "SELECT health_status FROM health_monitor WHERE id = 1012;"
   ```
   ER: health_status = 0

4. Проверить обновление agriculture_moex:
   ```powershell
   docker-compose exec postgres psql -U user -d my_db -c "SELECT id_value, date_val, avg_val FROM agriculture_moex LIMIT 1;"  
   ```
   Обновить цену (заменить id_value_real и date_val_real)    
   ```powershell
   docker-compose exec postgres psql -U user -d my_db -c "UPDATE agriculture_moex SET avg_val = 999, date_upd = NOW() WHERE id_value = id_value_real AND date_val = 'date_val_real';"
   ```
   ER: Цена успешно обновляется
   
5. Восстановить исходные значения:  
   Восстановить health_monitor
   ```powershell
   docker-compose exec postgres psql -U user -d my_db -c "UPDATE health_monitor SET health_status = 100, date_upd = NOW() WHERE id = 1012;"
   ```
   Восстановить agriculture_moex (заменить id_value_real и date_val_real)
   ```powershell
   docker-compose exec postgres psql -U user -d my_db -c "UPDATE agriculture_moex SET avg_val = исходное_значение, date_upd = NOW() WHERE id_value = id_value_real AND date_val = 'date_val_real';"
   ```
   ER: Исходные значения восстановлены

   **Evidence:**

- TC-DB-004_step1_current_health.JPG
- TC-DB-004_step2_update_health.JPG
- TC-DB-004_step3_verify_health.JPG
- TC-DB-004_step4_update_agriculture.JPG
- TC-DB-004_step5_restore_values.JPG

**Status:** ✅ Manual
   


   

---
### TC-DB-005: Query Performance and Data Retrieval
**Priority:** Medium  
**Type:** Database Performance  
**Description:** Проверка производительности основных запросов к данным  
**Preconditions:**
- Таблицы содержат достаточное количество записей
- PostgreSQL доступен

**Test Steps:**
1. Проверить время выполнения базового запроса: `docker-compose exec postgres psql -U user -d my_db -c "EXPLAIN ANALYZE SELECT COUNT(*) FROM agriculture_moex WHERE date_val > CURRENT_DATE - INTERVAL '30 days';"`
2. Проверить запрос с JOIN: `docker-compose exec postgres psql -U user -d my_db -c "EXPLAIN ANALYZE SELECT COUNT(*) FROM agriculture_moex am JOIN www_data_idx wdi ON am.id_value = wdi.id WHERE wdi.source = 'ore_futures';"`
3. Проверить что запросы выполняются за разумное время (< 1 секунды)

**Expected Results:**
- Базовые запросы выполняются быстро (< 100ms)
- Запросы с JOIN выполняются за разумное время
- Отсутствуют предупреждения о полном сканировании таблиц (Seq Scan)

**Status:** ✅ Manual

---
### TC-DB-005: Sequence Operations Validation
**Priority:** Medium  
**Type:** Database Operations  
**Description:** Проверка корректной работы последовательностей (sequences) в PostgreSQL  
**Preconditions:**
- Таблица www_data_idx содержит последовательность www_data_idx_id_seq
- PostgreSQL доступен

**Test Steps:**
1. Проверить текущее значение последовательности: `docker-compose exec postgres psql -U user -d my_db -c "SELECT last_value FROM www_data_idx_id_seq;"`
2. Проверить максимальный ID в таблице: `docker-compose exec postgres psql -U user -d my_db -c "SELECT MAX(id) FROM www_data_idx;"`
3. Вставить новую запись с автоматическим ID: `docker-compose exec postgres psql -U user -d my_db -c "INSERT INTO www_data_idx (mask, name_rus, name_eng, source, url) VALUES ('TEST', 'Тестовая запись', 'Test Record', 'test', 'http://test.com') RETURNING id;"`
4. Проверить что использовался следующий ID из последовательности
5. Удалить тестовую запись

**Expected Results:**
- Последовательность www_data_idx_id_seq существует и доступна
- Новый ID автоматически генерируется из последовательности
- ID новой записи = last_value + 1
- Последовательность увеличивается после каждой вставки

**Status:** ✅ Manual

---
### TC-DB-008: Data Types Validation
**Priority:** High  
**Type:** Database Integrity  
**Description:** Проверка корректности типов данных и форматов в таблицах  
**Preconditions:**
- Таблицы содержат тестовые данные
- PostgreSQL доступен

**Test Steps:**
1. Проверить типы данных в agriculture_moex: `docker-compose exec postgres psql -U user -d my_db -c "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'agriculture_moex';"`
2. Проверить что числовые поля содержат только числа: `docker-compose exec postgres psql -U user -d my_db -c "SELECT COUNT(*) FROM agriculture_moex WHERE id_value !~ '^[0-9]+$' OR min_val !~ '^[0-9.-]+$' OR max_val !~ '^[0-9.-]+$';"`
3. Проверить формат дат: `docker-compose exec postgres psql -U user -d my_db -c "SELECT COUNT(*) FROM agriculture_moex WHERE date_val::text !~ '^\d{4}-\d{2}-\d{2}$';"`
4. Проверить корректность валют: `docker-compose exec postgres psql -U user -d my_db -c "SELECT DISTINCT currency FROM agriculture_moex;"`

**Expected Results:**
- Все числовые поля содержат только числовые значения (COUNT = 0 для нечисловых проверок)
- Все даты в корректном формате YYYY-MM-DD
- Валюты соответствуют ожидаемым значениям (USD, etc.)
- Типы данных соответствуют схеме таблиц

**Status:** ✅ Manual

---
### TC-DB-009: Complex JOIN Queries Validation
**Priority:** Medium  
**Type:** Database Operations  
**Description:** Проверка корректности выполнения сложных запросов с JOIN между таблицами  
**Preconditions:**
- Таблицы www_data_idx и agriculture_moex содержат данные
- PostgreSQL доступен

**Test Steps:**
1. Выполнить JOIN запрос для получения данных с названиями фьючерсов: `docker-compose exec postgres psql -U user -d my_db -c "SELECT am.id_value, wdi.name_rus, am.date_val, am.avg_val, am.volume FROM agriculture_moex am JOIN www_data_idx wdi ON am.id_value = wdi.id WHERE wdi.source = 'ore_futures' LIMIT 5;"`
2. Проверить что запрос возвращает корректные данные
3. Выполнить запрос с агрегацией и JOIN: `docker-compose exec postgres psql -U user -d my_db -c "SELECT wdi.name_eng, COUNT(*) as record_count, AVG(am.avg_val) as avg_price FROM agriculture_moex am JOIN www_data_idx wdi ON am.id_value = wdi.id WHERE wdi.source = 'ore_futures' GROUP BY wdi.name_eng LIMIT 10;"`
4. Проверить корректность агрегированных данных

**Expected Results:**
- JOIN запросы выполняются без ошибок
- Данные корректно связываются между таблицами по id_value = id
- Агрегатные функции (COUNT, AVG) возвращают правильные значения
- Запросы возвращают ожидаемое количество записей

**Status:** ✅ Manual

---




