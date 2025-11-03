import asyncio
import json
import logging
import random
import os
from collections import defaultdict
from datetime import datetime
from typing import List, Tuple

from __init__ import SCHEDULE_FILENAME, SHEDULE_CREATION_LOCK
from connector import DatabaseConnector

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Константы
POPULATION_SIZE = 300
GENERATIONS = 300
ELITISM_RATE = 0.2
SURVIVAL_RATE = 0.8

CONFIG_FILENAME = "genetic_config.json"

def load_config_from_file():
    default_config = {
        "population_size": 300,
        "generations": 300,
        "elitism_rate": 0.2,
        "survival_rate": 0.8
    }
    
    try:
        if os.path.exists(CONFIG_FILENAME):
            with open(CONFIG_FILENAME, 'r', encoding='utf-8') as f:
                saved_config = json.load(f)
                for key in default_config:
                    if key in saved_config:
                        default_config[key] = saved_config[key]
    except Exception as e:
        logger.error(f"Ошибка при загрузке конфигурации: {e}")
    
    return default_config

def save_config_to_file(config):
    try:
        with open(CONFIG_FILENAME, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"Ошибка при сохранении конфигурации: {e}")

# загрузка конфигурации при старте
initial_config = load_config_from_file()
POPULATION_SIZE = initial_config["population_size"]
GENERATIONS = initial_config["generations"]
ELITISM_RATE = initial_config["elitism_rate"]
SURVIVAL_RATE = initial_config["survival_rate"]

# функции для изменения констант
def set_population_size(value: int):
    global POPULATION_SIZE
    if 50 <= value <= 1000:
        POPULATION_SIZE = value
        # Сохраняем в файл
        config = load_config_from_file()
        config["population_size"] = value
        save_config_to_file(config)
        logger.info(f"POPULATION_SIZE изменен на {value}")
    else:
        raise ValueError("POPULATION_SIZE должен быть между 50 и 1000")

def set_generations(value: int):
    global GENERATIONS
    if 50 <= value <= 1000:
        GENERATIONS = value
        config = load_config_from_file() #сохранение в файл
        config["generations"] = value
        save_config_to_file(config)
        logger.info(f"GENERATIONS изменен на {value}")
    else:
        raise ValueError("GENERATIONS должен быть между 50 и 1000")

def set_elitism_rate(value: float):
    global ELITISM_RATE
    if 0.1 <= value <= 0.5:
        ELITISM_RATE = value
        config = load_config_from_file()
        config["elitism_rate"] = value
        save_config_to_file(config)
        logger.info(f"ELITISM_RATE изменен на {value}")
    else:
        raise ValueError("ELITISM_RATE должен быть между 0.1 и 0.5")

def set_survival_rate(value: float):
    global SURVIVAL_RATE
    if 0.5 <= value <= 0.95:
        SURVIVAL_RATE = value
        config = load_config_from_file()
        config["survival_rate"] = value
        save_config_to_file(config)
        logger.info(f"SURVIVAL_RATE изменен на {value}")
    else:
        raise ValueError("SURVIVAL_RATE должен быть между 0.5 и 0.95")

def get_current_config():
    return {
        "population_size": POPULATION_SIZE,
        "generations": GENERATIONS,
        "elitism_rate": ELITISM_RATE,
        "survival_rate": SURVIVAL_RATE
    }


DAYS_WEEK_EVEN = [d + "_ч" for d in ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]]
DAYS_WEEK_ODD = [d + "_з" for d in ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]]
DAYS_OF_WEEK = DAYS_WEEK_EVEN + DAYS_WEEK_ODD

# Типы данных
Group = str
Subject = str
Teacher = str
LessonSlot = str
LessonType = str
DayOfWeek = str
Gene = List  # [Teacher, LessonSlot, Group, Subject, LessonType, DayOfWeek]
Schedule = List[Gene]

def get_data_from_db():
    db = DatabaseConnector()
    db.connect()
    data = db.fetch_initial_data()
    db.close()
    return data

def generate_random_schedule() -> Schedule:
    schedule = []
    for (group, subject, lesson_type_key), count in group_subject_requirements.items():
        available_teachers = [t for t, subjs in teacher_subjects.items() if subject in subjs]
        if not available_teachers:
            raise ValueError(f"Нет доступных учителей по предмету {subject}")

        for _ in range(count):
            teacher = random.choice(available_teachers)
            gene = [
                teacher,
                random.choice(lesson_slots),
                group,
                subject,
                lesson_type_key,  
                random.choice(DAYS_OF_WEEK),
            ]
            schedule.append(gene)
    return schedule

def calculate_fitness(schedule: Schedule) -> int:
    if len(schedule) != sum(group_subject_requirements.values()):
        return -1_000_000

    hard_constraints_violations = 0

    for day in DAYS_OF_WEEK:
        day_schedule = [gene for gene in schedule if gene[5] == day]

        teacher_lessons = defaultdict(set)
        group_lessons = defaultdict(set)

        for teacher, lesson_slot, group, subject, lesson_type, day in day_schedule:          
            if subject not in teacher_subjects.get(teacher, []):
                hard_constraints_violations += 1

            # доступность учителя
            slot_time = lesson_slot if isinstance(lesson_slot, str) else lesson_slot[0]
            slot_key = f"{day}|{slot_time}"
            if slot_key not in teacher_availability.get(teacher, set()):
                hard_constraints_violations += 1

            # коллизии по слоту у препода/группы
            if lesson_slot in teacher_lessons[teacher]:
                hard_constraints_violations += 1
            teacher_lessons[teacher].add(lesson_slot)

            if lesson_slot in group_lessons[group]:
                hard_constraints_violations += 1
            group_lessons[group].add(lesson_slot)

    subject_counts = defaultdict(int)
    for teacher, lesson_slot, group, subject, lesson_type, day in schedule:
        subject_counts[(group, subject, lesson_type)] += 1

    for (g, s, lt), required in group_subject_requirements.items():
        actual = subject_counts.get((g, s, lt), 0)
        hard_constraints_violations += abs(required - actual)

    return 1_000_000 - hard_constraints_violations * 10_000


def crossover(parent1: Schedule, parent2: Schedule) -> Schedule:
    child = []
    for gene in parent1:
        teacher, lesson_slot, group, subject, lesson_type, day = gene
 
        teacher_conflict = any(
            t == teacher and l == lesson_slot and d == day
            for t, l, g, s, lt, d in child
        )
        group_conflict = any(
            g == group and l == lesson_slot and d == day
            for t, l, g, s, lt, d in child
        )

        if not teacher_conflict and not group_conflict:
            # проверка доступности преподавателя
            slot_time = lesson_slot if isinstance(lesson_slot, str) else lesson_slot[0]
            if f"{day}|{slot_time}" in teacher_availability.get(teacher, set()):
                child.append(gene)
                continue

        # ели конфликт или недоступность, то ищем альтернативу в parent2
        alternatives = [
            g for g in parent2
            if g[2] == group and g[3] == subject and g[4] == lesson_type
        ]

        valid_alternatives = []
        for alt in alternatives:
            alt_teacher, alt_lesson, alt_group, alt_subject, alt_type, alt_day = alt
            teacher_ok = all(
                not (t == alt_teacher and l == alt_lesson and d == alt_day)
                for t, l, g, s, lt, d in child
            )
            group_ok = all(
                not (g == alt_group and l == alt_lesson and d == alt_day)
                for t, l, g, s, lt, d in child
            )

            slot_time = alt_lesson if isinstance(alt_lesson, str) else alt_lesson[0]
            availability_ok = f"{alt_day}|{slot_time}" in teacher_availability.get(alt_teacher, set())

            if teacher_ok and group_ok and availability_ok:
                valid_alternatives.append(alt)

        if valid_alternatives:
            child.append(random.choice(valid_alternatives))
        elif alternatives:
            child.append(random.choice(alternatives))
        else:
            child.append(gene)  # fallback

    return child


def mutate(schedule: Schedule) -> Schedule:
    idx = random.randint(0, len(schedule) - 1)
    teacher, lesson_slot, group, subject, lesson_type, day = schedule[idx]

    teacher_conflict = (
        sum(1 for t, l, g, s, lt, d in schedule if t == teacher and l == lesson_slot and d == day) != 1
    )
    group_conflict = (
        sum(1 for t, l, g, s, lt, d in schedule if g == group and l == lesson_slot and d == day) != 1
    )

    if not teacher_conflict and not group_conflict:
        return schedule

    mutation_type = random.random()

    if mutation_type < 0.4:
        lesson_type_key = lesson_type

        #те, кто ведёт этот предмет и доступен в это время
        slot_time = lesson_slot if isinstance(lesson_slot, str) else lesson_slot[0]
        available_teachers = [
            t for t, subjs in teacher_subjects.items()
            if subject in subjs and f"{day}|{slot_time}" in teacher_availability.get(t, set())
        ]

        if available_teachers:
            schedule[idx][0] = random.choice(available_teachers)

    elif mutation_type < 0.8:
        group_lessons = {l for t, l, g, s, lt, d in schedule if g == group and d == day}
        available_slots = [l for l in lesson_slots if l not in group_lessons]

        if available_slots:
            possible_slots = [
                s for s in available_slots
                if f"{day}|{s if isinstance(s, str) else s[0]}" in teacher_availability.get(teacher, set())
            ]
            if possible_slots:
                schedule[idx][1] = random.choice(possible_slots)
            else:
                schedule[idx][1] = random.choice(available_slots)
        else:
            possible_slots = [
                s for s in lesson_slots
                if f"{day}|{s if isinstance(s, str) else s[0]}" in teacher_availability.get(teacher, set())
            ]
            if possible_slots:
                schedule[idx][1] = random.choice(possible_slots)
            else:
                schedule[idx][1] = random.choice(lesson_slots)

    else:
        # подобрать наименее занятый день, но среди доступных для этого преподавателя/слота
        group_days = [d for t, l, g, s, lt, d in schedule if g == group]
        day_counts = {d: group_days.count(d) for d in DAYS_OF_WEEK}
        min_cnt = min(day_counts.values()) if day_counts else 0
        least_busy_days = [d for d, cnt in day_counts.items() if cnt == min_cnt]

        slot_time = lesson_slot if isinstance(lesson_slot, str) else lesson_slot[0]
        available_days = [
            d for d in least_busy_days
            if f"{d}|{slot_time}" in teacher_availability.get(teacher, set())
        ] or [
            d for d in DAYS_OF_WEEK
            if f"{d}|{slot_time}" in teacher_availability.get(teacher, set())
        ] or least_busy_days  # если совсем нет доступных — сохраняем старую логику

        schedule[idx][5] = random.choice(available_days)

    return schedule

def select_parent(ranked_population: List[Tuple[int, Schedule]]) -> Schedule:
    total_fitness = sum(max(fit, 0) for fit, ind in ranked_population)
    if total_fitness == 0:
        return random.choice(ranked_population)[1]

    pick = random.uniform(0, total_fitness)
    current = 0
    for fit, ind in ranked_population:
        current += max(fit, 0)
        if current > pick:
            return ind
    return ranked_population[0][1]

def genetic_algorithm() -> Schedule:
    global lesson_slots, groups, subjects, teachers, classrooms
    global group_subject_requirements, teacher_subjects, lesson_types, lock_slot, teacher_availability

    db_data = get_data_from_db()

    lesson_slots = db_data["lesson_slots"]
    groups = db_data["groups"]
    subjects = db_data["subjects"]
    teachers = db_data["teachers"]
    classrooms = db_data["classrooms"]
    group_subject_requirements = db_data["group_subject_requirements"]
    teacher_subjects = db_data["teacher_subjects"]
    lesson_types = db_data["lesson_types"]
    lock_slot = db_data["lock_slots"]
    teacher_availability = db_data["teacher_availability"]

    population = [generate_random_schedule() for _ in range(POPULATION_SIZE)]

    for generation in range(GENERATIONS):
        ranked = sorted([(calculate_fitness(ind), ind) for ind in population], reverse=True)

        elite = ranked[: int(POPULATION_SIZE * ELITISM_RATE)]
        survivors = ranked[: int(POPULATION_SIZE * SURVIVAL_RATE)]

        best_fitness, best_schedule = max(ranked, key=lambda x: x[0])
        logger.debug(f"Поколение {generation}, Лучший балл: {best_fitness}")

        if best_fitness == 1_000_000:
            logger.debug(f"Идеальное решение найдено в поколении {generation}")
            return best_schedule

        new_generation = [ind for (fit, ind) in elite]

        while len(new_generation) < POPULATION_SIZE:
            parent1 = select_parent(survivors)
            parent2 = select_parent(survivors)
            child = crossover(parent1, parent2)

            if random.random() < 0.1:
                child = mutate(child)
            new_generation.append(child)

        population = new_generation

    return max(population, key=calculate_fitness)

def schedule_to_dict(schedule: Schedule, generated_at: str, metadata: dict) -> dict:
    schedule_dict = {
        "metadata": {
            "generated_at": generated_at,
            "groups": metadata.get("groups", []),
            "subjects": metadata.get("subjects", []),
            "teachers": metadata.get("teachers", []),
            "lesson_slots": metadata.get("lesson_slots", []),
            "days_of_week": metadata.get("days_of_week", []),
            "locked_slots": metadata.get("locked_slots", [])
        },
        "schedule": {},
    }

    for teacher, lesson_slot, group, subject, lesson_type, day in schedule:
        if group not in schedule_dict["schedule"]:
            schedule_dict["schedule"][group] = {}
        if day not in schedule_dict["schedule"][group]:
            schedule_dict["schedule"][group][day] = []

        schedule_dict["schedule"][group][day].append({
            "lecturer": teacher,
            "subject": subject,
            "lesson_type": lesson_type,
            "time_slot": lesson_slot if isinstance(lesson_slot, str) else lesson_slot[0]
        })

    # обработка заблокированных слотов
    locked_slots_processed = set()
    for _, group, day, time_slot, even, odd in metadata.get("locked_slots", []):
        blocked_days = []
        if even:
            blocked_days.append(f"{day}_ч")
        if odd:
            blocked_days.append(f"{day}_з")
        
        for blocked_day in blocked_days:
            slot_key = (group, blocked_day, time_slot)
            if slot_key in locked_slots_processed:
                continue

            locked_slots_processed.add(slot_key)


            if group not in schedule_dict["schedule"]:
                schedule_dict["schedule"][group] = {}
            if blocked_day not in schedule_dict["schedule"][group]:
                schedule_dict["schedule"][group][blocked_day] = []

            existing_block = next(
                (item for item in schedule_dict["schedule"][group][blocked_day]
                 if item["subject"] == "Заблокировано админом" and item["time_slot"] == time_slot),
                None
            )

            if not existing_block:
                schedule_dict["schedule"][group][blocked_day].append({
                    "lecturer": "Админ",
                    "subject": "Заблокировано админом",
                    "lesson_type": "",
                    "time_slot": time_slot
                })

    return schedule_dict

def save_schedule_to_json(schedule: Schedule, filename: str = "schedule.json") -> None:
    generated_at = datetime.now().isoformat()
    metadata = {
        "groups": groups,
        "subjects": subjects,
        "teachers": teachers,
        "lesson_slots": lesson_slots,
        "days_of_week": DAYS_OF_WEEK,
        "locked_slots": lock_slot,
        "generated_at": generated_at
    }

    schedule_dict = schedule_to_dict(schedule, generated_at, metadata)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(schedule_dict, f, ensure_ascii=False, indent=4)

def load_schedule_from_json(filename: str = "schedule.json") -> Schedule:
    try:
        with open(filename, encoding="utf-8") as f:
            data = json.load(f)

        schedule = []
        for group, days in data["schedule"].items():
            for day, lessons in days.items():
                for lesson in lessons:
                    schedule.append(
                        [lesson["lecturer"], lesson["time_slot"], group, lesson["subject"], lesson.get("lesson_type", ""), day]
                    )
        return schedule
    except Exception as e:
        logger.error(f"Ошибка при загрузке расписания: {e}")
        return []

async def create_schedule_task() -> None:
    if not SHEDULE_CREATION_LOCK.locked():
        async with SHEDULE_CREATION_LOCK:
            try:
                schedule = await asyncio.to_thread(genetic_algorithm)
                save_schedule_to_json(schedule, SCHEDULE_FILENAME)
            except Exception as err:
                logger.critical(f"Error on schedule creation: {err}")

if __name__ == "__main__":
    try:
        best_schedule = genetic_algorithm()
        print("\nФинальное лучшее расписание найдено!")
        print(lock_slot)

        save = input("\nХотите сохранить расписание в JSON? (y/n): ").lower()
        if save == "y":
            filename = (
                input("Введите имя файла (по умолчанию schedule.json): ") or "schedule.json"
            )
            save_schedule_to_json(best_schedule, filename)
    except ValueError as e:
        print(f"Ошибка: {e}")
        print("Пожалуйста, проверьте введенные данные. Убедитесь, что по всем предметам назначен хотя бы один учитель.")