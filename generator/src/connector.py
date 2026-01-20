from collections import defaultdict
from typing import Any, Dict
import psycopg2
from decouple import config
import pprint

class DatabaseConnector:
    POSTGRES_DB = config("POSTGRES_DB", default="postgres_db")
    POSTGRES_USER = config("POSTGRES_USER", default="chillout")
    POSTGRES_PASSWORD = config("POSTGRES_PASSWORD", default="P@ssw0rd@123")
    POSTGRES_HOST = config("POSTGRES_HOST", default="10.10.1.125")
    POSTGRES_PORT = config("POSTGRES_PORT", default="5433", cast=int)

    CURSORS_TO_KEYS = {
        "cursor_lock_slot": "lock_slots",
        "cursor_classrooms": "classrooms",
        "cursor_groups": "groups",
        "cursor_subjects": "subjects",
        "cursor_teachers": "teachers",
        "cursor_times": "lesson_slots",
        "cursor_teacher_time": "teacher_time",
        "cursor_tgsl": "tgls",
        "cursor_linking": "linking",  
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

        data: Dict[str, Any] = {}

        self.cursor.callproc("select_configuration")

        available_cursors = self.cursor.fetchone()

        for cursor_name in available_cursors:
            if not cursor_name:
                continue

            cursor_name = cursor_name.strip()

            if cursor_name not in self.CURSORS_TO_KEYS:
                continue

            self.cursor.execute(f'FETCH ALL FROM "{cursor_name}"')
            rows = self.cursor.fetchall()

            data[self.CURSORS_TO_KEYS[cursor_name]] = rows

        rows = data.get("tgls", [])

        group_subject_requirements = defaultdict(int)
        teacher_subjects = defaultdict(list)
        lesson_types = {}

        for (
            _id,
            teacher_name,
            subject_name,
            lesson_type,
            group_name,
            lectures,
            seminars,
            labs,
        ) in rows:
            seminars = int(seminars or 0)
            lectures = int(lectures or 0)
            labs = int(labs or 0)

            lt = lesson_type.lower()

            if lt == "семинар":
                count = seminars
            elif lt == "лекция":
                count = lectures
            elif lt == "лаба":
                count = labs
            else:
                continue

            if count <= 0:
                continue

            group_subject_requirements[(group_name, subject_name, lesson_type)] += count

            if subject_name not in teacher_subjects[teacher_name]:
                teacher_subjects[teacher_name].append(subject_name)

            lesson_types[(group_name, subject_name, teacher_name)] = lesson_type

        teacher_time_rows = data.get("teacher_time", [])

        teacher_availability = defaultdict(set)
        for _id, teacher, day, time, numerator, denominator in teacher_time_rows:
            if numerator not in (None, 0, '0'):
                teacher_availability[teacher].add(f"{day}_ч|{time}")
            if denominator not in (None, 0, '0'):
                teacher_availability[teacher].add(f"{day}_з|{time}")

        # --- НОВОЕ ---
        linking_rows = data.get("linking", [])
        linked_groups_by_id_para = defaultdict(list)
        for row in linking_rows:
            if len(row) >= 6:
                _, subject, lesson_type, teacher, group_name, id_para = row[:6]
                linked_groups_by_id_para[id_para].append({
                    "group": group_name,
                    "subject": subject,
                    "lesson_type": lesson_type,
                    "teacher": teacher,
                })

        # Убираем дубликаты по группе в рамках id_para
        for id_para, groups in linked_groups_by_id_para.items():
            unique_groups = []
            seen = set()
            for g in groups:
                if g["group"] not in seen:
                    unique_groups.append(g)
                    seen.add(g["group"])
            linked_groups_by_id_para[id_para] = unique_groups


        data["teacher_availability"] = dict(teacher_availability)
        data["group_subject_requirements"] = dict(group_subject_requirements)
        data["teacher_subjects"] = dict(teacher_subjects)
        data["lesson_types"] = lesson_types
        data["linked_groups_by_id_para"] = dict(linked_groups_by_id_para)  # <-- НОВОЕ

        return data

if __name__ == "__main__":
    connector = DatabaseConnector()
    connector.connect()
    try:
        data = connector.fetch_initial_data()
        pprint.pprint(data)
    finally:
        connector.close()