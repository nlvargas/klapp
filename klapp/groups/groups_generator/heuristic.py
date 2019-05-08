from groups.groups_generator.params import students, groups
from random import choice
from openpyxl import Workbook

qmax = 6

def assign():
    for student in students:
        if student.preferences[0] == "#N/A":
            student.priority = 0
        else:
            student.priority = 10  # Should be a function
    #  Sort by priority
    students.sort(key=lambda x: x.priority, reverse=True)

    # Create a group with the first preference of the first student
    groups_created = [students[0].preferences[0]]

    assignment(students, groups_created, 0)
    first_row = ["Grupo", "Alumno 1", "Alumno 2", "Alumno 3", "Alumno 4", "Alumno 5",
                 "Alumno 6", "Alumno 7", "Alumno 8", "Alumno 9", "Alumno 10"]

    for student in students:
        groups[student.asignation].append(student.id)
    print(groups)
    save_results(first_row, groups)


def assignment(students, groups_created, i):
    if i == len(students):
        return True
    student = students[i]
    #  is better to create a new group or have a lower priority rate?
    for preference in student.preferences:
        if isValid(student, preference):
            if preference in groups_created:
                student.asignation = preference
                if assignment(students, groups_created, i + 1):
                    return True
                student.asignation = None
            elif len(groups_created) < qmax:
                groups_created.append(preference)
                student.asignation = preference
                if assignment(students, groups_created, i + 1):
                    return True
                student.asignation = None
                groups_created.remove(preference)
    #  add student to a convenient group
    group = convenientGroup(student, groups_created)
    student.asignation = group
    if assignment(students, groups_created, i + 1):
        return True
    student.asignation = None
    return False


def save_results(first_row, res):
    book = Workbook()
    sheet = book.active
    sheet.append(first_row)
    for row in res:
        r = []
        r.append(row)
        r += res[row]
        if len(r) >= 2:
            sheet.append(r)
    book.save('results.xlsx')


def isValid(student, group):
    #  Checks for groups general constrains
    return True


def convenientGroup(student, groups_created):
    #  Picks the group with less flexibility or frequency
    return choice(groups_created)






