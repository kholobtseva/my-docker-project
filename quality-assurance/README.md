# Quality Assurance - My Docker Project

## 📋 Overview
QA процессы для микросервисного пайплайна данных с Kafka, PostgreSQL, Elasticsearch.

## 🎯 Testing Strategy
- **Unit Tests**: pytest для изолированного тестирования логики
- **Integration Tests**: End-to-end тестирование пайплайна данных  
- **Manual Testing**: Ручное тестирование Kafka через AKHQ/Kafdrop
- **CI/CD Validation**: Автоматическая проверка в GitHub Actions

## 📁 Structure
- `test_cases/` - Тест-кейсы и сценарии тестирования
- `bug_reports/` - Баг-репорты и анализ дефектов
- `checklists/` - Чек-листы для различных процессов