# Test Cases: Kafka Data Pipeline

## Smoke Tests

### TC-KAFKA-001: Basic Kafka Connectivity
**Priority:** High  
**Type:** Smoke  
**Description:** Проверка доступности Kafka брокера и топиков  
**Preconditions:** 
- Все сервисы запущены: `docker-compose up -d`
- Kafka брокер здоров

**Test Steps:**
1. Проверить статус контейнеров: `docker-compose ps`
2. Проверить список топиков: `docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092`
3. Убедиться что топик `market-data` существует
4. Проверить доступность Kafdrop: http://localhost:9000

**Expected Results:**
- Все контейнеры в статусе "Up" 
- Топик `market-data` присутствует в списке
- Kafdrop доступен и отображает топики

**Status:** ✅ Automated in CI

---

### TC-KAFKA-002: Manual Message Producing via AKHQ
**Priority:** High  
**Type:** Manual  
**Description:** Ручная отправка тестовых сообщений через AKHQ UI  
**Preconditions:** 
- AKHQ доступен: http://localhost:8080
- Топик `market-data` создан

**Test Steps:**
1. Открыть AKHQ в браузере
2. Перейти в топик `market-data`
3. Нажать "Produce message"
4. Ввести тестовое сообщение:

**Test Data (читаемый формат):**   
```json
{
  "id_value": 999,
  "date": "2024-01-15",
  "price": 150.75,
  "contract": "MANUAL_TEST",
  "name_rus": "Тест ручного QA",
  "source": "manual_test"
}
```

**Test Data (для AKHQ):**
```
{"id_value":999,"date":"2024-01-15","price":150.75,"contract":"MANUAL_TEST","name_rus":"Тест ручного QA","source":"manual_test"}
```
