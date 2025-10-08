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

### TC-ES-002: PostgreSQL to Elasticsearch Data Synchronization

| Шаг | Действие | Ожидаемый результат | Фактический результат | Статус | Доказательства |
|-----|----------|---------------------|----------------------|--------|----------------|
| 1 | Проверить данные в Kibana Discover | Данные отображаются, все поля присутствуют | ✅ Данные отображаются, все поля присутствуют | PASS | ![Kibana Discover](../screenshots/elasticsearch_tests/TC-ES-002_step1_kibana_discover.JPG) |
| 2 | Проверить детали документа | Документ содержит все обязательные поля | ✅ Все поля присутствуют: id_value, date, price, contract, name_rus, source, sync_timestamp | PASS | ![Document Details](../screenshots/elasticsearch_tests/TC-ES-002_step2_document_details.JPG) |
| 3 | Проверить количество документов | Количество документов > 0 | ✅ 1412 документов в индексе | PASS | ![Document Count](../screenshots/elasticsearch_tests/TC-ES-002_step3_document_count.JPG) |
| 4 | Сравнить с PostgreSQL | Количество в PostgreSQL ≈ количеству в ES | ✅ PostgreSQL: 2072 записей = ES: 2072 документов | PASS | ![PostgreSQL Count](../screenshots/elasticsearch_tests/TC-ES-002_step4_postgres_count.JPG) |

**Статус:** ✅ Manual ✅ PASSED
