## 🧪 Test Case Results
✅ PASS - все ок  
❌ FAIL - тест не прошел  

### TC-DB-001: Подключение к базе данных и базовые операции

| Шаг | Действие | Ожидаемый результат | Фактический результат | Статус | Доказательства |
|-----|----------|---------------------|----------------------|--------|----------------|
| 1 | Проверить доступность PostgreSQL | PostgreSQL доступен | ✅ PostgreSQL accepting connections | PASS | ![Health](../screenshots/database_tests/TC-DB-001_step1_postgres_availability.JPG) |
| 2 | Проверить список таблиц | Отображается список таблиц | ✅ 3 таблицы отображаются | PASS | ![Tables](../screenshots/database_tests/TC-DB-001_step2_table_list.JPG) |
| 3 | Проверить существование основных таблиц | Все основные таблицы существуют | ✅ Все 3 таблицы найдены | PASS | ![Main Tables](../screenshots/database_tests/TC-DB-001_step3_main_tables.JPG) |
| 4 | Проверить количество записей | Таблица содержит записи (COUNT > 0) | ✅ 65 записей в таблице | PASS | ![Record Count](../screenshots/database_tests/TC-DB-001_step4_record_count.JPG) |

**Статус:** ✅ Manual ✅ PASSED

---

### TC-DB-002: Проверка целостности данных и ограничений

| Шаг | Действие | Ожидаемый результат | Фактический результат | Статус | Доказательства |
|-----|----------|---------------------|----------------------|--------|----------------|
| 1 | Проверить UNIQUE constraint в agriculture_moex | Нет дубликатов по UNIQUE constraint | ✅ 0 дубликатов найдено | PASS | ![Unique Constraint](../screenshots/database_tests/TC-DB-002_step1_unique_constraint.JPG) |
| 2 | Проверить PRIMARY KEY в www_data_idx | Нет дубликатов PRIMARY KEY | ✅ 0 дубликатов PRIMARY KEY | PASS | ![Primary Key](../screenshots/database_tests/TC-DB-002_step2_primary_key.JPG) |
| 3 | Проверить что все обязательные поля заполнены | Все обязательные поля содержат значения (COUNT = 0) | ✅ 0 записей с NULL значениями | PASS | ![Null Check](../screenshots/database_tests/TC-DB-002_step3_null_check.JPG) |

**Статус:** ✅ Manual ✅ PASSED

---

### TC-DB-003: Проверка механизма ON CONFLICT

| Шаг | Действие | Ожидаемый результат | Фактический результат | Статус | Доказательства |
|-----|----------|---------------------|----------------------|--------|----------------|
| 1 | Выбрать существующую запись | Возвращает существующую запись | ✅ Запись найдена: id_value=198, date_val=2025-07-23 | PASS | ![Select Record](../screenshots/database_tests/TC-DB-003_step1_select_record.JPG) |
| 2 | Вставить дубликат с ON CONFLICT | Не возникает ошибки UNIQUE violation | ✅ INSERT 0 1 - запись обновилась | PASS | ![Insert Conflict](../screenshots/database_tests/TC-DB-003_step2_insert_conflict.JPG) |
| 3 | Проверить обновление записи | avg_val=150, date_upd обновился | ✅ avg_val=150, date_upd=2025-10-09 16:36:22 | PASS | ![Verify Update](../screenshots/database_tests/TC-DB-003_step3_verify_update.JPG) |

**Статус:** ✅ Manual ✅ PASSED

---

### TC-DB-004: Проверка операций обновления данных

| Шаг | Действие | Ожидаемый результат | Фактический результат | Статус | Доказательства |
|-----|----------|---------------------|----------------------|--------|----------------|
| 1 | Проверить текущее значение health_status | health_status = 100 | ✅ health_status = 100 | PASS | ![Current Health](../screenshots/database_tests/TC-DB-004_step1_current_health.JPG) |
| 2 | Выполнить обновление health_status | UPDATE выполняется без ошибок | ✅ UPDATE 1 - успешно | PASS | ![Update Health](../screenshots/database_tests/TC-DB-004_step2_update_health.JPG) |
| 3 | Проверить обновление health_status | health_status = 0 | ✅ health_status = 0 | PASS | ![Verify Health](../screenshots/database_tests/TC-DB-004_step3_verify_health.JPG) |
| 4 | Обновить запись в agriculture_moex | Цена успешно обновляется | ✅ Цена обновлена на 999 | PASS | ![Update Agriculture](../screenshots/database_tests/TC-DB-004_step4_update_agriculture.JPG) |
| 5 | Восстановить исходные значения | Исходные значения восстановлены | ✅ health_status=100, цена восстановлена | PASS | ![Restore Values](../screenshots/database_tests/TC-DB-004_step5_restore_values.JPG) |

**Статус:** ✅ Manual ✅ PASSED

---

### TC-DB-005: Query Performance and Data Retrieval

| Шаг | Действие | Ожидаемый результат | Фактический результат | Статус | Доказательства |
|-----|----------|---------------------|----------------------|--------|----------------|
| 1 | Проверить время выполнения базового запроса | Запрос выполняется быстро (< 100ms) | ✅ Execution Time: 0.347 ms | PASS | ![Basic Query](../screenshots/database_tests/TC-DB-005_step1_basic_query.JPG) |
| 2 | Проверить запрос с JOIN | Запрос выполняется за разумное время (< 1 секунды) | ✅ Execution Time: 0.692 ms | PASS | ![Join Query](../screenshots/database_tests/TC-DB-005_step2_join_query.JPG) |
| 3 | Проверить что запросы выполняются за разумное время | Оба запроса < 1 секунды | ✅ Query1: 0.142ms, Query2: 0.696ms | PASS | ![Performance Check](../screenshots/database_tests/TC-DB-005_step3_performance_check.JPG) |

**Статус:** ✅ Manual ✅ PASSED

---

### TC-DB-006: Complex JOIN Queries Validation

| Шаг | Действие | Ожидаемый результат | Фактический результат | Статус | Доказательства |
|-----|----------|---------------------|----------------------|--------|----------------|
| 1 | JOIN запрос с названиями фьючерсов | Запрос выполняется без ошибок | ✅ 5 записей с русскими названиями | PASS | ![Join Query](../screenshots/database_tests/TC-DB-009_step1_join_query.JPG) |
| 2 | JOIN запрос с агрегацией | Агрегатные функции работают | ✅ COUNT и AVG возвращают данные | PASS | ![Aggregation Query](../screenshots/database_tests/TC-DB-009_step2_aggregation_query.JPG) |

**Статус:** ✅ Manual ✅ PASSED
