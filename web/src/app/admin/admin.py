import os
import re
import requests
from app import config
from app.postgre.connect import Connect
from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from app.admin.download_excel import download_excel_schedule
from app.admin.transform_schedule_data import transform_schedule
from app.admin.transform_linking import transform_linkings

admin_router = Blueprint("admin", __name__)


@admin_router.route("/", methods=["POST", "GET"])
def admin_pas():
    user = session.get("user")
    if request.method == "POST":
        passw = request.form.get("password")
        if passw == "s" or session.get("adm"): #FIXME поменять пароль или в целом затереть возможность захода всем кроме состоящих в одной из групп
            session["adm"] = True
            return redirect("/admin/choice")
        else:
            return render_template("admin_pas.html", error=True)
    if session.get("adm"):
        return redirect("/admin/choice")
    else:
        return render_template("admin_pas.html", user=user)


@admin_router.route("/choice", methods=["POST", "GET"])
def choice():
    connect = Connect()
    peoples = connect.select_teachers()
    linking_remember=False
    active_tab = request.args.get("active_tab") or request.form.get("active_tab", "teachers-tab")
    flag_hours = False
    if request.method == "POST":
        active_tab = request.form.get("active_tab", "teachers-tab")
        people = request.form.get("peoples")
        if "val_teacher" in request.form and people:
            session["selected_teacher"] = people
            return redirect("/admin/settings")

        action = request.form.get("action")
        if action == "add_teacher":
            name = request.form.get("teacher_name")
            if not connect.check_table_name("teachers", name):
                connect.insert_tablename_value("teachers", name)
                flash("Преподаватель добавлен", "success")
            return redirect("/admin/choice")

        elif action == "delete_teacher":
            name = request.form.get("teacher_name")
            # print(f'\n\n\n\n\nNAME:{name}')
            if connect.check_table_name("teachers", name):
                connect.delete_from_teacher(name)
                if connect.check_tgsl_tt_name("teacher_group_subject_ls", name):
                    connect.delete_from_tgsl(name)
                if connect.check_tgsl_tt_name("teacher_time", name):
                    connect.delete_from_teacher_time(name)
                if connect.check_one_column("linking", "teacher", {name}):
                    # name = next(iter(name))
                    # print(f'\n\n\n\n\nNAME:{name}')
                    connect.delete_from_table("linking", "teacher", {name})
                flash("Преподаватель удален", "success")
            return redirect("/admin/choice")

        elif action == "add_group":
            name = str(request.form.get("group_name"))
            count = int(request.form.get("group_count"))
            name = "ИУ10-" + name
            if not connect.check_table_name("groups", name):
                connect.insert_group(name, count)

        elif action == "delete_group":
            name = request.form.get("group_name")
            # name =name
            if connect.check_table_name("groups", name):
                connect.delete_from_table_name("groups", name)
                connect.delete_from_table_g_name("hours", name)
                connect.delete_from_table_g_name("lock_slot", name)
                if connect.check_one_column("linking", "group_name", {name}):
                    # name = next(iter(name))
                    # print(f'\n\n\n\n\nNAME:{name}')
                    connect.delete_from_table("linking", "group_name", {name})
                # FOR TGSL
                all_tgsl = connect.select_all_tgsl()  # [['Антонова', 'Языки программирования', 'семинар', '["ИУ10-11", "ИУ10-12", "ИУ10-13"]'], ['Антонова', 'Языки программирования', 'лекция', '[]'], ['Антонова', 'Языки программирования', 'лаба', '[]']]
                for el in all_tgsl:
                    el[3] = el[3].replace(f', "{name}"', "")
                    el[3] = el[3].replace(f'"{name}", ', "")
                    el[3] = el[3].replace(f'"{name}"', "")
                connect.delete_table("teacher_group_subject_ls")
                for el in all_tgsl:
                    connect.insert_tgsl(el[0], el[1], el[2], el[3])

        elif action == "add_property":
            name = request.form.get("property_name")
            if not connect.check_table_name("property", name):
                connect.insert_tablename_value("property", name)
                flash("Свойство добавлено", "success")

        elif action == "delete_property":
            name = request.form.get("property_name")
            if connect.check_table_name("property", name):
                # print(name)
                connect.delete_from_table_name("property", name)
                # FOR SUBJECTS
                subjects = connect.select_all_subjects()  # [['Языки программирования', '["computer_linux", "apples"]']]
                for el in subjects:
                    el[1] = el[1].replace(f', "{name}"', "")
                    el[1] = el[1].replace(f'"{name}", ', "")
                    el[1] = el[1].replace(f'"{name}"', "")
                connect.delete_table("subjects")
                for el in subjects:
                    connect.insert_subject(el[0], el[1])
                # FOR CLASSROOMS
                classrooms = connect.select_all_classrooms()  # [['Языки программирования', '["computer_linux", "apples"]']]
                # print(classrooms)
                for el in classrooms:
                    el[2] = el[2].replace(f', "{name}"', "")
                    el[2] = el[2].replace(f'"{name}", ', "")
                    el[2] = el[2].replace(f'"{name}"', "")
                # print(classrooms)
                connect.delete_table("classrooms")
                for el in classrooms:
                    connect.insert_classroom(el[0], el[1], el[2], el[3])

        elif action == "add_classroom":
            room_num = request.form.get("classroom_name")
            capacity = request.form.get("classroom_capacity")
            properties = str(request.form.getlist("classroom_properties")).replace("'", '"')
            room_body = request.form.get("classroom_body")
            room = ""
            if room_body in ("ГЗ", "В7"):
                room = str(room_num)
            elif room_body == "В4к":
                room = str(room_num) + "к"
            elif room_body == "Хим. Лаб.":
                room = str(room_num) + "х"
            elif room_body == "Т":
                room = str(room_num) + "т"
            elif room_body == "УЛК":
                room = str(room_num) + "л"
            if not connect.check_table_name("classrooms", room):
                connect.insert_classroom(room, capacity, properties, room_body)

        elif action == "delete_classroom":
            name = request.form.get("classroom_name")
            if connect.check_table_name("classrooms", name):
                connect.delete_from_table_name("classrooms", name)

        elif action == "add_subject":
            name = request.form.get("subject_name")
            properties = str(request.form.getlist("subject_properties")).replace("'", '"')
            if not connect.check_table_name("subjects", name):
                connect.insert_subject(name, properties)

        elif action == "delete_subject":
            name = request.form.get("subject_name")
            if connect.check_table_name("subjects", name):
                if connect.check_one_column("linking", "subject", {name}):
                    # name = next(iter(name))
                    # print(f'\n\n\n\n\nNAME:{name}')
                    connect.delete_from_table("linking", "subject", {name})
                connect.delete_from_table_name("subjects", name)
                connect.delete_from_hours_s_name(name)
                connect.delete_subject_tgsl(name)

        elif action == "confirm_sg":
            subject = request.form.get("hours_subject")
            group = request.form.get("hours_group")
            return redirect(f"/admin/hours/{subject}/{group}")

        elif action == "confirm_sl":
            subject = request.form.get("lock_subject")
            return redirect(f"/admin/lock/{subject}")

        elif action == "insert_table":
            connect.create_tables()  # if not exists
            connect.insert_tables()

        elif action == "drop_table":
            connect.drop_tables()
            connect.create_tables()

        elif action.startswith("redact_hours"):
            subject, group = action.split("_")[2:4]
            # print(subject, group)
            return redirect(url_for("admin.hours_table", subject=subject, group=group))
        
        elif action == "add_linking":
            linking_remember=True
            link_subject = request.form.get("linking_subject")
            link_type_subject = request.form.get("linking_type_subject")
            teachers = request.form.getlist("linking_teachers")
            groups = request.form.getlist("linking_groups")
            connect.insert_linking(link_subject, link_type_subject, teachers, groups)
            return redirect(url_for("admin.choice", active_tab="linking-tab"))
        
        elif action == "edit_linking":
            subj = request.form.get("subj")
            type_subj = request.form.get("type_subj")
            id_para = request.form.get("id_para")
            return redirect(f"/admin/linking/{subj}/{type_subj}/{id_para}")

        elif action == "delete_linking":
            subj = request.form.get("subj")
            type_subj = request.form.get("type_subj")
            id_para = request.form.get("id_para")
            connect.delete_linking_stroke(subj, type_subj, int(id_para))
            connect.linking_edit_id_para()
            return redirect(url_for("admin.choice", active_tab="linking-tab"))

        elif action == "schedule_browser":
            return redirect("/admin/schedule")

        elif action == "create_schedule":
            url = config.Config().generator_pavel_create
            response = requests.get(url)
            data = response.json()
            print(data["message"])

        elif action == "schedule_download":
            return download_excel_schedule()

    # print(11111)
    link_subject = request.form.get("linking_subject")
    link_type_subject = request.form.get("linking_type_subject")
    times = connect.select_times()
    hours = connect.select_all_hours()
    if not hours:
        hours = [["-", "-", "-", "-", "-", "-", "-"]]
    # print(hours)
    subjects = connect.select_all_subjects()
    classrooms = connect.select_all_classrooms()
    body_classroom = connect.select_body_classroom()
    properties = connect.select_property()
    groups = connect.select_groups()
    locks = connect.select_locks()
    final_groups = []
    for name, count in groups.items():
        final_groups.append((name, count))
    subjects = sorted(subjects, key=lambda x: x[0])
    classrooms = sorted(classrooms, key=lambda x: x[0])
    properties = sorted(properties, key=lambda x: x[0])
    locks = dict(sorted(locks.items()))
    data_linking = connect.select_linking()
    transform_linking = transform_linkings(data_linking)
    transform_linking = sorted(transform_linking, key=lambda x: x[-1])
    # print(transform_linking)
    # print(transform_linking)
    # print(locks, '\n\n\nUGAGAG\n\n\n')
    # print(hours) # [('Дисциплина кафедры 3', 'ИУ10-14', 0, 0, 0), ('Аналитическая геометрия', 'ИУ10-111', 3, 3, 4)]
    return render_template("admin.html",
                           peoples=peoples,
                           user=session.get("user"),
                           groups=final_groups,
                           properties=properties,
                           classrooms=classrooms,
                           body_classroom=body_classroom,
                           subjects=subjects,
                           flag_hours=flag_hours,
                           hours=hours,
                           times=times,
                           locks=locks,
                           active_tab=active_tab,
                           link_subject=link_subject,
                           link_type_subject=link_type_subject,
                           linking_remember=linking_remember,
                           linkings=transform_linking
                           )


@admin_router.route("/schedule", methods=["POST", "GET"])
def schedule():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "recreate_schedule":
            session["current_course"] = request.form.get("current_course", "1")
            session["current_week_type"] = request.form.get("current_week_type", "all")
            url = config.Config().generator_pavel_create
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                print(data.get("message", "No message in response"))

    url = config.Config().generator_pavel_view
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        # print("Received data:", data)
        # schedule_data = data.get('schedule', {}).get('schedule', {})
        schedule_data = data  # transform_schedule(data)
        metadata = data.get("schedule", {}).get("metadata", {})
        schedule = data.get("schedule", {}).get("schedule", {})
        locked_slots = metadata.get("locked_slots", [])
        groups_name = metadata.get("groups", [])
        groups_name = [group[0] for group in groups_name] if groups_name and isinstance(groups_name[0],
                                                                                        list) else groups_name
        if not all([schedule_data, locked_slots, groups_name]):
            print("Warning: Some data is missing in the response!")
            print(f"inner_schedule: {bool(schedule_data)}")
            print(f"locked_slots: {bool(locked_slots)}")
            print(f"groups_name: {bool(groups_name)}")
        # print(schedule_data,'\n\n\n\n\n\n')
        # print(locked_slots,'\n\n\n\n\n\n\n\n')

        # {1: ["ИУ10-11", "ИУ10-12"],..}
        groups_by_courses: dict[int, list[str]] = dict(enumerate([list(map(lambda x: x[0], filter(
            lambda x: x and (re.match(rf"^ИУ10-{i * 2}\d$", x[0]) or re.match(rf"^ИУ10-{i * 2 - 1}\d$", x[0])),
            metadata["groups"]))) for i in range(1, 7)], start=1))

        return render_template("schedule_web.html",
                               user=session.get("user"),
                               current_course=session.get("current_course", "1"),
                               current_week_type=session.get("current_week_type", "all"),
                               metadata=metadata,
                               schedule=schedule,
                               groups_by_courses=groups_by_courses,
                               )
    return render_template("schedule_web.html",
                           user=session.get("user"),
                           current_course=session.get("current_course", "1"),
                           current_week_type=session.get("current_week_type", "all"),
                           metadata={},
                           schedule={},
                           groups_by_courses={},
                           )


@admin_router.route("/linking/<subject>/<type_subject>/<id_para>", methods=["POST", "GET"])
def linking_table(subject: str, type_subject: str, id_para: str):
    id_para = int(id_para)
    connect = Connect()
    subjects = connect.select_all_subjects()
    subjects = sorted(subjects, key=lambda x: x[0])
    peoples = connect.select_teachers()
    groups = connect.select_groups()
    final_groups = []
    for name, count in groups.items():
        final_groups.append((name, count))
    table = transform_linkings(connect.select_linking())
    # print(table, id_para)
    filtered = [
        row for row in table
        if row[0] == subject and row[1] == type_subject and row[4] == id_para
    ]
    # print(filtered) # [('Java', 'Лекция', ('s', 'Владычинская В.А.'), ('ИУ10-11', 'ИУ10-113'))]
    if not table:
        table = [(subject, type_subject, 'pass', 'pass', '-1')]
    if request.method == "POST":
        action = request.form.get("action")
        if action == "confirm_edit_linking":
            active_tab = request.form.get("active_tab", "linking-tab")
            link_subject = request.form.get("linking_subject")
            link_type_subject = request.form.get("linking_type_subject")
            teachers = request.form.getlist("linking_teachers")
            groups = request.form.getlist("linking_groups")
            # print(f'TEACFHERS: {teachers}\n\n\n\n\n{groups}')
            connect.update_linking(subject, type_subject, link_subject, link_type_subject, teachers, groups, id_para)
            return redirect(url_for("admin.choice", active_tab=active_tab))

    return render_template("linking_table.html",
                           user=session.get("user"),
                           table=filtered,
                           subject=subject,
                           type_subject=type_subject,
                           subjects=subjects,
                           peoples=peoples,
                           groups_list=final_groups)

@admin_router.route("/hours/<subject>/<group>", methods=["POST", "GET"])
def hours_table(subject: str, group: str):
    connect = Connect()
    table = connect.select_hours(subject, group)
    if not table:
        table = [(subject, group, 0, 0, 0)]
    # print('table:', table)
    if request.method == "POST":
        action = request.form.get("action")
        if action == "add_hours_subj_group":
            active_tab = request.form.get("active_tab", "hours-tab")
            ch_sem = request.form.get("ch_sem")
            ch_lec = request.form.get("ch_lec")
            ch_lab = request.form.get("ch_lab")
            one = (subject, group, ch_sem, ch_lec, ch_lab)
            connect.delete_from_hours_s_g_name(subject, group)
            connect.insert_hours(one)
            return redirect(url_for("admin.choice", active_tab=active_tab))

    return render_template("hours_table.html",
                           table=table,
                           subject=subject,
                           group=group)


@admin_router.route("/lock/<subject>", methods=["POST", "GET"])
def lock_table(subject: str):
    connect = Connect()
    table = connect.select_lock(subject)
    if request.method == "POST":
        action = request.form.get("action")
        if action == "add_lock_subj":
            active_tab = request.form.get("active_tab", "lock-slot-tab")
            schedule = {
                "Понедельник": {},
                "Вторник": {},
                "Среда": {},
                "Четверг": {},
                "Пятница": {},
                "Суббота": {}
            }
            time_mapping = {
                "1": "Понедельник",
                "2": "Вторник",
                "3": "Среда",
                "4": "Четверг",
                "5": "Пятница",
                "6": "Суббота"
            }
            for key in request.form:  # для таблицы2 со временем
                if key.startswith("choice"):
                    day_num = key[6]  # Первая цифра после 'choice'
                    time_slot = request.form[key]
                    schedule[time_mapping[day_num]][time_slot] = ""

            for key in request.form:
                if key.startswith("odd_week"):
                    day_num = key[8]
                    time_slot = request.form[key]
                    schedule[time_mapping[day_num]][time_slot] = "odd"
                elif key.startswith("even_week"):
                    day_num = key[9]
                    time_slot = request.form[key]
                    if schedule[time_mapping[day_num]][time_slot] == "odd":
                        schedule[time_mapping[day_num]][time_slot] = "both"
                    else:
                        schedule[time_mapping[day_num]][time_slot] = "even"
            connect.insert_lock_table(schedule, subject)
            # print(schedule)
            return redirect(url_for("admin.choice", active_tab=active_tab))
    # print(table)
    return render_template("lock_table.html",
                           scheduleData=table
                           )


@admin_router.route("/filter_hours", methods=["POST"])
def filter_hours():
    connect = Connect()
    subject = request.json.get("subject", "")
    group = request.json.get("group", "")
    raw_hours = connect.select_filtered_table(subject, group)
    hours_data = []
    for hour in raw_hours:
        # Предполагаем, что hour содержит данные в формате:
        # (subject, group, seminar, lecture, lab)
        hour_dict = {
            "subject": hour[0],
            "group": hour[1],
            "seminar_odd": hour[2],
            "lecture_odd": hour[3],
            "lab_odd": hour[4]
        }
        hours_data.append(hour_dict)
    return jsonify({
        "hours": hours_data
    })


@admin_router.route("/settings", methods=["POST", "GET"])
def anketa():
    connect = Connect()
    user = session.get("selected_teacher")
    if request.method == "POST":
        schedule = {
            "Понедельник": {},
            "Вторник": {},
            "Среда": {},
            "Четверг": {},
            "Пятница": {},
            "Суббота": {}
        }
        time_mapping = {
            "1": "Понедельник",
            "2": "Вторник",
            "3": "Среда",
            "4": "Четверг",
            "5": "Пятница",
            "6": "Суббота"
        }
        for key in request.form:  # для таблицы2 со временем
            if key.startswith("choice"):
                day_num = key[6]  # Первая цифра после 'choice'
                time_slot = request.form[key]
                schedule[time_mapping[day_num]][time_slot] = ""

        for key in request.form:
            if key.startswith("odd_week"):
                day_num = key[8]
                time_slot = request.form[key]
                schedule[time_mapping[day_num]][time_slot] = "odd"
            elif key.startswith("even_week"):
                day_num = key[9]
                time_slot = request.form[key]
                if schedule[time_mapping[day_num]][time_slot] == "odd":
                    schedule[time_mapping[day_num]][time_slot] = "both"
                else:
                    schedule[time_mapping[day_num]][time_slot] = "even"
        # print(schedule) # {'Понедельник': {'08:30 - 10:00': 'odd', '11:50 - 13:20': 'even'}, 'Вторник': {'19:15 - 20:45': 'both'}, 'Среда': {}, 'Четверг': {}, 'Пятница': {}, 'Суббота': {}}
        connect.insert_teacher_time(schedule, user)
        return render_template("data_send.html")

    groups = connect.select_groups()
    subjects_list = connect.select_subjects()
    group_subject = connect.select_teacher_group_subject_ls(user)
    selected_times = connect.select_teacher_time(user)
    times = connect.select_times()
    times_slots = []
    for i, g in enumerate(times):
        times_slots.append((i, g))
    # print(selected_times)
    subjects = []
    for i, el in enumerate(subjects_list):
        subjects.append((i + 1, el))
    # print(selected_times)
    return render_template("new_anketa.html",
                           title="Анкета",
                           user=user,
                           groups_list=groups,
                           subjects=subjects,
                           group_data=group_subject,
                           scheduleData=selected_times,
                           times_slots=times_slots
                           )


@admin_router.route("/subject/<int:subject_id>", methods=["GET", "POST"])
def set_groups_to_subject(subject_id: int):
    connect = Connect()
    user = session.get("selected_teacher")
    subjects_list = connect.select_subjects()
    groups = connect.select_groups()
    subject_list: list[str] = connect.select_subjects()
    if request.method == "POST":
        result = {
            "table_sem": [],
            "table_lec": [],
            "table_lab": []
        }
        for key, value in request.form.items():
            if key.startswith("sem_"):
                result["table_sem"].append(value)
            if key.startswith("lec_"):
                result["table_lec"].append(value)
            if key.startswith("lab_"):
                result["table_lab"].append(value)
        final_result = {user: {subjects_list[subject_id - 1]: result}}
        connect.insert_teacher_group_subject_ls(final_result)
        return redirect("/admin/settings")

    if len(subject_list) < subject_id:
        return redirect("/admin/settings")
    subject = subject_list[subject_id - 1]
    data_tgsl = connect.select_teacher_group_subject_ls(user)
    if user in data_tgsl and subject in data_tgsl[user]:
        data_tgsl = connect.select_teacher_group_subject_ls(user)[user][subject]
    # print(data_tgsl)
    # print('13123', subject)
    return render_template("anketa_subject.html",
                           title=f"Предмет - {subject}",
                           groups_list=groups,
                           backend_data=data_tgsl,
                           user=user
                           )
