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
from models import GeneticConfig, GeneticConfigModel

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

CONFIG_FILENAME = "genetic_config.json"

def get_data_from_db():
    """Получение данных из базы данных"""
    db = DatabaseConnector()
    db.connect()
    data = db.fetch_initial_data()
    db.close()
    return data

def load_config_from_file() -> GeneticConfig:
    default_config = GeneticConfig()
    
    try:
        if os.path.exists(CONFIG_FILENAME):
            with open(CONFIG_FILENAME, 'r', encoding='utf-8') as f:
                saved_config = json.load(f)
                return GeneticConfig(
                    population_size=saved_config.get("population_size", default_config.population_size),
                    generations=saved_config.get("generations", default_config.generations),
                    elitism_rate=saved_config.get("elitism_rate", default_config.elitism_rate),
                    survival_rate=saved_config.get("survival_rate", default_config.survival_rate)
                )
    except Exception as e:
        logger.error(f"Ошибка при загрузке конфигурации: {e}")
    
    return default_config

def save_config_to_file(config: GeneticConfig) -> None:
    try:
        with open(CONFIG_FILENAME, 'w', encoding='utf-8') as f:
            json.dump({
                "population_size": config.population_size,
                "generations": config.generations,
                "elitism_rate": config.elitism_rate,
                "survival_rate": config.survival_rate
            }, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"Ошибка при сохранении конфигурации: {e}")

# загрузка конфигурации при старте
genetic_config = load_config_from_file()

# функции для изменения конфигурации
def set_population_size(value: int) -> None:
    global genetic_config
    if 50 <= value <= 1000:
        genetic_config.population_size = value
        save_config_to_file(genetic_config)
        logger.info(f"POPULATION_SIZE изменен на {value}")
    else:
        raise ValueError("POPULATION_SIZE должен быть между 50 и 1000")

def set_generations(value: int) -> None:
    global genetic_config
    if 50 <= value <= 1000:
        genetic_config.generations = value
        save_config_to_file(genetic_config)
        logger.info(f"GENERATIONS изменен на {value}")
    else:
        raise ValueError("GENERATIONS должен быть между 50 и 1000")

def set_elitism_rate(value: float) -> None:
    global genetic_config
    if 0.1 <= value <= 0.5:
        genetic_config.elitism_rate = value
        save_config_to_file(genetic_config)
        logger.info(f"ELITISM_RATE изменен на {value}")
    else:
        raise ValueError("ELITISM_RATE должен быть между 0.1 и 0.5")

def set_survival_rate(value: float) -> None:
    global genetic_config
    if 0.5 <= value <= 0.95:
        genetic_config.survival_rate = value
        save_config_to_file(genetic_config)
        logger.info(f"SURVIVAL_RATE изменен на {value}")
    else:
        raise ValueError("SURVIVAL_RATE должен быть между 0.5 и 0.95")

def get_current_config() -> GeneticConfigModel:
    global genetic_config
    return genetic_config.to_model()

def update_genetic_config(new_config: GeneticConfigModel) -> None:
    global genetic_config
    genetic_config = GeneticConfig.from_model(new_config)
    save_config_to_file(genetic_config)

DAYS_WEEK_EVEN = [d + "_ч" for d in ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]]
DAYS_WEEK_ODD = [d + "_з" for d in ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]]
DAYS_OF_WEEK = DAYS_WEEK_EVEN + DAYS_WEEK_ODD

Group = str
Subject = str
Teacher = str
LessonSlot = str
LessonType = str
DayOfWeek = str
Gene = List  # [Teacher, LessonSlot, Group, Subject, LessonType, DayOfWeek]
Schedule = List[Gene]

def generate_random_schedule() -> Schedule:
    schedule = []
    processed_id_paras = set()

    # Сначала обрабатываем связанные группы
    for id_para, group_info_list in linked_groups_by_id_para.items():
        if id_para in processed_id_paras:
            continue

        # Берем первую группу из списка, чтобы взять общие параметры
        first_group_info = group_info_list[0]
        group_name = first_group_info["group"]
        subject = first_group_info["subject"]
        lesson_type = first_group_info["lesson_type"]
        teacher = first_group_info["teacher"]

        # Проверяем, что учитель может вести этот предмет
        if subject not in teacher_subjects.get(teacher, []):
            # Если нет — ищем другого учителя
            available_teachers = [t for t, subjs in teacher_subjects.items() if subject in subjs]
            if not available_teachers:
                raise ValueError(f"Нет доступных учителей по предмету {subject} для поточной лекции")
            teacher = random.choice(available_teachers)

        # Генерируем общий слот для всех групп
        day = random.choice(DAYS_OF_WEEK)
        slot = random.choice(lesson_slots)

        # Проверяем доступность учителя
        slot_time = slot if isinstance(slot, str) else slot[0]
        if f"{day}|{slot_time}" not in teacher_availability.get(teacher, set()):
            # Ищем другой слот
            available_slots = [
                s for s in lesson_slots
                if f"{day}|{s if isinstance(s, str) else s[0]}" in teacher_availability.get(teacher, set())
            ]
            if available_slots:
                slot = random.choice(available_slots)
            else:
                # Ищем другой день
                available_days = [
                    d for d in DAYS_OF_WEEK
                    if f"{d}|{slot_time}" in teacher_availability.get(teacher, set())
                ]
                if available_days:
                    day = random.choice(available_days)
                else:
                    # Fallback — любой слот
                    slot = random.choice(lesson_slots)
                    day = random.choice(DAYS_OF_WEEK)

        # Создаём записи для всех групп в этом id_para
        for info in group_info_list:
            group = info["group"]
            gene = [
                teacher,
                slot,
                group,
                subject,
                lesson_type,
                day,
            ]
            schedule.append(gene)

        processed_id_paras.add(id_para)

    # Теперь обрабатываем остальные (не связанные) группы
    for (group, subject, lesson_type_key), count in group_subject_requirements.items():
        # Пропускаем группы, которые уже обработаны через linked_groups_by_id_para
        is_linked = any(
            group in [g["group"] for g in group_info_list]
            for group_info_list in linked_groups_by_id_para.values()
        )
        if is_linked:
            continue

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

    # Проверка поточных лекций
    for id_para, group_info_list in linked_groups_by_id_para.items():
        if len(group_info_list) < 2:
            continue

        # Получаем первые значения для сравнения
        first_group = group_info_list[0]["group"]
        first_gene = None
        for gene in schedule:
            if gene[2] == first_group:  # group
                first_gene = gene
                break

        if not first_gene:
            hard_constraints_violations += 1000  # очень серьёзное нарушение
            continue

        teacher_ref, slot_ref, _, _, _, day_ref = first_gene

        # Проверяем все остальные группы в этом id_para
        for info in group_info_list[1:]:
            group = info["group"]
            found = False
            for gene in schedule:
                if gene[2] == group:
                    t, s, g, subj, lt, d = gene
                    if t != teacher_ref or s != slot_ref or d != day_ref:
                        hard_constraints_violations += 1000  # нарушение поточности
                    found = True
                    break
            if not found:
                hard_constraints_violations += 1000

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

        # если конфликт или недоступность, то ищем альтернативу в parent2
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

    # После того, как child создан, проверяем связанные группы
    child_groups = set(gene[2] for gene in child)

    for id_para, group_info_list in linked_groups_by_id_para.items():
        group_names = [g["group"] for g in group_info_list]
        present_groups = [g for g in group_names if g in child_groups]

        if len(present_groups) == 0:
            continue

        # Берём первую группу из present_groups и её параметры
        first_group = present_groups[0]
        first_gene = next(gene for gene in child if gene[2] == first_group)
        teacher_ref, slot_ref, _, _, _, day_ref = first_gene

        # Для всех остальных групп в этом id_para — приводим к тем же параметрам
        for group_name in group_names:
            if group_name in child_groups:
                continue  # уже есть

            # Ищем в child запись для этой группы — если есть, заменяем
            for i, gene in enumerate(child):
                if gene[2] == group_name:
                    child[i] = [
                        teacher_ref,
                        slot_ref,
                        group_name,
                        gene[3],  # subject
                        gene[4],  # lesson_type
                        day_ref,
                    ]
                    break
            else:
                # Если нет — добавляем новую запись
                child.append([
                    teacher_ref,
                    slot_ref,
                    group_name,
                    group_info_list[0]["subject"],
                    group_info_list[0]["lesson_type"],
                    day_ref,
                ])

    return child


def mutate(schedule: Schedule) -> Schedule:
    idx = random.randint(0, len(schedule) - 1)
    teacher, lesson_slot, group, subject, lesson_type, day = schedule[idx]

    # Проверяем, принадлежит ли эта группа к связанному id_para
    linked_id_para = None
    for id_para, group_info_list in linked_groups_by_id_para.items():
        if any(g["group"] == group for g in group_info_list):
            linked_id_para = id_para
            break

    if linked_id_para:
        # Мутация затрагивает все группы в этом id_para
        group_names = [g["group"] for g in linked_groups_by_id_para[linked_id_para]]

        # Выбираем тип мутации
        mutation_type = random.random()

        if mutation_type < 0.4:
            # Меняем преподавателя — для всех групп
            available_teachers = [
                t for t, subjs in teacher_subjects.items()
                if subject in subjs and f"{day}|{lesson_slot if isinstance(lesson_slot, str) else lesson_slot[0]}" in teacher_availability.get(t, set())
            ]
            if available_teachers:
                new_teacher = random.choice(available_teachers)
                for i, gene in enumerate(schedule):
                    if gene[2] in group_names:
                        schedule[i][0] = new_teacher

        elif mutation_type < 0.8:
            # Меняем слот — для всех групп
            group_lessons = {l for t, l, g, s, lt, d in schedule if g in group_names and d == day}
            available_slots = [l for l in lesson_slots if l not in group_lessons]

            if available_slots:
                possible_slots = [
                    s for s in available_slots
                    if f"{day}|{s if isinstance(s, str) else s[0]}" in teacher_availability.get(teacher, set())
                ]
                if possible_slots:
                    new_slot = random.choice(possible_slots)
                else:
                    new_slot = random.choice(available_slots)
            else:
                possible_slots = [
                    s for s in lesson_slots
                    if f"{day}|{s if isinstance(s, str) else s[0]}" in teacher_availability.get(teacher, set())
                ]
                if possible_slots:
                    new_slot = random.choice(possible_slots)
                else:
                    new_slot = random.choice(lesson_slots)

            for i, gene in enumerate(schedule):
                if gene[2] in group_names:
                    schedule[i][1] = new_slot

        else:
            # Меняем день — для всех групп
            group_days = [d for t, l, g, s, lt, d in schedule if g in group_names]
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
            ] or least_busy_days

            new_day = random.choice(available_days)

            for i, gene in enumerate(schedule):
                if gene[2] in group_names:
                    schedule[i][5] = new_day

    else:
        # Обычная мутация — как раньше
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
            ] or least_busy_days

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
    global linked_groups_by_id_para  # <-- НОВОЕ

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
    linked_groups_by_id_para = db_data.get("linked_groups_by_id_para", {})  # <-- НОВОЕ

    # Используем конфигурацию вместо глобальных констант
    population = [generate_random_schedule() for _ in range(genetic_config.population_size)]

    for generation in range(genetic_config.generations):
        ranked = sorted([(calculate_fitness(ind), ind) for ind in population], reverse=True)

        elite = ranked[: int(genetic_config.population_size * genetic_config.elitism_rate)]
        survivors = ranked[: int(genetic_config.population_size * genetic_config.survival_rate)]

        best_fitness, best_schedule = max(ranked, key=lambda x: x[0])
        logger.debug(f"Поколение {generation}, Лучший балл: {best_fitness}")

        if best_fitness == 1_000_000:
            logger.debug(f"Идеальное решение найдено в поколении {generation}")
            return best_schedule

        new_generation = [ind for (fit, ind) in elite]

        while len(new_generation) < genetic_config.population_size:
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