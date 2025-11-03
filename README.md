## Скелет микросервиса для автоматизированного формирования расписания занятий на основе предпочтений преподавателей и последующей скачки Excel файла

Мой первый web сайт
Синхронная обработка, тк сайт предназначен для 2-3 человек (Операции быстрые, поэтому ассинхронную обработку опустили с целью неусложнения кода)

# Compsoe 
WIP
# Сервисы
## Web
WIP
---

## Generator
## Startup
uvicorn api:app --reload --port 8000 запуск api


## ENV example
```
POSTGRES_DB="postgres_db"
POSTGRES_USER="pg"
POSTGRES_PASSWORD="pg"
#POSTGRES_HOST=postgres
POSTGRES_PORT=5433
WIKI_PORT=2048
POSTGRES_LOCAL_PORT=5432
```
