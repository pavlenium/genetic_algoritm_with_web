def transform_schedule(original_data):
    transformed = {}

    # Обрабатываем locked_slots
    locked_lessons = {}
    for slot in original_data["schedule"]["metadata"].get("locked_slots", []):
        _, group, day, time_slot, is_ch, is_zn = slot
        if group not in locked_lessons:
            locked_lessons[group] = {}
        if day not in locked_lessons[group]:
            locked_lessons[group][day] = {}

        if is_ch:
            locked_lessons[group][day][time_slot] = {
                "Преподаватель": "Админ",
                "Предмет": "Заблокировано админом",
                "Время": time_slot,
                "Тип недели": "Чс",
                "Тип пары": ""
            }
        if is_zn:
            locked_lessons[group][day][f"{time_slot}_Зн"] = {
                "Преподаватель": "Админ",
                "Предмет": "Заблокировано админом",
                "Время": time_slot,
                "Тип недели": "Зн",
                "Тип пары": ""
            }

    for group_name, group_schedule in original_data["schedule"]["schedule"].items():
        # Определяем курс (ваш код правильный)
        group_num = group_name.split("-")[1]
        courses_mapping = {"1": 1, "3": 2, "5": 3, "7": 4, "9": 5}
        if len(group_num) == 2:
            course = courses_mapping.get(group_num[0], 1)
        elif len(group_num) == 3:
            course = 6

        if course not in transformed:
            transformed[course] = {}

        group_data = {}

        # Сначала добавляем все обычные занятия
        for day_with_type, lessons in group_schedule.items():
            day_name, week_type = day_with_type.split("_")
            week_type = "Чс" if week_type == "ч" else "Зн"

            if day_name not in group_data:
                group_data[day_name] = {}

            for lesson in lessons:
                time_slot = lesson["time_slot"]  # ИСПРАВЛЕНО: убрано [0]
                lecturer = lesson["lecturer"]
                subject = lesson["subject"]
                lesson_type = lesson.get("lesson_type", "")

                # Ключ для знаменателя — с суффиксом _Зн
                slot_key = f"{time_slot}_Зн" if week_type == "Зн" else time_slot

                group_data[day_name][slot_key] = {
                    "Преподаватель": lecturer,
                    "Предмет": subject,
                    "Время": time_slot,
                    "Тип недели": week_type,
                    "Тип пары": lesson_type
                }

        # Затем добавляем/перезаписываем заблокированные слоты
        if group_name in locked_lessons:
            for day, slots in locked_lessons[group_name].items():
                if day not in group_data:
                    group_data[day] = {}
                # Заблокированные слоты имеют приоритет
                for slot_key, blocked_lesson in slots.items():
                    group_data[day][slot_key] = blocked_lesson

        # Объединяем слоты для Чс/Зн
        for day_name, day_schedule in group_data.items():
            slots_to_remove = []
            slots_to_update = []

            for slot_key, lesson_data in day_schedule.items():
                if "_Зн" in slot_key:
                    base_slot = slot_key.replace("_Зн", "")
                    if base_slot in day_schedule:
                        base_lesson = day_schedule[base_slot]
                        zn_lesson = day_schedule[slot_key]

                        # Проверяем, что оба НЕ заблокированы
                        if (base_lesson["Предмет"] != "Заблокировано админом" and
                                zn_lesson["Предмет"] != "Заблокировано админом"):

                            # Если предметы и преподаватели одинаковые - объединяем
                            if (base_lesson["Предмет"] == zn_lesson["Предмет"] and
                                    base_lesson["Преподаватель"] == zn_lesson["Преподаватель"]):

                                base_lesson["Тип недели"] = "Чс/Зн"
                                slots_to_remove.append(slot_key)
                            else:
                                # Если разные - помечаем оба как Чс/Зн но оставляем раздельно
                                base_lesson["Тип недели"] = "Чс/Зн"
                                zn_lesson["Тип недели"] = "Чс/Зн"

            # Удаляем объединенные слоты
            for slot_key in slots_to_remove:
                del day_schedule[slot_key]

        transformed[course][group_name] = group_data

    return transformed