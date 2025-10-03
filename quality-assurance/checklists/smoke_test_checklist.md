# Smoke Test Checklist

## 🐳 Docker Services
- [ ] Все контейнеры running: `docker-compose ps`
- [ ] PostgreSQL доступен на порту 5432
- [ ] Kafka доступен на порту 9092
- [ ] Elasticsearch доступен на порту 9200

## 🔄 Kafka Pipeline
- [ ] Топик `market-data` существует
- [ ] Producer отправляет данные в Kafka
- [ ] Consumer получает сообщения из Kafka
- [ ] Данные сохраняются в CSV файл

## 📊 Data Validation
- [ ] CSV файл создается с заголовками
- [ ] Данные нормализуются (пробелы тримятся)
- [ ] Обязательные поля присутствуют