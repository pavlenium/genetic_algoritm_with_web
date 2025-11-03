from asyncio import Lock

SCHEDULE_FILENAME = "schedule.json"
SHEDULE_CREATION_LOCK = Lock()  # Для защиты процесса создания расписания от race effect
