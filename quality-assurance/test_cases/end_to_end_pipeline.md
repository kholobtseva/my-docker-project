# Test Cases: End-to-End Pipeline (PowerShell Version)

## Complete Data Flow Tests

### TC-E2E-001: Full Pipeline Data Flow
**Priority:** High  
**Type:** End-to-End  
**Description:** Проверка полного цикла данных от API до конечных потребителей  
**Preconditions:**
- Все сервисы запущены
- Singapore Exchange API доступен
- Kafka топик market-data пуст

**Test Steps:**
1. Запустить полный пайплайн: `docker-compose up python-script`
2. В отдельных окнах PowerShell мониторить логи:
   - **Окно 1:** `docker-compose logs -f python-script`
   - **Окно 2:** `docker-compose logs -f kafka-consumer`
3. После завершения проверить логи: `docker-compose logs python-script | findstr "price volume"`
4. Проверить что данные прошли все этапы:
   - Данные получены от API ✅
   - Сохранены в PostgreSQL ✅  
   - Отправлены в Kafka ✅
   - Обработаны consumer'ом ✅
   - Сохранены в CSV ✅
   - Синхронизированы в Elasticsearch ✅

**Expected Results:**
- Данные проходят все этапы пайплайна без потерь
- В Kafka топике появляются сообщения
- CSV файл обновляется новыми данными
- Elasticsearch содержит актуальные данные
- Весь процесс завершается без ошибок

**Status:** ✅ Manual

---

### TC-E2E-002: Pipeline Recovery After Component Failure
**Priority:** High  
**Type:** Recovery  
**Description:** Проверка восстановления работы пайплайна после сбоя отдельных компонентов  
**Preconditions:**
- Все сервисы запущены и работают
- Пайплайн функционирует нормально

**Test Steps:**
1. Запустить мониторинг consumer: `docker-compose logs -f kafka-consumer`
2. Остановить Kafka брокер: `docker-compose stop kafka`
3. Запустить скрипт сбора данных: `docker-compose up python-script`
4. Наблюдать ошибки подключения к Kafka в логах
5. Запустить Kafka обратно: `docker-compose start kafka`
6. Подождать 2 минуты: `Start-Sleep -Seconds 120`
7. Проверить что данные начали поступать в Kafka
8. Проверить что consumer обработал накопленные сообщения
9. Убедиться что CSV файл содержит все данные

**Expected Results:**
- При недоступности Kafka producer логирует ошибки, но не падает
- После восстановления Kafka producer возобновляет отправку сообщений
- Consumer обрабатывает все накопленные сообщения
- Данные не теряются при временном сбое
- Пайплайн полностью восстанавливает работу

**Status:** ✅ Manual

---

### TC-E2E-003: Data Processing Order Validation
**Priority:** Medium  
**Type:** Data Integrity  
**Description:** Проверка сохранения порядка и последовательности обработки данных в пайплайне  
**Preconditions:**
- Все сервисы запущены
- Пайплайн работает стабильно

**Test Steps:**
1. Очистить CSV файл: `Remove-Item output.csv -ErrorAction SilentlyContinue`
2. Запустить скрипт сбора данных: `docker-compose up python-script`
3. В реальном времени отслеживать порядок обработки в логах:
   - Время получения данных от API
   - Время сохранения в PostgreSQL  
   - Время отправки в Kafka
   - Время обработки consumer'ом
   - Время записи в CSV
4. Проверить временные метки в CSV файле: `Get-Content output.csv | Select-Object -First 5`
5. Сравнить порядок записей в PostgreSQL и CSV

**Expected Results:**
- Данные обрабатываются в правильной последовательности: API → PostgreSQL → Kafka → Consumer → CSV
- Временные метки в CSV отражают реальное время обработки
- Порядок записей сохраняется на всех этапах
- Отсутствуют инверсии во времени обработки

**Status:** ✅ Manual

---

### TC-E2E-004: Data Integrity Across Pipeline Stages
**Priority:** High  
**Type:** Data Integrity  
**Description:** Проверка сохранения целостности и неизменности данных на всех этапах пайплайна  
**Preconditions:**
- Все сервисы запущены
- Singapore Exchange API доступен

**Test Steps:**
1. Запустить полный пайплайн: `docker-compose up python-script`
2. Выбрать несколько конкретных фьючерсов для отслеживания (например, FEFZ25, FEFU25)
3. Сравнить данные на каждом этапе:
   - **API уровень**: зафиксировать значения price, volume из логов
   - **PostgreSQL**: проверить те же значения в БД
   - **Kafka**: проверить сообщения в Kafdrop
   - **CSV**: проверить значения в конечном файле
   - **Elasticsearch**: проверить документы через Kibana
4. Для каждого отслеживаемого фьючерса убедиться что:
   - Цена (price) не изменилась
   - Объем (volume) сохранился
   - Контракт (contract) корректный
   - Дата (date) правильная

**Expected Results:**
- Данные идентичны на всех этапах пайплайна
- Числовые значения не искажаются (price, volume)
- Текстовые поля сохраняются без изменений
- Отсутствуют потери данных между этапам
- Все обязательные поля присутствуют везде

**Status:** ✅ Manual

---

### TC-E2E-005: Parallel Component Operation Testing
**Priority:** Medium  
**Type:** Performance  
**Description:** Проверка корректной работы пайплайна при параллельном выполнении компонентов  
**Preconditions:**
- Все сервисы запущены
- Kafka consumer работает постоянно

**Test Steps:**
1. Запустить постоянный мониторинг consumer: `docker-compose logs -f kafka-consumer`
2. Параллельно запустить сбор данных несколько раз подряд: 
   - `docker-compose up python-script`
   - Через 30 секунд повторно: `docker-compose up python-script`
3. Наблюдать за параллельной работой в логах:
   - Producer отправляет новые сообщения
   - Consumer продолжает обрабатывать сообщения
   - Отсутствуют конфликты в БД
4. Проверить что в CSV файле данные от всех запусков: `Get-Content output.csv`
5. Проверить отсутствие дубликатов в PostgreSQL

**Expected Results:**
- Producer и Consumer работают параллельно без конфликтов
- Новые сообщения добавляются в Kafka топик
- Consumer обрабатывает сообщения в реальном времени
- ON CONFLICT механизм в PostgreSQL предотвращает дубликаты
- CSV файл содержит данные от всех запусков
- Отсутствуют ошибки блокировок или конфликтов

**Status:** ✅ Manual

---

### TC-E2E-006: Large Volume Data Processing
**Priority:** Medium  
**Type:** Performance  
**Description:** Проверка обработки больших объемов данных и устойчивости пайплайна под нагрузкой  
**Preconditions:**
- Все сервисы запущены
- Singapore Exchange API доступен
- В БД есть исторические данные

**Test Steps:**
1. Изменить интервал данных на '3y' в main.py для получения большого объема данных
2. Запустить скрипт: `docker-compose up python-script`
3. Мониторить потребление ресурсов: `docker stats`
4. Отслеживать логи на предмет ошибок памяти или таймаутов
5. Проверить что все данные обработаны:
   - В PostgreSQL: `SELECT COUNT(*) FROM agriculture_moex;`
   - В Kafka: через Kafdrop проверить количество сообщений
   - В CSV: проверить размер файла и количество строк
6. Вернуть интервал обратно на '1w'

**Expected Results:**
- Система обрабатывает большой объем данных без падений
- Потребление памяти остается в разумных пределах
- Все данные успешно проходят через весь пайплайн
- Отсутствуют таймауты или ошибки переполнения
- Данные сохраняются полностью без потерь

**Status:** ✅ Manual