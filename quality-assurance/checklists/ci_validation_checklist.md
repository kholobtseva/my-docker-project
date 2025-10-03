# CI Validation Checklist

## Before Pushing to GitHub

### 🔍 Code Quality
- [ ] Код компилируется без ошибок: `python -m py_compile app/*.py`
- [ ] Синтаксис Python корректен
- [ ] Все импорты работают

### 🧪 Local Testing
- [ ] Все тесты проходят локально: `pytest tests/ -v`
- [ ] Покрытие тестами не уменьшилось
- [ ] Новый код покрыт тестами

### 🐳 Docker Validation
- [ ] Dockerfile собирается: `docker build -t ci-test .`
- [ ] requirements.txt актуальны
- [ ] Контейнер запускается: `docker run -d ci-test`

### 📁 Project Structure
- [ ] Все необходимые файлы присутствуют:
  - [ ] Dockerfile
  - [ ] docker-compose.yml  
  - [ ] requirements.txt
  - [ ] app/main.py
  - [ ] app/kafka_consumer.py
  - [ ] tests/ тестовые файлы

### 🔄 CI-Specific Checks
- [ ] GitHub Actions workflow файлы валидны
- [ ] Secrets не закоммичены в код
- [ ] Нет жестких путей (hardcoded paths)

## After CI Pipeline Run

### ✅ CI Results Verification
- [ ] Все jobs прошли успешно (зеленые галочки)
- [ ] Тесты выполнены в CI среде
- [ ] Docker образ собран и протестирован
- [ ] Нет warnings в логах CI

### 📊 Artifact Validation
- [ ] Docker образ загружен в Docker Hub (если применимо)
- [ ] Тестовые отчеты сгенерированы
- [ ] Бейджи статуса обновились в README

## Quick Local CI Simulation
```bash
# Запуск всех проверок как в CI
pytest tests/ -v
docker build -t ci-validation .
python -c "import app.main, app.kafka_consumer; print('✅ All imports work')"

# Проверка структуры проекта
[ -f "Dockerfile" ] && echo "✅ Dockerfile exists" || echo "❌ Dockerfile missing"
[ -f "docker-compose.yml" ] && echo "✅ docker-compose.yml exists" || echo "❌ docker-compose.yml missing"