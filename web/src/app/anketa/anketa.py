
from flask import Blueprint, redirect, render_template, request, session

from app.postgre.connect import Connect

anketa_router = Blueprint("anketa", __name__)

@anketa_router.route("/", methods=["POST", "GET"])
def anketa():
    connect = Connect()
    user = session.get("user")
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
        for key in request.form: # для таблицы2 со временем
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
    # print(times_slots)
    # print(selected_times)
    subjects = []
    for i, el in enumerate (subjects_list):
        subjects.append((i + 1, el))
    # print(selected_times)
    return render_template("new_anketa.html",
                           title="Анкета",
                           user=user,
                           groups_list=groups,
                           subjects=subjects,
                           group_data=group_subject,
                           scheduleData = selected_times,
                           times_slots=times_slots
                           )


@anketa_router.route("/subject/<int:subject_id>", methods=["GET", "POST"])
def set_groups_to_subject(subject_id: int):
    connect = Connect()
    user = session.get("user")
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
        final_result = {user: {subjects_list[subject_id-1]: result}}
        connect.insert_teacher_group_subject_ls(final_result)
        return redirect("/anketa")

    if len(subject_list)<subject_id:
        return redirect("/anketa")
    subject = subject_list[subject_id-1]
    data_tgsl = connect.select_teacher_group_subject_ls(user)
    if user in data_tgsl and subject in data_tgsl[user]:
        data_tgsl = connect.select_teacher_group_subject_ls(user)[user][subject]
    # print(data_tgsl)
    # print('13123', subject)
    return  render_template("anketa_subject.html",
                           title=f"Предмет - {subject}",
                           groups_list=groups,
                            backend_data=data_tgsl,
                            user=user
                           )
