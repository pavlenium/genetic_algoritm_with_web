import json
import random
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Set, Tuple

import psycopg2
from tabulate import tabulate

# Подключение к базе данных
conn = psycopg2.connect(
    host="11.11.1.111",
    port="5433",
    database="database",
    user="user",
    password="password"
)

cursor = conn.cursor()

# Получение базовых данных
cursor.execute("SELECT name FROM times ORDER BY id;")
lesson_slots_db = cursor.fetchall()
lesson_slots = [slot[0] for slot in lesson_slots_db]

cursor.execute("SELECT * FROM groups ORDER BY id;")
groups_db = cursor.fetchall()
groups = [group[1] for group in groups_db]

cursor.execute("SELECT * FROM subjects;")
subjects_db = cursor.fetchall()
subjects = [slot[0] for slot in subjects_db]

cursor.execute("SELECT * FROM teachers;")
teachers_db = cursor.fetchall()
teachers = [slot[0] for slot in teachers_db]

cursor.execute("SELECT * FROM classrooms;")
classrooms_db = cursor.fetchall()
classrooms = [slot[0] for slot in classrooms_db]

# Получение данных о группах, предметах и преподавателях из одной таблицы
cursor.execute("""
    SELECT 
        json_array_elements_text(group_name::json) AS group_name,
        subject AS subject_name,
        teacher AS teacher_name,
        CASE 
            WHEN ls = 'лекция' THEN 2
            WHEN ls = 'семинар' THEN 1
            WHEN ls = 'лаба' THEN 1
            ELSE 0
        END AS hours
    FROM teacher_group_subject_ls
""")
schedule_data = cursor.fetchall()

# Формируем словарь требований по группам и предметам
group_subject_requirements = defaultdict(int)
teacher_subjects = defaultdict(list)

for group_name, subject_name, teacher_name, hours in schedule_data:
    group_subject_requirements[(group_name, subject_name)] += hours
    if subject_name not in teacher_subjects[teacher_name]:
        teacher_subjects[teacher_name].append(subject_name)

# Преобразуем defaultdict в обычный dict для удобства
group_subject_requirements = dict(group_subject_requirements)
teacher_subjects = dict(teacher_subjects)

conn.close()

# Константы
POPULATION_SIZE = 300
GENERATIONS = 300
ELITISM_RATE = 0.2
SURVIVAL_RATE = 0.8
DAYS_OF_WEEK = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]

# Типы данных
Group = str
Subject = str
Teacher = str
LessonSlot = str
DayOfWeek = str
Gene = List  # [Teacher, LessonSlot, Group, Subject, DayOfWeek]
Schedule = List[Gene]  # Расписание на всю неделю

def generate_random_schedule() -> Schedule:
    schedule = []
    for (group, subject), count in group_subject_requirements.items():
        available_teachers = [t for t, subjs in teacher_subjects.items() if subject in subjs]
        if not available_teachers:
            raise ValueError(f"Нет доступных учителей по предмету {subject}")

        for _ in range(count):
            gene = [
                random.choice(available_teachers),
                random.choice(lesson_slots),
                group,
                subject,
                random.choice(DAYS_OF_WEEK)  # Добавляем случайный день недели
            ]
            schedule.append(gene)
    return schedule


def calculate_fitness(schedule: Schedule) -> int:
    if len(schedule) != sum(group_subject_requirements.values()):
        return -1_000_000

    hard_constraints_violations = 0

    # Проверки для каждого дня отдельно
    for day in DAYS_OF_WEEK:
        day_schedule = [gene for gene in schedule if gene[4] == day]

        teacher_lessons = defaultdict(set)  # {teacher: {lesson_slots}}
        group_lessons = defaultdict(set)  # {group: {lesson_slots}}

        for teacher, lesson_slot, group, subject, day in day_schedule:
            # Проверка, может ли учитель преподавать предмет
            if subject not in teacher_subjects[teacher]:
                hard_constraints_violations += 1

            # Проверка, что учитель не занят в это время
            if lesson_slot in teacher_lessons[teacher]:
                hard_constraints_violations += 1
            teacher_lessons[teacher].add(lesson_slot)

            # Проверка, что группа не занята в это время
            if lesson_slot in group_lessons[group]:
                hard_constraints_violations += 1
            group_lessons[group].add(lesson_slot)

    # Проверка общего количества занятий по предметам
    subject_counts = defaultdict(int)
    for teacher, lesson_slot, group, subject, day in schedule:
        subject_counts[(group, subject)] += 1

    for (group, subject), required in group_subject_requirements.items():
        actual = subject_counts.get((group, subject), 0)
        hard_constraints_violations += abs(required - actual)

    # Проверка на лишние предметы
    for (group, subject), actual in subject_counts.items():
        if (group, subject) not in group_subject_requirements:
            hard_constraints_violations += actual

    return 1_000_000 - hard_constraints_violations * 10_000


def crossover(parent1: Schedule, parent2: Schedule) -> Schedule:
    child = []
    for gene in parent1:
        teacher, lesson_slot, group, subject, day = gene

        # Проверка конфликтов в родителе 1
        teacher_conflict = sum(1 for t, l, g, s, d in parent1
                               if t == teacher and l == lesson_slot and d == day) != 1
        group_conflict = sum(1 for t, l, g, s, d in parent1
                             if g == group and l == lesson_slot and d == day) != 1

        if not teacher_conflict and not group_conflict:
            child.append(gene)
        else:
            # Поиск альтернатив в родителе 2
            alternatives = [g for g in parent2
                            if g[2] == group and g[3] == subject]

            # Фильтрация альтернатив без конфликтов
            valid_alternatives = []
            for alt in alternatives:
                alt_teacher, alt_lesson, alt_group, alt_subject, alt_day = alt
                teacher_ok = sum(1 for t, l, g, s, d in child
                                 if t == alt_teacher and l == alt_lesson and d == alt_day) == 0
                group_ok = sum(1 for t, l, g, s, d in child
                               if g == alt_group and l == alt_lesson and d == alt_day) == 0
                if teacher_ok and group_ok:
                    valid_alternatives.append(alt)

            if valid_alternatives:
                child.append(random.choice(valid_alternatives))
            else:
                child.append(random.choice(alternatives))

    return child


def mutate(schedule: Schedule) -> Schedule:
    idx = random.randint(0, len(schedule) - 1)
    teacher, lesson_slot, group, subject, day = schedule[idx]

    # Проверка конфликтов
    teacher_conflict = sum(1 for t, l, g, s, d in schedule
                           if t == teacher and l == lesson_slot and d == day) != 1
    group_conflict = sum(1 for t, l, g, s, d in schedule
                         if g == group and l == lesson_slot and d == day) != 1

    if not teacher_conflict and not group_conflict:
        return schedule

    mutation_type = random.random()

    if mutation_type < 0.4:  # Мутация преподавателя
        available_teachers = [t for t, subjs in teacher_subjects.items()
                              if subject in subjs]
        schedule[idx][0] = random.choice(available_teachers)

    elif mutation_type < 0.8:  # Мутация времени
        # Доступные слоты, где группа свободна в этот день
        group_lessons = {l for t, l, g, s, d in schedule
                         if g == group and d == day}
        available_slots = [l for l in lesson_slots if l not in group_lessons]

        if available_slots:
            schedule[idx][1] = random.choice(available_slots)
        else:
            schedule[idx][1] = random.choice(lesson_slots)

    else:  # Мутация дня
        # Доступные дни, где у группы меньше занятий
        group_days = [d for t, l, g, s, d in schedule if g == group]
        day_counts = {d: group_days.count(d) for d in DAYS_OF_WEEK}
        least_busy_days = [d for d, cnt in day_counts.items()
                           if cnt == min(day_counts.values())]
        schedule[idx][4] = random.choice(least_busy_days)

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


def visualize_schedule(schedule: Schedule):
    """Отображает расписание по дням недели."""
    for day in DAYS_OF_WEEK:
        day_schedule = [gene for gene in schedule if gene[4] == day]

        if not day_schedule:
            print(f"\n{day}: Нет занятий")
            continue

        time_schedule = defaultdict(lambda: defaultdict(list))
        used_slots = {lesson[1] for lesson in day_schedule}

        for teacher, slot, group, subject, day in day_schedule:
            entry = f"{teacher}: {subject}"
            time_schedule[slot][group].append(entry)

        # Подготовка данных для таблицы
        table = []
        headers = ["Время"] + groups

        for slot in lesson_slots:
            if slot not in used_slots:
                continue
            row = [slot]
            for group in groups:
                lessons = time_schedule[slot].get(group, [])
                if len(lessons) > 1:
                    row.append("КОНФЛИКТ!\n" + "\n".join(lessons))
                elif lessons:
                    row.append("\n".join(lessons))
                else:
                    row.append("---")
            table.append(row)

        print(f"\n{day}:")
        print(tabulate(table, headers=headers, tablefmt="grid", stralign="left"))

    print("\nПримечания:")
    print("- КОНФЛИКТ! означает несколько занятий в одно время")
    print("- --- означает отсутствие занятий")
    print(f"Общий балл пригодности: {calculate_fitness(schedule)}")
    print("-----------------")


def genetic_algorithm() -> Schedule:
    population = [generate_random_schedule() for _ in range(POPULATION_SIZE)]

    for generation in range(GENERATIONS):
        ranked = sorted([(calculate_fitness(ind), ind)
                         for ind in population], reverse=True)

        elite = ranked[:int(POPULATION_SIZE * ELITISM_RATE)]
        survivors = ranked[:int(POPULATION_SIZE * SURVIVAL_RATE)]

        best_fitness, best_schedule = max(ranked, key=lambda x: x[0])
        print(f"Поколение {generation}, Лучший балл: {best_fitness}")

        if generation % 10 == 0:  # Показываем прогресс каждые 10 поколений
            visualize_schedule(best_schedule)

        if best_fitness == 1_000_000:
            print(f"Идеальное решение найдено в поколении {generation}")
            return best_schedule

        new_generation = [ind for (fit, ind) in elite]

        while len(new_generation) < POPULATION_SIZE:
            parent1 = select_parent(survivors)
            parent2 = select_parent(survivors)
            child = crossover(parent1, parent2)

            if random.random() < 0.1:  # Вероятность мутации
                child = mutate(child)
            new_generation.append(child)

        population = new_generation

    return max(population, key=calculate_fitness)

def schedule_to_dict(schedule: Schedule) -> dict:
    # DAY_TRANSLATIONS = {
    #     "Понедельник": "Mon",
    #     "Вторник": "Tue",
    #     "Среда": "Wed",
    #     "Четверг": "Thu",
    #     "Пятница": "Fri",
    #     "Суббота": "Sat",
    #     "Воскресенье": "Sun"
    # }

    schedule_dict = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "groups": groups,
            "subjects": subjects,
            "teachers": teachers,
            "lesson_slots": lesson_slots,
            "days_of_week": DAYS_OF_WEEK
        },
        "schedule": {}
    }

    for gene in schedule:
        teacher, lesson_slot, group, subject, day = gene

        if group not in schedule_dict["schedule"]:
            schedule_dict["schedule"][group] = {}

        if day not in schedule_dict["schedule"][group]:
            schedule_dict["schedule"][group][day] = []

        schedule_dict["schedule"][group][day].append({
            "lecturer": teacher,
            "subject": subject,
            "time_slot": lesson_slot
        })

    return schedule_dict

def save_schedule_to_json(schedule: Schedule, filename: str = "schedule.json"):
    schedule_dict = schedule_to_dict(schedule)

    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(schedule_dict, f, ensure_ascii=False, indent=4)
        print(f"Расписание успешно сохранено в файл {filename}")
    except Exception as e:
        print(f"Ошибка при сохранении файла: {e}")

    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(schedule_dict, f, ensure_ascii=False, indent=4)
        print(f"Расписание успешно сохранено в файл {filename}")
    except Exception as e:
        print(f"Ошибка при сохранении файла: {e}")

def load_schedule_from_json(filename: str = "schedule.json") -> Schedule:
    try:
        with open(filename, encoding="utf-8") as f:
            data = json.load(f)

        schedule = []
        for group, days in data["schedule"].items():
            for day, lessons in days.items():
                for lesson in lessons:
                    schedule.append([
                        lesson["lecturer"],
                        lesson["time_slot"],
                        group,
                        lesson["subject"],
                        day
                    ])
        return schedule
    except Exception as e:
        print(f"Ошибка при загрузке расписания: {e}")
        return []


if __name__ == "__main__":
    try:
        best_schedule = genetic_algorithm()
        print("\nФинальное лучшее расписание:")
        visualize_schedule(best_schedule)
        save = input("\nХотите сохранить расписание в JSON? (y/n): ").lower()
        if save == "y":
            filename = input("Введите имя файла (по умолчанию schedule.json): ") or "schedule.json"
            save_schedule_to_json(best_schedule, filename)
    except ValueError as e:
        print(f"Ошибка: {e}")
        print("Пожалуйста, проверьте введенные данные. Убедитесь, что по всем предметам назначен хотя бы один учитель.")
