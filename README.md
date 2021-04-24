# yamdb_final

## Описание
API для проекта yamdb.

### Технологии
- Python 3.8.5
- Django 3.0.5
- DRF 3.11.0
- PostgreSQL 12.4
- nginx 1.19.3  
- Docker

### Требования
Необходим установленный и запущенный Docker.

Инструкции по установке см. [Docker](https://www.docker.com/get-started#h_installation)

### Первый запуск проекта
     
1. Клонирование репозитория 
```bash
git clone https://github.com/ImmensusFirst/yamdb_final.git
```
2. Подготовка

Заменить имя аккаунта и образ (immensusf/yamdb_final:1.0) на hub.docker.com на свой.

Добавить необходимые переменные (Git secrets):
```text
# django
SECRET_KEY=
SERVER_NAMES=
DB_NAME=
DB_HOST=
DB_PORT=
POSTGRES_USER=
POSTGRES_PASSWORD=

# docker
DOCKER_USERNAME=
DOCKER_PASSWORD=

# ssl
HOST=
USER=
SSH_KEY=
PASSPHRASE=

# telegram
TELEGRAM_TO=
TELEGRAM_TOKEN=
```
3. Запустить action yamdb_final workflow 

4. Запустить миграции и сбор статики 
```bash
-  docker-compose exec web sh migr_colstat.sh
``` 
5. Создать учетную запись администратора
```bash
- docker-compose exec web python manage.py createsuperuser
```
6. Загрузить в базу тестовых данных (по желанию) 
```bash
- docker-compose exec web python manage.py loaddata fixtures.json
```

### Регулярный запуск       
1. Запуск
```bash
- docker-compose up -d
```
2. При необходимости выполнить миграции и сбор статики 
```bash
- docker-compose exec web sh migr_colstat.sh
```
                         
### Об авторе
- [Rubtsov Dmitrii](https://github.com/ImmensusFirst)

### Статус Workflow
![Workflow](https://github.com/ImmensusFirst/yamdb_final/actions/workflows/yamdb_workflow.yaml/badge.svg)

### Рабочий вариант сервера
- [immensus.cf](http://immensus.cf/)