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
