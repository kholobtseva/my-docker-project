### TC-API-001: Successful API Data Fetch
**Priority:** High  
**Type:** API Validation  
**Description:** Проверка успешного получения и обработки данных от внешнего API  
**Preconditions:**
- Интернет соединение доступно
- Singapore Exchange API доступен

**Test Steps:**
1. Запустить основной скрипт: `docker-compose up python-script`
2. Проверить логи на успешное получение данных
3. Убедиться что данные сохранены в PostgreSQL
4. Проверить синхронизацию с Elasticsearch

**Expected Results:**
- API запрос выполняется успешно
- Данные корректно парсятся из JSON
- Записи добавляются в таблицу `agriculture_moex`
- Данные синхронизируются с Elasticsearch

**Status:** ✅ Manual

---
### TC-API-002: Network Connectivity Issues
**Priority:** High  
**Type:** API Validation  
**Description:** Проверка обработки ошибок сети при недоступности внешнего API  
**Preconditions:**
- Интернет соединение изначально доступно

**Test Steps:**
1. Временно отключить интернет на машине
2. Запустить основной скрипт
3. Проверить логи на обработку network errors
4. Включить интернет обратно
5. Проверить восстановление работы

**Expected Results:**
- Network errors корректно обрабатываются
- В логах есть понятные сообщения об ошибках подключения
- Система не падает при временной недоступности API
- При восстановлении связи работа возобновляется

**Status:** ✅ Manual

---

### TC-API-003: Data Structure Validation
**Priority:** High  
**Type:** API Validation  
**Description:** Проверка корректной обработки валидной структуры данных от API  
**Preconditions:**
- Singapore Exchange API доступен

**Test Steps:**
1. Запустить основной скрипт
2. Проверить логи на наличие предупреждений о данных
3. Проверить что все обязательные поля присутствуют в полученных данных
4. Убедиться что данные корректно сохраняются в БД

**Expected Results:**
- Система корректно обрабатывает все поля из API ответа
- Отсутствуют ошибки парсинга JSON
- Данные сохраняются с правильными типами
- Логи не содержат сообщений о проблемах с форматом данных

**Status:** ✅ Manual

---

### TC-API-004: Empty API Response Handling
**Priority:** Medium  
**Type:** API Validation  
**Description:** Проверка обработки пустого или минимального ответа от API  
**Preconditions:**
- Singapore Exchange API доступен

**Test Steps:**
1. Запустить основной скрипт
2. Проверить логи на наличие записей типа "No data available"
3. Проверить что система не падает при минимальных данных
4. Убедиться что health status обновляется корректно

**Expected Results:**
- Система корректно обрабатывает сценарии с минимальными данными
- В логах есть информативные сообщения о статусе данных
- Отсутствуют ошибки парсинга при пустых ответах
- Health monitor отражает реальное состояние системы

**Status:** ✅ Manual

---
### TC-API-005: API Recovery After Temporary Unavailability
**Priority:** High  
**Type:** API Validation  
**Description:** Проверка восстановления работы после временной недоступности внешнего API  
**Preconditions:**
- Интернет соединение изначально доступно
- Все сервисы запущены и работают

**Test Steps:**
1. Запустить мониторинг логов: `docker-compose logs -f python-script`
2. В отдельном окне отключить интернет на 2-3 минуты
3. Наблюдать за логами в реальном времени
4. Зафиксировать появление ошибок подключения в логах
5. Включить интернет обратно
6. Наблюдать за логами в течение 5 минут
7. Проверить наличие новых записей в БД: `docker-compose exec postgres psql -U user -d my_db -c "SELECT COUNT(*) FROM agriculture_moex WHERE date_upd > NOW() - INTERVAL '10 minutes';"`
8. Проверить обновление health status: `docker-compose exec postgres psql -U user -d my_db -c "SELECT health_status FROM health_monitor WHERE id = 1012;"`

**Expected Results:**
- В течение 1 минуты после отключения интернета в логах появляются сообщения: "Network error", "Connection error", "Failed to connect"
- Система продолжает работу, не возникает критических ошибок
- В течение 3 минут после включения интернета в логах появляются сообщения об успешном получении данных
- В БД появляются новые записи с timestamp после восстановления связи
- Health status возвращается к значению 100 после восстановления работы

**Status:** ✅ Manual

---
### TC-API-006: API Data Retrieval Validation
**Priority:** High  
**Type:** API Validation  
**Description:** Проверка успешного получения данных от API для списка фьючерсов  
**Preconditions:**
- Singapore Exchange API доступен
- Все сервисы запущены и работают

**Test Steps:**
1. Запустить мониторинг логов: `docker-compose logs -f python-script`
2. Запустить основной скрипт: `docker-compose up python-script`
3. В логах отслеживать обработку фьючерсов: FEFV25, FEFX25, FEFZ25, FEFF26, FEFG26, FEFH26, FEFJ26, FEFK26, FEFM26, FEFN26, FEFQ26, FEFU26, FEFV26, FEFX26, FEFZ26, FEFF27, FEFG27, FEFH27, FEFJ27, FEFK27, FEFM27, FEFN27, FEFQ27, FEFU27, FEFV27, FEFX27, FEFZ27, FEFF28, FEFG28, FEFH28, FEFJ28, FEFK28, FEFM28, FEFN28, FEFQ28, FEFU28, FEFV28
4. Зафиксировать для каждого фьючерса один из статусов в логах:
   - "daily-settlement-price-abs" - данные получены
   - "No data available" - данные отсутствуют

**Expected Results:**
- Для каждого фьючерса в логах есть четкий статус (данные получены или отсутствуют)
- Отсутствуют ошибки парсинга JSON
- Система обрабатывает все фьючерсы без падений

**Status:** ✅ Manual

---
### TC-API-007: Database Storage Validation  
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
### TC-API-008: Weekly Data Update Without Duplicates
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

