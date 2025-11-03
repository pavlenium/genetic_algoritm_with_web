def transform_linkings(data: list):
    """
    Преобразует список (subject, type, teacher, group, id_para)"""
    result = {}
    # print(data)
    for subj, type_subj, teacher, group, id_para in data:
        key = (subj, type_subj, id_para)
        if key not in result:
            result[key] = {"teachers": set(), "groups": set(), "id_para": -1}
        result[key]["teachers"].add(teacher)
        result[key]["groups"].add(group)
        # result[key]["id_para"] = id_para

    # превращаем во вложенные кортежи
    transformed = []
    for (subj, type_subj, id_para), vals in result.items():
        teachers = tuple(sorted(vals["teachers"]))
        groups = tuple(sorted(vals["groups"]))
        # id_para = vals["id_para"]
        # если преподаватель один — оставляем строку, а не tuple
        teachers = teachers if len(teachers) > 1 else teachers[0]
        groups   = groups   if len(groups) > 1   else groups[0]
        transformed.append((subj, type_subj, teachers, groups, id_para))

    return transformed
