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
1. Проверить статус Elasticsearch: 
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:9200/_cluster/health?pretty" -Method Get
   ```
   ER: Elasticsearch возвращает status: "green" или "yellow"
   
2. Проверить список индексов: 
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:9200/_cat/indices?v" -Method Get
   ```
   ER: Индекс agriculture-data присутствует в списке
   
3. Проверить доступность Kibana: http://localhost:5601  
   **ER:** Kibana доступен и отображает индекс agriculture-data

**Status:** ✅ Manual

**Evidence:**
- TC-ES-001_step1_elasticsearch_health.JPG
- TC-ES-001_step2_elasticsearch_indices.JPG  
- TC-ES-001_step3_kibana_interface.JPG

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
1. Проверить данные в Kibana Discover
powershell
   Открыть Kibana: http://localhost:5601    
   Перейти в Discover → выбрать индекс *agriculture-data*  
   ER: Данные отображаются, все поля присутствуют
2. Проверить детали документа
   В Kibana Discover кликнуть на любой документ для просмотра деталей.
   ER: Документ содержит все поля:
   ```
   id_value, date, price, contract, name_rus, source, sync_timestamp
   ```
4. Проверить количество документов
   В Kibana сверху отображается total documents
   ER: Количество документов > 0
5. Сравниваем с PostgreSQL 
```powershell
docker-compose exec postgres psql -U user -d my_db -c "SELECT COUNT(*) FROM agriculture_moex;"
```
   ER: Количество записей в PostgreSQL ≈ количеству документов в Elasticsearch

**Evidence:**

- TC-ES-002_step2_documents_count.JPG
- TC-ES-002_step3_sample_data.JPG
- TC-ES-002_step4_postgres_count.JPG
- TC-ES-002_step5_sync_logs.JPG

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
1. Выполнить поиск по названию контракта FEFZ25 через Kibana Discover  
   Открыть Kibana:
   ```bash
   http://localhost:5601
   ``` 
   Перейти в Discover → добавить фильтр: *`contract: FEFZ25`*  
   ER: Отображаются только документы с contract: *FEFZ25*

3. Выполнить поиск по диапазону цен 100-200 через Kibana Discover  
   Добавить фильтр: *`price >= 100 AND price <= 200`*  
   ER: Отображаются документы с price в диапазоне 100-200

4. Проверить агрегацию по контрактам через Kibana Visualize  
   Создать pie chart по полю *`contract.keyword`*  
   ER: Pie chart показывает распределение по контрактам

5. Проверить поиск по русскому тексту через Kibana Discover  
   Добавить фильтр: *`name_rus: "железная"`*  
   ER: Отображаются документы с name_rus содержащим "железная"

**Evidence:**
- TC-ES-003_step1_contract_search.JPG
- TC-ES-003_step2_price_range_search.JPG  
- TC-ES-003_step3_contracts_aggregation.JPG
- TC-ES-003_step4_russian_text_search.JPG

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



