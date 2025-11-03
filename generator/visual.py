from tabulate import tabulate
from typing import List
import json

Gene = List[str]  # [Teacher, LessonSlot, Group, Subject, DayOfWeek]
Schedule = List[Gene]

DAYS_WEEK_EVEN = [d + "_ч" for d in ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]]
DAYS_WEEK_ODD = [d + "_з" for d in ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]]
DAYS_OF_WEEK = DAYS_WEEK_EVEN + DAYS_WEEK_ODD


def load_schedule_from_json(filename: str = "schedule.json") -> Schedule:
    try:
        with open(filename, encoding="utf-8") as f:
            data = json.load(f)

        schedule = []
        for group, days in data["schedule"].items():
            for day, lessons in days.items():
                for lesson in lessons:
                    schedule.append(
                        [lesson["lecturer"], lesson["time_slot"], group, lesson["subject"], day]
                    )
        return schedule
    except Exception as e:
        print(f"Ошибка при загрузке расписания: {e}")
        return []


def visualize_schedule(schedule: Schedule):
    from collections import defaultdict

    grouped_by_group = defaultdict(list)

    for gene in schedule:
        teacher, lesson_slot, group, subject, day = gene
        grouped_by_group[group].append({
            "День": day,
            "Время": lesson_slot,
            "Предмет": subject,
            "Преподаватель": teacher,
        })

    for group, lessons in grouped_by_group.items():
        print(f"\nРАСПИСАНИЕ ДЛЯ ГРУППЫ: {group}")
        sorted_lessons = sorted(lessons, key=lambda x: (DAYS_OF_WEEK.index(x["День"]), x["Время"]))
        print(tabulate(sorted_lessons, headers="keys", tablefmt="fancy_grid"))


if __name__ == "__main__":
    schedule = load_schedule_from_json("schedule.json")
    if schedule:
        visualize_schedule(schedule)
    else:
        print("Не удалось загрузить расписание.")
