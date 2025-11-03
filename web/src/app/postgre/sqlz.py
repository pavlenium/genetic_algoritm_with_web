CREATE_TEACHERS_TABLE = """
CREATE TABLE IF NOT EXISTS teachers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);
"""

CREATE_BODY_CLASSROOM_TABLE = """
CREATE TABLE IF NOT EXISTS body_classroom (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);
"""

CREATE_LINKING_TABLE = """
CREATE TABLE IF NOT EXISTS linking (
    id SERIAL PRIMARY KEY,
    subject VARCHAR(255) NOT NULL,
    type_subj VARCHAR(255) NOT NULL,
    teacher VARCHAR(255) NOT NULL,
    group_name VARCHAR(255) NOT NULL,
    id_para int4 not null
);
"""

SELECT_LINKING_MAX_ID_PARA = """
SELECT max(id_para) from linking;
"""

INSERT_LINKING = """
INSERT INTO linking (subject, type_subj, teacher, group_name, id_para)
values
	
"""

CHECK_LINKING = """
select * from linking
where subject=
"""

SELECT_LINKING = """
select subject, type_subj, teacher, group_name, id_para from linking;
"""

DELETE_LINKING_STROKE = """
DELETE FROM linking
where subject=
"""

CREATE_HOURS_TABLE = """
create table if not exists hours (
	id serial primary key,
	subject_name text not null,
	group_name text not null,
	seminars int4 not null,
	lectures int4 not null,
	labs int4 not null
)
"""

CREATE_LOCK_SLOT_TABLE = """
create table if not exists lock_slot (
    id serial primary key,
    group_name text not null,
    day text not null,
    time text not null,
    numerator BOOLEAN not null,
    denominator BOOLEAN not null
)
"""

INSERT_BODY_CLASSROOM_TABLE = """
INSERT INTO body_classroom (name)
values
    ('body_classroom1'),
    ('body_classroom2'),
    ('body_classroom3'),
    ('body_classroom4'),
    ('body_classroom5'),
    ('body_classroom6')
"""

SELECT_BODY_CLASSROOM = """
select name from body_classroom ;
"""

CREATE_GROUPS_TABLE = """
CREATE TABLE IF NOT EXISTS groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    count int4 NOT NULL
);
"""

CREATE_TEACHER_GROUP_SUBJECT_LS_TABLE = """
create table if not exists teacher_group_subject_ls (
	id SERIAL PRIMARY KEY,
	teacher text not null,
	subject text not null,
	ls text not null,
	group_name text not null
);
"""

CREATE_TEACHER_TIME_TABLE = """
CREATE TABLE IF NOT EXISTS teacher_time (
    id SERIAL PRIMARY KEY,
    teacher VARCHAR(255) NOT null,
    day text not null,
    time text not null,
    numerator BOOLEAN not null,
    denominator BOOLEAN not null
);
"""

KIRILL_SQL = """
CREATE OR REPLACE FUNCTION select_configuration(
    OUT cur_hours REFCURSOR,
    OUT cur_lock_slot REFCURSOR,
    OUT cur_teacher_time REFCURSOR,
    out cur_body_classroom REFCURSOR,
    out cur_classrooms REFCURSOR,
    out cur_groups  REFCURSOR,
    out cur_property REFCURSOR,
    out cur_subjects REFCURSOR,
    out cur_tgsl REFCURSOR,
    out cur_teachers REFCURSOR,
    out cur_times REFCURSOR,
    out cur_schedule_data REFCURSOR
) AS $$
BEGIN
    cur_hours := 'cursor_hours';
    cur_lock_slot := 'cursor_lock_slot';
    cur_teacher_time := 'cursor_teacher_time';
  cur_body_classroom := 'cursor_body_classroom';
    cur_classrooms := 'cursor_classrooms';
    cur_groups := 'cursor_groups';
    cur_property := 'cursor_property';
    cur_subjects := 'cursor_subjects';
    cur_tgsl := 'cursor_tgsl';
    cur_teachers := 'cursor_teachers';
    cur_times := 'cursor_times';
    cur_schedule_data := 'cursor_schedule_data';
    

  OPEN cur_hours FOR SELECT * FROM hours;
  OPEN cur_lock_slot FOR SELECT * FROM lock_slot;
  OPEN cur_teacher_time FOR SELECT * FROM teacher_time;

  OPEN cur_body_classroom FOR SELECT * FROM body_classroom;  
  OPEN cur_classrooms FOR SELECT  id FROM classrooms;  
  OPEN cur_groups FOR SELECT  name FROM groups ORDER BY id;
  OPEN cur_property FOR SELECT * FROM property;  
  OPEN cur_subjects FOR SELECT id, name FROM subjects;  
  OPEN cur_tgsl FOR select * from view_tgls_with_hours where group_name is not null and (seminars  is not null or lectures  is not null or labs  is not null ); 
  OPEN cur_teachers FOR SELECT id, name FROM teachers;  
  OPEN cur_times FOR SELECT name FROM times ORDER BY id;  
  OPEN cur_schedule_data FOR SELECT  teacher, subject, ls, group_name FROM teacher_group_subject_ls;

    RETURN;
END;
$$ LANGUAGE plpgsql;
"""

CREATE_SUBJECTS_TABLE = """
CREATE TABLE IF NOT EXISTS subjects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    property VARCHAR(255) NOT NULL
);
"""

CREATE_TIMES_TABLE = """
CREATE TABLE IF NOT EXISTS times (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);
"""

CREATE_CLASSROOMS_TABLE = """
CREATE TABLE IF NOT EXISTS classrooms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    capacity int4 NOT NULL,
    property VARCHAR(255) NOT NULL,
    body VARCHAR(255) NOT NULL
);
"""

CREATE_GS = """
CREATE TABLE IF NOT EXISTS public.group_to_subject (
    group_id int4 NOT NULL,
    subject_id int4 NOT NULL
);
"""

CREATE_TS = """
CREATE TABLE IF NOT EXISTS public.teacher_to_subject (
    teacher_id int4 NOT NULL,
    subject_id int4 NOT NULL
);
"""

CREATE_TABLE_PROPERTY = """
CREATE TABLE IF NOT EXISTS property (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);
"""
INSERT_PROPERTY = """
insert into property(name)
values
	('dashboard'),
	('computer_linux'),
	('proektor'),
	('computer_windows'),
	('wi-fi'),
	('apples'),
	('banana');
"""
SELECT_PROPERTY = """
select name from property;
"""

DROP_TABLE_PROPERTY = """
drop table property;
"""

INSERT_TEACHER = """
insert into public.teachers(name)
	values 
"""

GROUP_TO_SUBJECT = """
select g.name, s.name, gs.hours
from groups g
join group_to_subject gs on gs.group_id = g.id
join subjects s on gs.subject_id = s.id;
"""

TEACHER_TO_SUBJECT = """
select t.name, s.name
from teachers t
join teacher_to_subject ts on ts.teacher_id = t.id
join subjects s on ts.subject_id = s.id;
"""

SELECT_GROUPS = """
select name, count from groups
order by name;
"""

SELECT_HOURS = """
select subject_name, group_name, seminars, lectures, labs from hours
where subject_name = %s and group_name = %s;
"""

SELECT_ALL_HOURS = """
select subject_name, group_name, seminars, lectures, labs from hours;
"""

SELECT_CLASSROOMS = """
select name, capacity, property, body from classrooms;
"""

SELECT_TEACHER_GROUP_SUBJECT_LS = """
select * from teacher_group_subject_ls tgsl
where teacher =
"""

SELECT_TEACHER_TIME = """
select teacher, day, time, numerator, denominator from teacher_time
where teacher =
"""

SELECT_LOCK = """
select group_name, day, time, numerator, denominator from lock_slot
where group_name =
"""

TEST_TABLE = """
create table if not exists test_table (
	id serial primary key,
	subject_name text not null,
	group_name text not null,
	numerator BOOLEAN not null,
	denominator BOOLEAN not null,
	seminars int4 not null,
	lectures int4 not null,
	labs int4 not null
)
"""


SELECT_LOCKS = """
select group_name, day, time, numerator, denominator from lock_slot;
"""

SELECT_SUBJECTS_DICT = """
select name, property from subjects;
"""

SELECT_SUBJECTS = """
select name, property from subjects
order by name;
"""

SELECT_TEACHERS = """
select name from teachers
order by name;
"""

SELECT_TIMES = """
select name from times;
"""

INSERT_TEACHERS = """
insert into teachers (name)
values
  ('teacher1'),
  ('teacher2'),
  ('teacher3'),
  ('teacher4'),
  ('teacher5'),
  ('teacher6'),
  ('teacher7'),
  ('teacher8'),
  ('teacher9'),
  ('teacher10');
"""

INSERT_GROUPS = """
INSERT INTO groups (name, count)
VALUES
  ('ИУ10-11', 15),
  ('ИУ10-12', 20),
  ('ИУ10-13', 12),
  ('ИУ10-14', 18),
  ('ИУ10-15', 22),
  ('ИУ10-16', 14),
  ('ИУ10-17', 19),
  ('ИУ10-18', 16),
  ('ИУ10-19', 21),
  ('ИУ10-31', 13),
  ('ИУ10-32', 17),
  ('ИУ10-33', 24),
  ('ИУ10-34', 15),
  ('ИУ10-35', 20),
  ('ИУ10-36', 12),
  ('ИУ10-37', 18),
  ('ИУ10-38', 22),
  ('ИУ10-39', 14),
  ('ИУ10-51', 19),
  ('ИУ10-52', 16),
  ('ИУ10-53', 21),
  ('ИУ10-54', 13),
  ('ИУ10-55', 17),
  ('ИУ10-56', 24),
  ('ИУ10-57', 15),
  ('ИУ10-58', 20),
  ('ИУ10-59', 12),
  ('ИУ10-71', 18),
  ('ИУ10-72', 22),
  ('ИУ10-73', 14),
  ('ИУ10-74', 19),
  ('ИУ10-75', 16),
  ('ИУ10-76', 21),
  ('ИУ10-77', 13),
  ('ИУ10-78', 17),
  ('ИУ10-79', 24),
  ('ИУ10-91', 15),
  ('ИУ10-92', 20),
  ('ИУ10-93', 12),
  ('ИУ10-94', 18),
  ('ИУ10-95', 22),
  ('ИУ10-96', 14),
  ('ИУ10-97', 19),
  ('ИУ10-98', 16),
  ('ИУ10-99', 21),
  ('ИУ10-111', 13),
  ('ИУ10-112', 17),
  ('ИУ10-113', 24),
  ('ИУ10-114', 15),
  ('ИУ10-115', 20),
  ('ИУ10-116', 12),
  ('ИУ10-117', 18),
  ('ИУ10-118', 22),
  ('ИУ10-119', 14);
"""

INSERT_SUBJECTS = """
insert into subjects (name, property)
values
  ('subject1', '["computer_linux", "apples"]'),
  ('subject2', '["computer_windows", "banana"]'),
  ('subject3', '["computer_windows", "banana"]'),
  ('subject4', '["wi-fi"]'),
  ('subject5', '["dashboard", "banana"]'),
  ('subject6', '["computer_windows", "apples", "wi-fi"]'),
  ('subject7', '["computer_windows", "banana"]'),
  ('subject8', '["computer_windows", "dashboard", "banana", "wi-fi"]'),
  ('subject9', '["proektor", "banana"]'),
  ('subject10', '["computer_linux", "proektor", "wi-fi"]'),
  ('subject11', '["dashboard", "proektor", "wi-fi"]'),
  ('subject12', '["computer_windows", "dashboard", "banana", "wi-fi"]'),
  ('subject13', '[]'),
  ('subject14', '["computer_windows", "computer_linux"]'),
  ('subject15', '["computer_linux"]'),
  ('subject16', '["computer_windows", "banana", "wi-fi"]'),
  ('subject17', '[]'),
  ('subject18', '[]'),
  ('subject19', '["dashboard"]'),
  ('subject20', '[]'),
  ('subject21', '["dashboard", "proektor"]'),
  ('subject22', '["computer_windows", "banana"]'),
  ('subject23', '["computer_windows", "banana"]'),
  ('subject24', '["computer_windows", "banana"]'),
  ('subject25', '["proektor", "banana"]'),
  ('subject26', '["computer_windows", "banana"]'),
  ('subject27', '["proektor", "banana"]'),
  ('subject28', '["computer_windows", "banana", "wi-fi"]'),
  ('subject29', '["computer_windows", "banana"]'),
  ('subject30', '["computer_windows", "banana"]'),
  ('subject31', '["computer_windows", "banana"]'),
  ('subject32', '["proektor", "banana"]'),
  ('subject33', '["computer_windows", "banana"]');
"""

INSERT_HOURS = """
insert into hours(subject_name, group_name, seminars, lectures, labs)
values 
	('subject1', 'ИУ10-11', 0, 2, 1),
	('subject1', 'ИУ10-12', 0, 2, 1),
	('subject1', 'ИУ10-13', 0, 2, 1),
	('subject1', 'ИУ10-14', 0, 2, 1),
	('subject1', 'ИУ10-15', 0, 2, 1),
	('subject1', 'ИУ10-16', 0, 2, 1),
	('subject1', 'ИУ10-17', 0, 2, 1),
	('subject1', 'ИУ10-18', 0, 2, 1),
	('subject1', 'ИУ10-19', 0, 2, 1),
	('subject2', 'ИУ10-11', 0, 2, 0),
	('subject2', 'ИУ10-12', 0, 2, 0),
	('subject2', 'ИУ10-13', 0, 2, 0),
	('subject2', 'ИУ10-14', 0, 2, 0),
	('subject2', 'ИУ10-15', 0, 2, 0),
	('subject2', 'ИУ10-16', 0, 2, 0),
	('subject2', 'ИУ10-17', 0, 2, 0),
	('subject2', 'ИУ10-18', 0, 2, 0),
	('subject2', 'ИУ10-19', 0, 2, 0),
	('subject3', 'ИУ10-111', 0, 2, 1),
	('subject3', 'ИУ10-112', 0, 2, 1),
	('subject3', 'ИУ10-113', 0, 2, 1),
	('subject3', 'ИУ10-114', 0, 2, 1),
	('subject3', 'ИУ10-115', 0, 2, 1),
	('subject3', 'ИУ10-116', 0, 2, 1),
	('subject3', 'ИУ10-117', 0, 2, 1),
	('subject3', 'ИУ10-118', 0, 2, 1),
	('subject3', 'ИУ10-119', 0, 2, 1);
"""

INSERT_TIMES = """
insert into times (name)
values
  ('08:30 - 10:00'),
  ('10:10 - 11:40'),
  ('11:50 - 13:20'),
  ('14:05 - 15:35'),
  ('15:55 - 17:25'),
  ('17:35 - 19:05'),
  ('19:15 - 20:45');
"""

INSERT_CLASSROOM = """
insert into classrooms (name, capacity, property, body)
values
  ('classroom1', 25, '["computer_windows", "dashboard", "banana", "wi-fi"]', 'ГЗ'),
  ('classroom2', 30, '["apples", "dashboard", "computer_linux", "wi-fi"]', 'ГЗ'),
  ('classroom3', 20, '["banana", "wi-fi"]', 'Т'),
  ('classroom4', 60, '["computer_windows", "proektor", "banana", "apples"]', 'ГЗ'),
  ('classroom5', 18, '["computer_windows", "wi-fi"]', 'В4к'),
  ('classroom6', 100, '["computer_windows", "dashboard", "computer_linux", "apples"]', 'В4к'),
  ('classroom7', 15, '["computer_linux"]', 'В4к'),
  ('classroom8', 10, '["dashboard", "banana", "proektor"]', 'В4к');
"""

INSERT_GS = """
INSERT INTO public.group_to_subject
(group_id, subject_id)
VALUES
  (1, 1),
  (1, 2),
  (1, 3),
  (1, 4),
  (2, 5),
  (2, 6),
  (2, 7),
  (3, 8),
  (3, 9),
  (4, 3),
  (5, 6),
  (6, 2),
  (7, 5),
  (8, 3),
  (9, 7),
  (9, 1);
"""

INSERT_TS = """
INSERT INTO public.teacher_to_subject
(teacher_id, subject_id)
VALUES
  (1, 4),
  (2, 1),
  (3, 3),
  (4, 7),
  (5, 4),
  (6, 2),
  (7, 8),
  (8, 9),
  (9, 4),
  (10, 6),
  (11, 5),
  (12, 4),
  (13, 3),
  (14, 5);
"""

INSERT_TGSL = """
insert into teacher_group_subject_ls (teacher, subject, ls, group_name) values
"""

DELETE_NAMES_FROM_TEACHER_TIME = """
delete from teacher_time
where teacher =
"""

DELETE_SUBJECT_FROM_LOCK_SLOT = """
delete from lock_slot
where group_name =
"""

DELETE_NAMES_FROM_TEACHER_GROUP_SUBJECT_LS = """
delete from teacher_group_subject_ls
where teacher =
"""

SELECT_TABLE_NAME = """
select * from %s
where name=%s;
"""

DELETE_TGSL_NAME = f"delete from teacher_subject_group_ls where name="

DELETE_TEACHER_TIME_NAME = f"delete from teacher_time where name="

SELECT_ALL_TGSL = """
select * from teacher_group_subject_ls;
"""

SELECT_ALL_SUBJECTS = """
select * from subjects;
"""

SELECT_ALL_CLASSROOMS = """
select * from classrooms;
"""

DELETE_TABLE = """
delete from
"""

DROP_ALL_TABLES = """
DO $$
DECLARE
    table_record RECORD;
    drop_query TEXT;
BEGIN
    FOR table_record IN
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = current_schema()  -- удаляем только из текущей схемы
    LOOP
        drop_query := 'DROP TABLE IF EXISTS ' || table_record.tablename || ' CASCADE;';
        EXECUTE drop_query;
    END LOOP;

    RAISE NOTICE 'Все таблицы в схеме % удалены.', current_schema();
END $$;
"""
