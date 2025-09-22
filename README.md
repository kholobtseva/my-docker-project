# My Docker Project

## Описание  
Python-скрипт для сбора данных с **MOEX ISS API** и сохранения в PostgreSQL

## Особенности
- Сбор данных по фьючерсам на сельхозтовары с Московской Биржи
- Автоматическое создание таблиц в PostgreSQL
- Docker-контейнеризация приложения

## Как запустить

git clone https://github.com/kholobtseva/my-docker-project.git
cd my-docker-project
docker-compose up --build

## Технологии

**Backend:**  
<img src="https://img.shields.io/badge/Python-3.9-blue?logo=python" alt="Python"> 
<img src="https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql" alt="PostgreSQL"> 
<img src="https://img.shields.io/badge/Docker-✓-blue?logo=docker" alt="Docker"> 
<img src="https://img.shields.io/badge/Docker_Compose-✓-blue?logo=docker" alt="Docker Compose">

**API:**  
<img src="https://img.shields.io/badge/MOEX_ISS_API-✓-orange" alt="MOEX ISS API">

**Инструменты:**  
<img src="https://img.shields.io/badge/Git-✓-lightgrey?logo=git" alt="Git"> 
<img src="https://img.shields.io/badge/GitHub-✓-lightgrey?logo=github" alt="GitHub">

## 🐳 Docker Image

**Доступно на Docker Hub:**  
[![Docker Hub](https://img.shields.io/badge/Docker_Hub-Repository-2496ED?logo=docker&logoColor=white)](https://hub.docker.com/r/kholobtseva/my-python-script:1.0)
