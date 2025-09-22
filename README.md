# My Docker Project

## Описание  
Python-скрипт для сбора данных с **MOEX ISS API** и сохранения в PostgreSQL

## Особенности
- Сбор данных по фьючерсам на сельхозтовары с Московской Биржи
- Автоматическое создание таблиц в PostgreSQL
- Docker-контейнеризация приложения

## Как запустить
```bash
git clone https://github.com/kholobtseva/my-docker-project.git
cd my-docker-project
docker-compose up --build

## 🛠 Технологии

**Backend:**
- ![Python](https://img.shields.io/badge/Python-3.9-blue?logo=python)
- ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql)
- ![Docker](https://img.shields.io/badge/Docker-✓-blue?logo=docker)
- ![Docker Compose](https://img.shields.io/badge/Docker_Compose-✓-blue?logo=docker)

**API:**
- ![MOEX ISS API](https://img.shields.io/badge/MOEX_ISS_API-✓-orange)

**Инструменты:**
- ![Git](https://img.shields.io/badge/Git-✓-lightgrey?logo=git)
- ![GitHub](https://img.shields.io/badge/GitHub-✓-lightgrey?logo=github)
