# Test Cases: Elasticsearch Integration

## Elasticsearch & Kibana Tests

### TC-ES-001: Elasticsearch Service Connectivity
**Priority:** High  
**Type:** Smoke  
**Description:** Проверка доступности Elasticsearch и базовой функциональности  
**Preconditions:**
- Все сервисы запущены: `docker-compose up -d`
- Elasticsearch контейнер здоров

**Test Steps:**
1. Проверить статус Elasticsearch: `curl -X GET "http://localhost:9200/_cluster/health?pretty"`
2. Проверить список индексов: `curl -X GET "http://localhost:9200/_cat/indices?v"`
3. Проверить доступность Kibana: http://localhost:5601
4. Убедиться что индекс `agriculture-data` существует

**Expected Results:**
- Elasticsearch возвращает status: "green" или "yellow"
- Индекс `agriculture-data` присутствует в списке
- Kibana доступен в браузере
- Отсутствуют ошибки подключения

**Status:** ✅ Manual

---
### TC-ES-002: PostgreSQL to Elasticsearch Data Synchronization
**Priority:** High  
**Type:** Integration  
**Description:** Проверка корректной синхронизации данных из PostgreSQL в Elasticsearch  
**Preconditions:**
- Все сервисы запущены
- В PostgreSQL есть данные в таблице agriculture_moex
- Функция sync_to_elasticsearch() работает

**Test Steps:**
1. Запустить синхронизацию: `docker-compose exec python-script python -c "from main import sync_to_elasticsearch; sync_to_elasticsearch()"`
2. Проверить количество документов в Elasticsearch: `curl -X GET "http://localhost:9200/agriculture-data/_count?pretty"`
3. Проверить что данные синхронизированы: `curl -X GET "http://localhost:9200/agriculture-data/_search?pretty" -H 'Content-Type: application/json' -d'{"query":{"match_all":{}}, "size": 2}'`
4. Сравнить количество записей в PostgreSQL и Elasticsearch: `docker-compose exec postgres psql -U user -d my_db -c "SELECT COUNT(*) FROM agriculture_moex;"`

**Expected Results:**
- Количество документов в Elasticsearch ≈ количеству записей в PostgreSQL
- Документы в Elasticsearch содержат все необходимые поля
- Данные корректно преобразованы (числа как numbers, даты как dates)
- Отсутствуют ошибки синхронизации в логах

**Status:** ✅ Manual

---

### TC-ES-003: Elasticsearch Search and Query Testing
**Priority:** High  
**Type:** Search Validation  
**Description:** Проверка функциональности поиска и запросов в Elasticsearch  
**Preconditions:**
- Elasticsearch содержит синхронизированные данные
- Индекс agriculture-data заполнен

**Test Steps:**
1. Выполнить поиск по названию контракта: `curl -X GET "http://localhost:9200/agriculture-data/_search?pretty" -H 'Content-Type: application/json' -d'{"query":{"match":{"contract":"FEFZ25"}}}'`
2. Проверить поиск по диапазону цен: `curl -X GET "http://localhost:9200/agriculture-data/_search?pretty" -H 'Content-Type: application/json' -d'{"query":{"range":{"price":{"gte":100,"lte":200}}}}'`
3. Проверить агрегацию по контрактам: `curl -X GET "http://localhost:9200/agriculture-data/_search?pretty" -H 'Content-Type: application/json' -d'{"size":0,"aggs":{"contracts":{"terms":{"field":"contract.keyword","size":10}}}}'`
4. Проверить полнотекстовый поиск по русским названиям: `curl -X GET "http://localhost:9200/agriculture-data/_search?pretty" -H 'Content-Type: application/json' -d'{"query":{"match":{"name_rus":"железная"}}}'`

**Expected Results:**
- Поиск по контракту возвращает соответствующие документы
- Range запросы корректно фильтруют по ценам
- Агрегации возвращают правильные группировки
- Русский текст корректно индексируется и находится
- Запросы выполняются быстро (< 1 секунды)

**Status:** ✅ Manual

---
### TC-ES-004: Kibana Visualizations and Dashboards
**Priority:** Medium  
**Type:** Visualization  
**Description:** Проверка создания и работы визуализаций в Kibana  
**Preconditions:**
- Kibana доступен: http://localhost:5601
- Elasticsearch содержит данные в индексе agriculture-data
- Index pattern создан для agriculture-data

**Test Steps:**
1. Открыть Kibana в браузере
2. Перейти в раздел "Discover"
3. Проверить что данные отображаются корректно
4. Создать простую визуализацию (гистограмма цен по датам)
5. Создать pie chart распределения по контрактам
6. Сохранить визуализации в dashboard
7. Проверить обновление данных в реальном времени

**Expected Results:**
- Данные отображаются в разделе Discover
- Визуализации создаются без ошибок
- Графики корректно отображают данные (цены, объемы)
- Dashboard сохраняется и обновляется
- Русские названия отображаются корректно

**Status:** ✅ Manual

---
### TC-ES-005: Elasticsearch Service Recovery
**Priority:** Medium  
**Type:** Recovery  
**Description:** Проверка восстановления работы Elasticsearch после перезапуска  
**Preconditions:**
- Все сервисы запущены и работают
- Elasticsearch содержит данные

**Test Steps:**
1. Остановить Elasticsearch: `docker-compose stop elasticsearch`
2. Проверить что Kibana показывает ошибку подключения
3. Проверить что скрипт синхронизации логирует ошибки
4. Запустить Elasticsearch обратно: `docker-compose start elasticsearch`
5. Подождать 1 минуту для полного запуска
6. Проверить статус Elasticsearch: `curl -X GET "http://localhost:9200/_cluster/health?pretty"`
7. Проверить что Kibana восстановил работу
8. Запустить синхронизацию данных: `docker-compose exec python-script python -c "from main import sync_to_elasticsearch; sync_to_elasticsearch()"`

**Expected Results:**
- При остановке Elasticsearch Kibana показывает ошибки подключения
- Скрипт синхронизации обрабатывает ошибки без падений
- После запуска Elasticsearch статус становится "green" или "yellow"
- Kibana восстанавливает работу автоматически
- Синхронизация данных работает после восстановления

**Status:** ✅ Manual

---
### TC-ES-006: Elasticsearch Field Mapping Validation
**Priority:** Medium  
**Type:** Data Integrity  
**Description:** Проверка корректности маппинга полей в Elasticsearch индексе  
**Preconditions:**
- Elasticsearch содержит индекс agriculture-data
- Данные синхронизированы из PostgreSQL

**Test Steps:**
1. Получить маппинг индекса: `curl -X GET "http://localhost:9200/agriculture-data/_mapping?pretty"`
2. Проверить типы ключевых полей:
   - `price` должен быть `float`
   - `date` должен быть `date`
   - `contract` должен быть `text` и `keyword`
   - `name_rus` должен быть `text`
3. Проверить что русский текст поддерживается: `curl -X GET "http://localhost:9200/agriculture-data/_search?pretty" -H 'Content-Type: application/json' -d'{"query":{"match":{"name_rus":"руда"}}}'`
4. Проверить что числовые поля поддерживают агрегации

**Expected Results:**
- Поле `price` имеет тип `float`
- Поле `date` имеет тип `date` с корректным форматом
- Поле `contract` имеет multi-field mapping (`text` и `keyword`)
- Русский текст корректно индексируется и ищется
- Числовые поля поддерживают range queries и агрегации

**Status:** ✅ Manual

---
