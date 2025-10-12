# Test Cases: API Validation (PowerShell Version)

## API Integration Tests

### TC-API-001: Successful API Data Fetch
**Priority:** High  
**Type:** API Validation  
**Description:** Проверка успешного получения и обработки данных от внешнего API  
**Preconditions:**
- Интернет соединение доступно
- Singapore Exchange API доступен
- Все сервисы запущены

**Test Steps:**
1. Запустить основной скрипт: `docker-compose up python-script`
2. Проверить логи на успешное получение данных: `docker-compose logs python-script | findstr "successfully|processed"`
3. Убедиться что данные сохранены в PostgreSQL: `docker-compose exec postgres psql -U user -d my_db -c "SELECT COUNT(*) FROM agriculture_moex WHERE date_val >= CURRENT_DATE - INTERVAL '7 days';"`
4. Проверить синхронизацию с Elasticsearch через Kibana

**Expected Results:**
- API запрос выполняется успешно
- Данные корректно парсятся из JSON
- Записи добавляются в таблицу `agriculture_moex`
- Данные синхронизируются с Elasticsearch
- В логах отсутствуют ошибки

**Status:** ✅ Manual

---

### TC-API-002: Data Structure Validation
**Priority:** High  
**Type:** API Validation  
**Description:** Проверка корректной обработки валидной структуры данных от API  
**Preconditions:**
- Singapore Exchange API доступен
- Все сервисы запущены

**Test Steps:**
1. Запустить основной скрипт: `docker-compose up python-script`
2. Проверить логи на наличие предупреждений о данных: `docker-compose logs python-script | findstr "warning|error|failed"`
3. Проверить что все обязательные поля присутствуют в полученных данных
4. Убедиться что данные корректно сохраняются в БД с правильными типами

**Expected Results:**
- Система корректно обрабатывает все поля из API ответа
- Отсутствуют ошибки парсинга JSON
- Данные сохраняются с правильными типами
- Логи не содержат сообщений о проблемах с форматом данных

**Status:** ✅ Manual

---

### TC-API-003: Key Futures Data Validation
**Priority:** Medium  
**Type:** API Validation  
**Description:** Проверка успешного получения данных от API для ключевых фьючерсов  
**Preconditions:**
- Singapore Exchange API доступен
- Все сервисы запущены

**Test Steps:**
1. Запустить мониторинг логов: `docker-compose logs -f python-script`
2. Запустить основной скрипт: `docker-compose up python-script`
3. В логах отслеживать обработку ключевых фьючерсов: FEFZ25, FEFF26, FEFG26
4. Зафиксировать для каждого фьючерса статус в логах:
   - "daily-settlement-price-abs" - данные получены
   - "No data available" - данные отсутствуют

**Expected Results:**
- Для каждого ключевого фьючерса в логах есть четкий статус
- Отсутствуют ошибки парсинга JSON
- Система обрабатывает фьючерсы без падений

**Status:** ✅ Manual

---

### TC-API-004: Database Storage Validation  
**Priority:** High  
**Type:** Database Integration  
**Description:** Проверка корректного сохранения полученных данных в базу данных  
**Preconditions:**
- Скрипт успешно завершил работу
- Данные получены от API

**Test Steps:**
1. Проверить сохранение данных в БД за вчерашний день: `docker-compose exec postgres psql -U user -d my_db -c "SELECT COUNT(*) FROM agriculture_moex WHERE date_val = CURRENT_DATE - INTERVAL '1 day';"`
2. Проверить статус здоровья системы: `docker-compose exec postgres psql -U user -d my_db -c "SELECT health_status FROM health_monitor WHERE id = 1012;"`

**Expected Results:**
- В БД есть записи за вчерашний день (COUNT > 0)
- Статус здоровья системы = 100 (успешное выполнение)

**Status:** ✅ Manual

---

### TC-API-005: Weekly Data Update Without Duplicates
**Priority:** High  
**Type:** Data Integrity  
**Description:** Проверка недельного обновления данных без дублирования записей  
**Preconditions:**
- В БД уже есть данные за предыдущие дни
- Singapore Exchange API доступен

**Test Steps:**
1. Зафиксировать количество записей ДО запуска: `docker-compose exec postgres psql -U user -d my_db -c "SELECT COUNT(*) FROM agriculture_moex;"`
2. Запустить скрипт: `docker-compose up python-script`
3. Проверить логи на обработку данных за неделю
4. Зафиксировать количество записей ПОСЛЕ запуска: `docker-compose exec postgres psql -U user -d my_db -c "SELECT COUNT(*) FROM agriculture_moex;"`
5. Проверить что данные за последний рабочий день присутствуют: `docker-compose exec postgres psql -U user -d my_db -c "SELECT COUNT(*) FROM agriculture_moex WHERE date_val >= CURRENT_DATE - INTERVAL '3 days' AND date_val < CURRENT_DATE;"`

**Expected Results:**
- Количество записей ПОСЛЕ = количеству записей ДО (данные не дублируются)
- Данные за последние 3 дня (исключая сегодня) присутствуют в БД (COUNT > 0)
- В логах отсутствуют ошибки дублирования записей
- ON CONFLICT механизм работает корректно

**Status:** ✅ Manual