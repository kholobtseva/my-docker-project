# Delivery Checklist

## Before Docker Hub Deployment

### ✅ Code Quality
- [ ] Все тесты пройдены в CI: `pytest tests/ -v`
- [ ] Код проходит линтеры (если используются)
- [ ] Коммит помечен тегом версии (например, 1.1.0)

### 🔧 Build Validation
- [ ] Dockerfile собирается без ошибок
- [ ] Размер образа оптимизирован
- [ ] requirements.txt актуальны

### 🐳 Container Readiness
- [ ] Контейнер запускается: `docker run -d kholobtseva/my-python-script:latest`
- [ ] Все environment variables документированы
- [ ] Health checks настроены

### 📊 Data Pipeline
- [ ] Пайплайн данных работает end-to-end
- [ ] Kafka producer/consumer корректно подключены
- [ ] Данные сохраняются в PostgreSQL и Elasticsearch

## During Deployment

### 🚀 Docker Hub
- [ ] Образ загружен с правильными тегами
- [ ] Описание обновлено на Docker Hub
- [ ] Версия соответствует git tag

### 🔍 Post-Deployment Verification
- [ ] Smoke tests пройдены на новом образе
- [ ] Все сервисы здоровы в docker-compose
- [ ] Данные flowing через обновленный пайплайн

## Quick Verification Commands
```bash
# Локальная сборка и тест
docker build -t my-python-script:test .
docker run -d my-python-script:test

# Проверка работы пайплайна
docker-compose up -d
docker-compose logs python-script

# Проверка данных
docker-compose exec postgres psql -U user -d my_db -c "SELECT COUNT(*) FROM agriculture_moex;"