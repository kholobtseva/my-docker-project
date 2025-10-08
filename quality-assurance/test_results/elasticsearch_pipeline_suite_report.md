## 🧪 Test Case Results
✅ PASS - все ок  
❌ FAIL - тест не прошел  

### TC-ES-001: Elasticsearch Service Connectivity

| Шаг | Действие | Ожидаемый результат | Фактический результат | Статус | Доказательства |
|-----|----------|---------------------|----------------------|--------|----------------|
| 1 | Проверить статус Elasticsearch | Status: "green" или "yellow" | ✅ Status: "yellow" (норма для single-node) | PASS | ![Health](../screenshots/elasticsearch_tests/TC-ES-001_step1_elasticsearch_health.JPG) |
| 2 | Проверить список индексов | Отображается список индексов | ✅ Индекс agriculture-data присутствует | PASS | ![Indices](../screenshots/elasticsearch_tests/TC-ES-001_step2_elasticsearch_indices.JPG) |
| 3 | Проверить количество документов | Индекс содержит данные | ✅ 1412 документов в индексе | PASS | ![Document Count](../screenshots/elasticsearch_tests/TC-ES-001_step3_agriculture_data_index.JPG) |

**Статус:** ✅ Manual ✅ PASSED

---

### TC-ES-002: PostgreSQL to Elasticsearch Data Synchronization

| Шаг | Действие | Ожидаемый результат | Фактический результат | Статус | Доказательства |
|-----|----------|---------------------|----------------------|--------|----------------|
| 1 | Проверить данные в Kibana Discover | Данные отображаются, все поля присутствуют | ✅ Данные отображаются, все поля присутствуют | PASS | ![Kibana Discover](../screenshots/elasticsearch_tests/TC-ES-002_step1_kibana_discover.JPG) |
| 2 | Проверить детали документа | Документ содержит все обязательные поля | ✅ Все поля присутствуют: id_value, date, price, contract, name_rus, source, sync_timestamp | PASS | ![Document Details](../screenshots/elasticsearch_tests/TC-ES-002_step2_document_details.JPG) |
| 3 | Проверить количество документов | Количество документов > 0 | ✅ 1412 документов в индексе | PASS | ![Document Count](../screenshots/elasticsearch_tests/TC-ES-002_step3_sample_data.JPG) |
| 4 | Сравнить с PostgreSQL | Количество в PostgreSQL ≈ количеству в ES | ✅ PostgreSQL: 2072 записей = ES: 2072 документов | PASS | ![PostgreSQL Count](../screenshots/elasticsearch_tests/TC-ES-002_step4_postgres_count.JPG) |

**Статус:** ✅ Manual ✅ PASSED

---

### TC-ES-003: Elasticsearch Search and Query Testing

| Шаг | Действие | Ожидаемый результат | Фактический результат | Статус | Доказательства |
|-----|----------|---------------------|----------------------|--------|----------------|
| 1 | Поиск по названию контракта FEFZ25 через Kibana Discover | Отображаются только документы с contract: FEFZ25 | ✅ Найдены документы с contract: FEFZ25 | PASS | ![Contract Search](../screenshots/elasticsearch_tests/TC-ES-003_step1_contract_search.JPG) |
| 2 | Поиск по диапазону цен 100-200 через Kibana Discover | Отображаются документы с price в диапазоне 100-200 | ✅ Найдены документы в указанном диапазоне цен | PASS | ![Price Range Search](../screenshots/elasticsearch_tests/TC-ES-003_step2_price_range_search.JPG) |
| 3 | Показать изменение объема торгов по дням через Kibana Visualize | Area chart показывает динамику объема торгов во времени | ✅ Area chart отображает изменение volume по датам | PASS | ![Volume Trend](../screenshots/elasticsearch_tests/TC-ES-003_step3_volume_trend.JPG) |
| 4 | Поиск по русскому тексту через Kibana Discover | Отображаются документы с name_rus содержащим "железная" | ✅ Найдены документы с русским текстом | PASS | ![Russian Text Search](../screenshots/elasticsearch_tests/TC-ES-003_step4_russian_text_search.JPG) |

**Статус:** ✅ Manual ✅ PASSED
