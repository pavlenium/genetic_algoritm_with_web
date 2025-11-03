import ast

import psycopg2
from decouple import config

from app.postgre.sqlz import *  # прописанные SQL запросы


class Connect:
    POSTGRES_DB = config("POSTGRES_DB")
    POSTGRES_USER = config("POSTGRES_USER")
    POSTGRES_PASSWORD = config("POSTGRES_PASSWORD")
    POSTGRES_HOST = config("POSTGRES_HOST")
    POSTGRES_PORT = config("POSTGRES_LOCAL_PORT", default="5433", cast=int)  # 5432 in docker subnet

    def __init__(self):
        self.conn = psycopg2.connect(
            database=self.POSTGRES_DB,
            user=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT
        )
        self.cur = self.conn.cursor()
        # print('Подключение к БД успешно')

    def create_tables(self):
        """Создание таблиц (без заполнения)"""
        try:
            self.cur.execute(CREATE_TEACHERS_TABLE)
            self.cur.execute(CREATE_GROUPS_TABLE)
            self.cur.execute(CREATE_SUBJECTS_TABLE)
            self.cur.execute(CREATE_TIMES_TABLE)
            self.cur.execute(CREATE_CLASSROOMS_TABLE)
            # self.cur.execute(CREATE_GS)
            # self.cur.execute(CREATE_TS)
            self.cur.execute(CREATE_TEACHER_GROUP_SUBJECT_LS_TABLE)
            self.cur.execute(CREATE_TEACHER_TIME_TABLE)
            self.cur.execute(CREATE_TABLE_PROPERTY)
            self.cur.execute(CREATE_BODY_CLASSROOM_TABLE)
            self.cur.execute(CREATE_HOURS_TABLE)
            self.cur.execute(CREATE_LOCK_SLOT_TABLE)
            self.cur.execute(KIRILL_SQL)
            self.cur.execute(CREATE_LINKING_TABLE)
            self.conn.commit()
            print("Таблицы успешно созданы или уже существуют.")
            return True
        except Exception as e:
            print(f"Ошибка при создании таблиц {e}.")
            return False

    def select_teach_subj(self) -> dict:
        """Вытягивание данных из таблицы teacher_to_subject в формате {'teacher': 'subject', ...} (устарела)"""
        try:
            self.cur.execute(TEACHER_TO_SUBJECT)
            rows = self.cur.fetchall()
            ts = {}
            for row in rows:
                if row[0] in ts:
                    ts[row[0]].append(row[1])
                else:
                    ts[row[0]] = [row[1]]
            return ts
        except Exception as e:
            print(f"Ошибка при вытягивании данных преподаватель - предмет {e}.")
            return {}

    def select_group_subj(self) -> dict:
        """Вытягивание данных из таблицы group_to_subject в формате {('group', 'subject'): 'hours', ...} (устарела)"""
        try:
            self.cur.execute(GROUP_TO_SUBJECT)
            rows = self.cur.fetchall()
            ts = {}
            for row in rows:
                ts[row[0], row[1]] = row[2]
            return ts
        except Exception as e:
            print(f"Ошибка при вытягивании данных преподаватель - предмет {e}.")
            return {}

    def select_groups(self) -> dict:
        """Вытягивание данных из таблицы groups в формате {'group_name': 'Count_people_in_group', ...}"""
        try:
            self.cur.execute(SELECT_GROUPS)
            rows = self.cur.fetchall()
            result = {}
            for row in rows:
                result[row[0]] = row[1]
            return result
        except Exception as e:
            print(f"Ошибка при вытягивании данных о группах: {e}.")
            return {}

    def select_property(self) -> list:
        """Вытягивание данных из таблицы property в формате ['property1', 'property2', ...]"""
        try:
            self.cur.execute(SELECT_PROPERTY)
            rows = self.cur.fetchall()
            result = [row[0] for row in rows]
            return result
        except Exception as e:
            print(f"Ошибка при вытягивании данных о свойствах: {e}.")
            return []

    def select_subjects_dict(self) -> dict:
        """Вытягивание данных из таблицы subjects в формате {'subject_name': ['property1', 'property3', ...], ...}"""
        try:
            self.cur.execute(SELECT_SUBJECTS_DICT)
            rows = self.cur.fetchall()
            result = {}
            for row in rows:
                result[row[0]] = ast.literal_eval(row[1])
            return result
        except Exception as e:
            print(f"Ошибка при вытягивании данных о группах: {e}.")
            return {}

    def select_subjects(self) -> list:
        """Вытягивание данных из таблицы subjects в формате ['subject1', 'subject2', ...]"""
        try:
            self.cur.execute(SELECT_SUBJECTS)
            rows = self.cur.fetchall()
            result = []
            for row in rows:
                result.append(row[0])
            return result
        except Exception as e:
            print(f"Ошибка при вытягивании данных о группах: {e}.")
            return []

    def select_teachers(self) -> list:
        """Вытягивание данных из таблицы teachers в формате ['teacher1', 'teacher2', ...]"""
        try:
            self.cur.execute(SELECT_TEACHERS)
            rows = self.cur.fetchall()
            result = [row[0] for row in rows]
            return result
        except Exception as e:
            print(f"Ошибка при вытягивании данных о группах: {e}.")
            return []

    def select_body_classroom(self) -> list:
        """Вытягивание данных из таблицы body_classroom в формате ['ГЗ', 'УЛК', ...]"""
        try:
            self.cur.execute(SELECT_BODY_CLASSROOM)
            rows = self.cur.fetchall()
            result = [row[0] for row in rows]
            return result
        except Exception as e:
            print(f"Ошибка при вытягивании данных о группах: {e}.")
            return []

    def select_times(self) -> list:
        """Вытягивание данных из таблицы times в формате ['time1', 'time2', ...]"""
        try:
            self.cur.execute(SELECT_TIMES)
            rows = self.cur.fetchall()
            result = [row[0] for row in rows]
            return result
        except Exception as e:
            print(f"Ошибка при вытягивании данных о времени: {e}.")
            return []

    def select_all_tgsl(self) -> list:
        """Достаем все данные из teacher_subject_group_ls (кроме id) в формате: [[teacher, subject, group, ls], ...]"""
        try:
            self.cur.execute(SELECT_ALL_TGSL)
            rows = self.cur.fetchall()
            result = []
            for row in rows:
                result.append([row[1], row[2], row[3], row[4]])
            return result
        except Exception as e:
            print(f"Ошибка при вытягивании данных о группах: {e}.")
            return []

    def select_all_subjects(self) -> list:
        """Достаем все данные из subjects (кроме id) в формате: [[subject_name, property], ...]"""
        try:
            self.cur.execute(SELECT_ALL_SUBJECTS)
            rows = self.cur.fetchall()
            # print(rows)
            result = []
            for row in rows:
                result.append([row[1], row[2]])
            return result
        except Exception as e:
            print(f"Ошибка при вытягивании данных о группах: {e}.")
            return []

    def select_all_classrooms(self) -> list:
        """Достаем все данные из classrooms (кроме id) в формате: [[number_auditory, property], ...]"""
        try:
            self.cur.execute(SELECT_ALL_CLASSROOMS)
            rows = self.cur.fetchall()
            # print(rows)
            result = []
            for row in rows:
                result.append([row[1], row[2], row[3], row[4]])
            return result
        except Exception as e:
            print(f"Ошибка при вытягивании данных о группах: {e}.")
            return []

    def select_teacher_group_subject_ls(self, name: str) -> dict:
        """Достаем данные из teacher_subject_group_ls в формате: {'teacher': {'subject': {'lesson_type': 'group'}}, ...}"""
        try:
            self.cur.execute(SELECT_TEACHER_GROUP_SUBJECT_LS + f"'{name}';")
            rows = self.cur.fetchall()
            if rows:
                result = {}
                for row in rows:
                    teacher_type = row[1] # препод
                    subject = row[2]  # название предмета
                    lesson_type = row[3]  # тип занятия
                    groups_str = row[4]  # список групп в формате '['Группа1', 'Группа2']'
                    # убираем внешние строки со списка групп
                    try:
                        groups = eval(groups_str) if groups_str != "[]" else []
                    except:
                        groups = []

                    if teacher_type not in result:
                        result[teacher_type] = {}
                    if subject not in result[teacher_type]:
                        result[teacher_type][subject] = {}
                    result[teacher_type][subject][lesson_type] = groups
                return result
            return {}
        except Exception as e:
            print(f"Ошибка при вытягивании данных о tsgl: {e}.")
            return {}

    def select_teacher_time(self, name: str) -> dict:
        """Тянем данные из teacher_time в формате {'Понедельник': {'08:30 - 10:00': 'odd', '11:50 - 13:20': 'even'}, 'Вторник': {'19:15 - 20:45': 'both'}, 'Среда': {}, 'Четверг': {}, 'Пятница': {}, 'Суббота': {}}"""
        try:
            self.cur.execute(SELECT_TEACHER_TIME + f"'{name}';")
            rows = self.cur.fetchall()
            result = {
                "Понедельник": {},
                "Вторник": {},
                "Среда": {},
                "Четверг": {},
                "Пятница": {},
                "Суббота": {}
            }
            if rows:
                for row in rows:
                    day = row[1]  # День недели
                    time_slot = row[2]  # Временной слот
                    if row[3] == True and row[4] == False:
                        cz = "odd"
                    elif row[3] == False and row[4] == True:
                        cz = "even"
                    else:
                        cz = "both"
                    if day in result:
                        result[day][time_slot] = cz
                    else:
                        result[day] = {time_slot: cz}
                return result
            return {}
        except Exception as e:
            print(f"Ошибка при вытягивании данных о teacher_time: {e}.")
            return {}

    def select_lock(self, subject: str) -> dict:
        """Тянем данные из lock_slot по имени в формате {'Понедельник': {'08:30 - 10:00': 'odd', '11:50 - 13:20': 'even'}, 'Вторник': {'19:15 - 20:45': 'both'}, 'Среда': {}, 'Четверг': {}, 'Пятница': {}, 'Суббота': {}}"""
        try:
            self.cur.execute(SELECT_LOCK + f"'{subject}';")
            rows = self.cur.fetchall()
            result = {
                "Понедельник": {},
                "Вторник": {},
                "Среда": {},
                "Четверг": {},
                "Пятница": {},
                "Суббота": {}
            }
            if rows:
                for row in rows:
                    day = row[1]  # День недели
                    time_slot = row[2]  # Временной слот
                    if row[3] == True and row[4] == False:
                        cz = "odd"
                    elif row[3] == False and row[4] == True:
                        cz = "even"
                    else:
                        cz = "both"
                    if day in result:
                        result[day][time_slot] = cz
                    else:
                        result[day] = {time_slot: cz}
                return result
            return {}
        except Exception as e:
            print(f"Ошибка при вытягивании данных о lock_slot: {e}.")
            return {}

    def select_locks(self) -> dict:
        """Тянем данные из lock_slot в формате {'Понедельник': {'08:30 - 10:00': 'odd', '11:50 - 13:20': 'even'}, 'Вторник': {'19:15 - 20:45': 'both'}, 'Среда': {}, 'Четверг': {}, 'Пятница': {}, 'Суббота': {}}"""
        try:
            self.cur.execute(SELECT_LOCKS)
            rows = self.cur.fetchall()
            result_2 = {}

            if rows:
                for row in rows:
                    group = row[0]
                    day = row[1]
                    time_slot = row[2]

                    if row[3] == True and row[4] == False:
                        cz = "odd"
                    elif row[3] == False and row[4] == True:
                        cz = "even"
                    else:
                        cz = "both"
                    if group not in result_2:
                        result_2[group] = {
                            "Понедельник": {},
                            "Вторник": {},
                            "Среда": {},
                            "Четверг": {},
                            "Пятница": {},
                            "Суббота": {}
                        }
                    result_2[group][day][time_slot] = cz

                return result_2
            return {}
        except Exception as e:
            print(f"Ошибка в select_locks: {e}.")
            return {}

    def select_hours(self, subject_name: str, group_name: str) -> list:
        """Из таблицы hours по имени предмета и группы тянем данные в формате [subject_name, group_name, seminars, lectures, labs]"""
        try:
            self.cur.execute(SELECT_HOURS, (subject_name, group_name))
            return self.cur.fetchall()
        except Exception as e:
            print(f"Ошибка при вытягивании данных о hours: {e}")
            return []

    def select_all_hours(self) -> list:
        """Из таблицы hours тянем все данные формате [subject_name, group_name, seminars, lectures, labs]"""
        try:
            self.cur.execute(SELECT_ALL_HOURS)
            return self.cur.fetchall()
        except Exception as e:
            print(f"Ошибка при вытягивании данных из hours: {e}")
            return []

    def drop_tables(self) -> bool:
        """функция удаления таблиц (необходима в процессе разработки для тестов)"""
        try:
            self.cur.execute(DROP_ALL_TABLES)
            # self.cur.execute(DROP_TABLE_TS)
            # self.cur.execute(DROP_TABLE_GS)
            # self.cur.execute(DROP_TABLE_SUBJECTS)
            # self.cur.execute(DROP_TABLE_GROUPS)
            # self.cur.execute(DROP_TABLE_TIMES)
            # self.cur.execute(DROP_TABLE_CLASSROOMS)
            # self.cur.execute(DROP_TABLE_TEACHER_GROUP_SUBJECT_LS)
            # self.cur.execute(DROP_TABLE_TEACHER_TIME)
            # self.cur.execute(DROP_TABLE_PROPERTY)
            self.conn.commit()
            print("Таблицы успешно удалены.")
            return True
        except Exception as e:
            print(f"Ошибка при удалении таблиц: {e}.")
            return False

    def insert_teacher_group_subject_ls(self, data: dict) -> bool:  # функция для заполнения бд из таблицы1 анкеты
        """Функция для заполнения teacher_group_subject_ls по сформированной data с бекенда (вкладка - Анкета)"""
        # data = {"s": {"Сети": {"table_sem": ["ИУ10-11"], "table_lec": ["ИУ10-13"], "table_lab": ["ИУ10-11"]}}} <- из анкеты таблица 1
        body_values = []
        for key_teacher, val_teacher in data.items():
            teacher = key_teacher
            for key_sub, val_sub in val_teacher.items():
                subject = key_sub
                for key_name, val_group in val_sub.items():
                    if key_name == "table_sem":
                        body_values.append((teacher, subject, "семинар", str(val_group).replace("'", '"')))
                    elif key_name == "table_lec":
                        body_values.append((teacher, subject, "лекция", str(val_group).replace("'", '"')))
                    else:  # table_lab
                        body_values.append((teacher, subject, "лаба", str(val_group).replace("'", '"')))
        zapros_insert = '''
        INSERT INTO public.teacher_group_subject_ls (teacher, subject, ls, group_name)
            VALUES '''
        for value in body_values:
            zapros_insert += "\n\t" + str(value) + ", "
        zapros_insert = zapros_insert[:-2] + ";"
        zapros_delete = DELETE_NAMES_FROM_TEACHER_GROUP_SUBJECT_LS + f"'{teacher}' and subject = '{subject}'"
        try:
            self.cur.execute(zapros_delete)  # чистим старые данные в бд
            self.cur.execute(zapros_insert)  # добавляем новые данные в бд
            self.conn.commit()
            print("Данные 'Предмет' добавлены в базу данных")
            return True
        except Exception as e:
            print(f"Ошибка при добавлении данных в таблицу 'Анкета: Таблица1': {e}.")
            return False

    def insert_teacher_time(self, data: dict, teacher: str) -> bool:  # функция для заполнения бд из таблицы2 анкеты
        """Функция для заполнения teacher_time по сформированной data и teacher с бекенда (вкладка - Анкета)"""
        # data = {'Понедельник': {'08:30 - 10:00': 'odd', '11:50 - 13:20': 'even'}, 'Вторник': {'19:15 - 20:45': 'both'}, 'Среда': {}, 'Четверг': {}, 'Пятница': {}, 'Суббота': {}}<- из анкеты таблица 2
        zapros_insert = '''
        INSERT INTO public.teacher_time (teacher, day, time, numerator, denominator)
            VALUES '''
        for day, time_cz in data.items():
            for time, cz in time_cz.items(): # cz - это odd(Чс), even(Зн) или both(Чс и Зн)
                if cz == "odd":
                    zapros_insert += "\n\t" + f"('{teacher}', '{day}', '{time}', true, false),"
                elif cz == "even":
                    zapros_insert += "\n\t" + f"('{teacher}', '{day}', '{time}', false, true),"
                else:
                    zapros_insert += "\n\t" + f"('{teacher}', '{day}', '{time}', true, true),"
        zapros_insert = zapros_insert[:-1] + ";"
        zapros_delete = DELETE_NAMES_FROM_TEACHER_TIME + f"'{teacher}';"
        try:
            self.cur.execute(zapros_delete)  # чистим старые данные в бд
            self.cur.execute(zapros_insert)  # добавляем новые данные в бд
            self.conn.commit()
            print("Данные 'Анкета: Таблица2' добавлены в базу данных")
            return True
        except Exception as e:
            print(f"Ошибка при добавлении данных в таблицу 'Анкета: Таблица2': {e}.")
            return False

    def insert_teacher(self, teacher: str) -> bool:
        """Функция создания преподавателя в списке бд при первичном входе на сайт."""
        try:
            self.cur.execute(INSERT_TEACHER + f'(\'{teacher}\');')
            self.conn.commit()
            return True
        except Exception as e:
            print(f'Ошибка в insert_teacher: {e}')
            return False

    def insert_lock_table(self, data: dict, subject: str) -> bool:
        """функция заполнения lock_slot при заполнении таблицы блокировки слотов (вкладка - Админ Панель)"""
        # data = {'Понедельник': {'08:30 - 10:00': 'odd', '11:50 - 13:20': 'even'}, 'Вторник': {'19:15 - 20:45': 'both'}, 'Среда': {}, 'Четверг': {}, 'Пятница': {}, 'Суббота': {}}<- из анкеты таблица 2
        zapros_insert = '''
        INSERT INTO public.lock_slot (group_name, day, time, numerator, denominator)
            VALUES '''
        for day, time_cz in data.items():
            for time, cz in time_cz.items(): # cz - это odd(Чс), even(Зн) или both(Чс и Зн)
                # print(teacher, day, time , cz)
                if cz == "odd":
                    zapros_insert += "\n\t" + f"('{subject}', '{day}', '{time}', true, false),"
                elif cz == "even":
                    zapros_insert += "\n\t" + f"('{subject}', '{day}', '{time}', false, true),"
                else:
                    zapros_insert += "\n\t" + f"('{subject}', '{day}', '{time}', true, true),"
        zapros_insert = zapros_insert[:-1] + ";"
        zapros_delete = DELETE_SUBJECT_FROM_LOCK_SLOT + f"'{subject}';"
        try:
            self.cur.execute(zapros_delete)  # чистим старые данные в бд
            self.cur.execute(zapros_insert)  # добавляем новые данные в бд
            self.conn.commit()
            print(f"Данные по блокировке слота {subject} добавлены")
            return True
        except Exception as e:
            print(f"Ошибка при добавлении данных в таблицу 'lock_slot': {e}.")
            return False


    def insert_classroom(self, name: str, capacity: int, property: str, body: str) -> bool:
        """функция заполнения classrooms при заполнении таблицы аудиторий с их номером, вместимостью, свойством и расположением (вкладка - Админ Панель)"""
        try:
            query = f"insert into classrooms values ('{name}', {capacity}, '{property}', '{body}')"
            self.cur.execute(query)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Ощибка при добавлении новой аудитории {name}: {e}")
            return False

    def insert_hours(self, one: tuple) -> bool:
        """Функция для заполнения таблицы hours - соотношение у групп их предметов с кол-ом пар за 2 недели (вкладка - Админ Панель)"""
        try:
            query = "insert into hours(subject_name, group_name, seminars, lectures, labs) values " + "\n\t" + str(one) + ";"
            self.cur.execute(query)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении данных в hours: {e}")
            return False

    def insert_tables(self) -> bool:
        """Заполнение таблиц статичными данными по типу номеров аудиторий"""
        try:
            # self.cur.execute(INSERT_TS)
            # self.cur.execute(INSERT_GS)
            self.cur.execute(INSERT_TEACHERS)
            self.cur.execute(INSERT_GROUPS)
            self.cur.execute(INSERT_SUBJECTS)
            self.cur.execute(INSERT_TIMES)
            self.cur.execute(INSERT_CLASSROOM)
            self.cur.execute(INSERT_PROPERTY)
            self.cur.execute(INSERT_BODY_CLASSROOM_TABLE)
            self.cur.execute(INSERT_HOURS)
            self.conn.commit()
            print("Данные в таблицы успешно добавлены.")
            return True
        except Exception as e:
            print(f"Ошибка при добавлении данных в таблицы: {e}.")
            return False

    def insert_tablename_value(self, table: str, name: str) -> bool:
        """Функция заполнения таблиц с колонкой name"""
        try:
            query = f"insert into {table}(name) values ('{name}')"
            self.cur.execute(query)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении данных в teachers: {e}.")
            return False

    def insert_group(self, name: str, count: int) -> bool:
        """Функция заполнения таблицы groups"""
        try:
            query = f"insert into groups(name, count) values ('{name}', {count})"
            self.cur.execute(query)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении через админку данных о group: {e}.")
            return False

    def insert_subject(self, name: str, property: str) -> bool:
        """Функция заполнения таблицы subjects"""
        try:
            self.cur.execute(f"insert into subjects(name, property) values ('{name}', '{property}');")
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении через админку данных о subject: {e}.")
            return False

    def insert_classroom(self, name: str, capacity: int, property: str, body: str) -> bool:
        """Функция заполнения таблицы classroms"""
        try:
            self.cur.execute(f"insert into classrooms(name, capacity, property, body) values ('{name}', '{capacity}', '{property}', '{body}');")
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении через админку данных о classroom: {e}.")
            return False

    def insert_tgsl(self, teacher: str, subject: str, ls: str, group: str) -> bool:
        """Функция заполнения таблицы teacher_group_subject_ls"""
        try:
            self.cur.execute(INSERT_TGSL + f"('{teacher}', '{subject}', '{ls}', '{group}');")
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при заполнении tgsl: {e}")
            return False
    
    def insert_linking(self, subject: str, type_subject: str, teachers: list, groups: list) -> None:
        """Функция заполнения таблицы linking"""
        try:
            flag_for_id_para = False # для: если было хотя бы одно обновление max_id_para, то не меняй max_id_para
            self.linking_edit_id_para() # Делает так, что минимальный id_para всегда 1. Тк в процессе редактирования эти id перезаписываются и в процессе выглядят некрасиво
            for teacher in teachers:
                for group in groups:
                    # if not self.check_linking(subject, type_subject, teacher, group):
                    self.cur.execute(SELECT_LINKING_MAX_ID_PARA)
                    max_id_para = self.cur.fetchall()[0][0] # [(None,)] or [(1,)] -> None or 1
                    if flag_for_id_para:
                        pass
                    elif max_id_para:
                        max_id_para = max_id_para + 1
                        flag_for_id_para = True
                    else:
                        max_id_para = 1
                        flag_for_id_para = True
                    self.cur.execute(INSERT_LINKING + f'(\'{subject}\', \'{type_subject}\', \'{teacher}\', \'{group}\', {max_id_para});\n')
            self.conn.commit()
        except Exception as e:
            print(f'Ошибка в insert_linking: {e}')
    
    def linking_edit_id_para(self) -> None:
        """Функция, чтобы id_para всегда начинался с 1. Тк если записи хотя бы две и редактировать 
        с мин id_para, то в последствии он мин id_para превр в max id_para + 1. 
        Попробуйте закомментировать в вызываемом коде и посмотреть как работает"""
        try:
            self.cur.execute("""
                WITH mapping AS (
                SELECT
                    old_id_para,
                    DENSE_RANK() OVER (ORDER BY old_id_para) AS new_id_para
                FROM (
                    SELECT DISTINCT id_para AS old_id_para
                    FROM linking
                ) d
                )
                UPDATE linking AS l
                SET id_para = m.new_id_para
                FROM mapping AS m
                WHERE l.id_para = m.old_id_para
                AND l.id_para <> m.new_id_para;
                """)
            # self.cur.execute("""
            #     WITH ids AS (
            #     SELECT DISTINCT id_para
            #     FROM linking
            #     ),
            #     mapping AS (
            #     SELECT
            #         id_para AS old_id_para,
            #         ROW_NUMBER() OVER (ORDER BY id_para) AS new_id_para
            #     FROM ids
            #     )
            #     UPDATE linking l
            #     SET id_para = m.new_id_para
            #     FROM mapping m
            #     WHERE l.id_para = m.old_id_para
            #     AND l.id_para <> m.new_id_para;
            #     """)
            self.conn.commit()
        except Exception as e:
            print(f'Ошибка в linking_edit_id_para: {e}')
    
    def update_linking(self, subject_old: str, type_subject_old: str, subject_new: str, type_subject_new: str, teachers: list, groups: list, id_para: int) -> None:
        """Обновить связку: заменить старый subject/type_subject на новый + обновить преподавателей и группы"""
        try:
            self.cur.execute(
                "DELETE FROM linking WHERE subject = %s AND type_subj = %s AND id_para = %s;",
                (subject_old, type_subject_old, id_para)
            )

            self.insert_linking(subject_new, type_subject_new, teachers, groups)
            # for teacher in teachers:
            #     for group in groups:
            #         self.cur.execute(SELECT_LINKING_ID_PARA)
            #         max_id_para = self.cur.fetchall()
            #         if max_id_para:
            #             max_id_para = max_id_para[0] + 1
            #         else:
            #             max_id_para = 1
            #         self.cur.execute(
            #             INSERT_LINKING + " (%s, %s, %s, %s, %s);",
            #             (subject_new, type_subject_new, teacher, group, max_id_para)
            #         )
            # 
            # self.conn.commit()
        except Exception as e:
            print(f"Ошибка в update_linking: {e}")

    def check_one_column(self, table: str, column: str, value: str) -> bool:
        """Универсальная функция проверки таблицы бд по столбцу и значению"""
        try:
            self.cur.execute(f'SELECT * FROM {table} where {column}=\'{next(iter(value))}\';')
            result = self.cur.fetchall()
            if len(result) != 0:
                return True
            return False
        except Exception as e:
            print(f'Ошибка в check_one_column: {e}')
            return False

    def check_linking(self, subject: str, type_subject: str, teacher: str, group: str) -> bool:
        """Функция для проверки наличия записи в linking (для недопущения дубликатов)"""
        try:
            self.cur.execute(CHECK_LINKING + f'\'{subject}\' AND type_subj=\'{type_subject}\' AND teacher=\'{teacher}\' AND group_name=\'{group}\';')
            rows = self.cur.fetchall()
            if len(rows) != 0:
                return True
            return False
        except Exception as e:
            print(f'Ошибка в check_linking: {e}')
            return False


    def select_linking(self) -> list:
        """Функция для вытягивания всех данных из linking"""
        try:
            self.cur.execute(SELECT_LINKING)
            result = self.cur.fetchall()
            return result
        except Exception as e:
            print(f'Ошибка в select_linking: {e}')
            return []
    
    def delete_linking_stroke(self, subject: str, type_subject: str, id_para: int) -> None:
        """Функция для удаления строки из linking по предмету и его типу"""
        try:
            self.cur.execute(DELETE_LINKING_STROKE + f'\'{subject}\' AND type_subj=\'{type_subject}\' AND id_para={id_para};')
            self.conn.commit()
        except Exception as e:
            print(f'Ошибка в delete_linking_stroke: {e}')

    def delete_from_teacher(self, name: str) -> bool:
        """Функция удаления преподавателя из таблицы teachers"""
        try:
            query = f"delete from teachers where name='{name}'"
            self.cur.execute(query)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при удалении данных в teachers: {e}.")
            return False

    def delete_from_tgsl(self, name: str) -> bool:
        """Функция удаления данных из teacher_group_subject_ls по имени преподавателя"""
        try:
            query = f"delete from teacher_group_subject_ls where teacher='{name}'"
            self.cur.execute(query)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при удалении данных в teacher_group_subject_ls: {e}.")
            return False


    def delete_from_teacher_time(self, name: str) -> bool:
        """Функция удаления данных из teacher_time по имени преподавателя"""
        try:
            query = f"delete from teacher_time where teacher='{name}'"
            self.cur.execute(query)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при удалении данных в teacher_time: {e}.")
            return False
    
    def delete_from_table(self, table: str, column: str, value: str) -> None:
        """Универсальная функция удаления из бд по столбцу и значению"""
        try:
            query = f"delete from {table} where {column}='{next(iter(value))}'"
            self.cur.execute(query)
            self.conn.commit()
        except Exception as e:
            print(f"Ошибка в delete_from_table: {e}.")

    def delete_from_table_name(self, table: str, name: str) -> bool:
        """Функция удаления данных из таблиц с колонкой name"""
        try:
            query = f"delete from {table} where name='{name}'"
            self.cur.execute(query)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при удалении данных в {table} where name={name}: {e}.")
            return False

    def delete_from_hours_s_name(self, name: str) -> bool:
        """Функция удаления данных из hours по названию предмета"""
        try:
            query = f"delete from hours where subject_name='{name}'"
            self.cur.execute(query)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при удалении данных в hours where subject_name={name}: {e}.")
            return False

    def delete_from_table_g_name(self, table: str, name: str) -> bool:
        """Функция удаления данных из таблицы с колонкой group_name"""
        try:
            query = f"delete from {table} where group_name='{name}'"
            self.cur.execute(query)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при удалении данных в {table} where group_name={name}: {e}.")
            return False

    def delete_from_hours_s_g_name(self, subject: str, group: str) -> bool:
        """Функция удаления данных из hours по group_name и subject_name"""
        try:
            query = f"delete from hours where group_name='{group}' and subject_name='{subject}'"
            self.cur.execute(query)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при удалении данных в hours where group_name={group} and subject_name={subject}: {e}.")
            return False

    def delete_subject_tgsl(self, subject: str) -> bool:
        """Функция удаления данных из teacher_group_subject_ls по названию предмета"""
        try:
            query = f"delete from teacher_group_subject_ls where subject='{subject}'"
            self.cur.execute(query)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при удалении данных в teacher_group_subject_ls where subject='{subject}': {e}.")
            return False

    def delete_table(self, table: str) -> bool:
        """Функция удаления данных из таблицы (FIXME сделать update)"""
        try:
            DELETE_TABLE = "delete from " + f"{table};"
            self.cur.execute(DELETE_TABLE)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при удалении таблицы {table}: {e}")
            return False

    def check_tgsl_tt_name(self, table: str, name: str) -> bool:
        """Функция проверки преподавателя в таблице table"""
        try:
            query = f"SELECT * FROM {table} WHERE teacher = '{name}';"
            self.cur.execute(query)
            rows = self.cur.fetchall()
            if len(rows) != 0:
                return True
            return False
        except Exception as e:
            print(f"Ошибка при проверки строк в {table}: {e}.")
            return False

    def check_hours_subject_group(self, subject_name: str, group_name: str) -> bool:
        """Функция проверки записи в hours по subject_name и group_name"""
        try:
            query = f"SELECT * FROM hours WHERE subject_name = '{subject_name}' and group_name = '{group_name}';"
            self.cur.execute(query)
            rows = self.cur.fetchall()
            if len(rows) != 0:
                return True
            return False
        except Exception as e:
            print(f"Ошибка при проверке строк в hours: {e}.")
            return False

    def check_table_name(self, table: str, name: str) -> bool:
        """Функция проверки наличия name в таблице table"""
        try:
            query = f"SELECT * FROM {table} WHERE name = '{name}';"
            self.cur.execute(query)
            rows = self.cur.fetchall()
            if len(rows) != 0:
                return True
            return False

        except Exception as e:
            print(f"Ошибка при проверке строк в {table}: {e}.")
            return False

    def select_filtered_table(self, subject: str, group: str) -> list:
        """Функция для фильтрованного вывода всех данных в hours (вкладка - Админ Панель)"""
        try:
            query = "SELECT subject_name, group_name, seminars, lectures, labs FROM hours WHERE 1=1"
            params = []
            if subject:
                query += " AND subject_name = %s"
                params.append(subject)

            if group:
                query += " AND group_name = %s"
                params.append(group)
            self.cur.execute(query, params)
            return self.cur.fetchall()
        except Exception as e:
            print(f"Ошибка в select_filtered_table: {e}")
            return []

def main():
    connect = Connect()
    _con, _cur = connect.conn, connect.cur
    # connect.create_tables()
    # connect.drop_tables()
    # connect.create_tables()
    # connect.insert_tables()

if __name__ == "__main__":
    main()
