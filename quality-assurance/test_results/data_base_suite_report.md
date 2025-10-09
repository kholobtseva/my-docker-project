## 🧪 Test Case Results
✅ PASS - все ок  
❌ FAIL - тест не прошел  

### TC-DB-001: Database Connection and Basic Operations

| Шаг | Действие | Ожидаемый результат | Фактический результат | Статус | Доказательства |
|-----|----------|---------------------|----------------------|--------|----------------|
| 1 | Проверить доступность PostgreSQL | PostgreSQL доступен | ✅ PostgreSQL accepting connections | PASS | ![Health](../screenshots/database_tests/TC-DB-001_step1_postgres_availability.JPG) |
| 2 | Проверить список таблиц | Отображается список таблиц | ✅ 3 таблицы отображаются | PASS | ![Tables](../screenshots/database_tests/TC-DB-001_step2_table_list.JPG) |
| 3 | Проверить существование основных таблиц | Все основные таблицы существуют | ✅ Все 3 таблицы найдены | PASS | ![Main Tables](../screenshots/database_tests/TC-DB-001_step3_main_tables.JPG) |
| 4 | Проверить количество записей | Таблица содержит записи (COUNT > 0) | ✅ 65 записей в таблице | PASS | ![Record Count](../screenshots/database_tests/TC-DB-001_step4_record_count.JPG) |

**Статус:** ✅ Manual ✅ PASSED



### TC-DB-002: Data Integrity and Constraints Validation

| Шаг | Действие | Ожидаемый результат | Фактический результат | Статус | Доказательства |
|-----|----------|---------------------|----------------------|--------|----------------|
| 1 | Проверить UNIQUE constraint в agriculture_moex | Нет дубликатов по UNIQUE constraint | ✅ 0 дубликатов найдено | PASS | ![Unique Constraint](../screenshots/database_tests/TC-DB-002_step1_unique_constraint.JPG) |
| 2 | Проверить PRIMARY KEY в www_data_idx | Нет дубликатов PRIMARY KEY | ✅ 0 дубликатов PRIMARY KEY | PASS | ![Primary Key](../screenshots/database_tests/TC-DB-002_step2_primary_key.JPG) |
| 3 | Проверить что все обязательные поля заполнены | Все обязательные поля содержат значения (COUNT = 0) | ✅ 0 записей с NULL значениями | PASS | ![Null Check](../screenshots/database_tests/TC-DB-002_step3_null_check.JPG) |

**Статус:** ✅ Manual ✅ PASSED

---

### TC-DB-003: ON CONFLICT Mechanism Validation

| Шаг | Действие | Ожидаемый результат | Фактический результат | Статус | Доказательства |
|-----|----------|---------------------|----------------------|--------|----------------|
| 1 | Выбрать существующую запись | Возвращает существующую запись | ✅ Запись найдена: id_value=198, date_val=2025-07-23 | PASS | ![Select Record](../screenshots/database_tests/TC-DB-003_step1_select_record.JPG) |
| 2 | Вставить дубликат с ON CONFLICT | Не возникает ошибки UNIQUE violation | ✅ INSERT 0 1 - запись обновилась | PASS | ![Insert Conflict](../screenshots/database_tests/TC-DB-003_step2_insert_conflict.JPG) |
| 3 | Проверить обновление записи | avg_val=150, date_upd обновился | ✅ avg_val=150, date_upd=2025-10-09 16:36:22 | PASS | ![Verify Update](../screenshots/database_tests/TC-DB-003_step3_verify_update.JPG) |

**Статус:** ✅ Manual ✅ PASSED
