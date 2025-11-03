from collections import defaultdict
from typing import Any, Dict
import psycopg2
from decouple import config
import json
import pprint


class DatabaseConnector:
    POSTGRES_DB = config("POSTGRES_DB")
    POSTGRES_USER = config("POSTGRES_USER")
    POSTGRES_PASSWORD = config("POSTGRES_PASSWORD")
    POSTGRES_HOST = config("POSTGRES_HOST")
    POSTGRES_PORT = config("POSTGRES_PORT", default="5433", cast=int)

    CURSORS_TO_KEYS = {
        "cursor_lock_slot": "lock_slots",
        "cursor_classrooms": "classrooms",
        "cursor_groups": "groups",
        "cursor_subjects": "subjects",
        "cursor_teachers": "teachers",
        "cursor_times": "lesson_slots",
    }

    def __init__(self):
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = psycopg2.connect(
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            database=self.POSTGRES_DB,
            user=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD
        )
        self.cursor = self.conn.cursor()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def fetch_initial_data(self) -> Dict[str, Any]:
        if not self.cursor:
            raise ValueError("Соединение с БД не установлено")

        data = {}
        self.cursor.callproc("select_configuration")
        available_cursors: list[str] = self.cursor.fetchone()

        if available_cursors:
            for cursor_name in available_cursors:
                if cursor_name in self.CURSORS_TO_KEYS:
                    self.cursor.execute(f"FETCH ALL FROM {cursor_name}")
                    raw_data = self.cursor.fetchall()
                    key = self.CURSORS_TO_KEYS[cursor_name]
                    data[key] = raw_data

        #берем данные из вьюхи
        self.cursor.execute("""
            SELECT 
                teacher,
                subject,
                ls,
                group_name,
                COALESCE(seminars, 0) AS seminars,
                COALESCE(lectures, 0) AS lectures,
                COALESCE(labs, 0) AS labs
            FROM view_tgls_with_hours
        """)
        rows = self.cursor.fetchall()

        #теперь ключ делаем (group, subject, lesson_type)
        group_subject_requirements = defaultdict(int)
        teacher_subjects = defaultdict(list)
        lesson_types = {}

        for teacher_name, subject_name, lesson_type, group_name, seminars, lectures, labs in rows:
            seminars = int(seminars or 0)
            lectures = int(lectures or 0)
            labs = int(labs or 0)

            #определяем количество по типу
            if lesson_type.lower() == "семинар":
                count = seminars
            elif lesson_type.lower() == "лекция":
                count = lectures
            elif lesson_type.lower() == "лаба":
                count = labs
            else:
                count = 0

            if count <= 0:
                continue

            group_subject_requirements[(group_name, subject_name, lesson_type)] += count

            if subject_name not in teacher_subjects[teacher_name]:
                teacher_subjects[teacher_name].append(subject_name)

            lesson_types[(group_name, subject_name, teacher_name)] = lesson_type

        self.cursor.execute("""
            SELECT teacher, day, time, numerator, denominator
            FROM teacher_time
        """)
        teacher_time_rows = self.cursor.fetchall()

        teacher_availability = defaultdict(set)
        for teacher, day, time, numerator, denominator in teacher_time_rows:
            if numerator:
                teacher_availability[teacher].add(f"{day}_ч|{time}")
            if denominator:
                teacher_availability[teacher].add(f"{day}_з|{time}")

        data["teacher_availability"] = dict(teacher_availability)
        data["group_subject_requirements"] = dict(group_subject_requirements)
        data["teacher_subjects"] = dict(teacher_subjects)
        data["lesson_types"] = lesson_types

        return data


if __name__ == "__main__":
    connector = DatabaseConnector()
    connector.connect()
    try:
        data1 = connector.fetch_initial_data()
        pprint.pprint(data1)
    finally:
        connector.close()