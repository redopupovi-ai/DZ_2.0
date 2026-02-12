import re

_phone_re = re.compile(r"^\+?\d{10,15}$")
_email_re = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def v_full_name(value: str) -> str:
    value = (value or "").strip()
    if len(value) < 5 or " " not in value:
        raise ValueError("ФИО минимум 5 символов и с пробелом (Иванов Иван).")
    return value

def v_age(value: str) -> int:
    value = (value or "").strip()
    if not value.isdigit():
        raise ValueError("Возраст должен быть числом.")
    age = int(value)
    if age < 14 or age > 80:
        raise ValueError("Возраст от 14 до 80.")
    return age

def v_group(value: str) -> str:
    value = (value or "").strip()
    if len(value) < 2:
        raise ValueError("Группа слишком короткая.")
    return value

def v_phone(value: str) -> str:
    value = (value or "").strip().replace(" ", "").replace("-", "")
    if not _phone_re.match(value):
        raise ValueError("Телефон: +996XXXXXXXXX (10–15 цифр).")
    return value

def v_email(value: str) -> str:
    value = (value or "").strip()
    if not _email_re.match(value):
        raise ValueError("Email должен быть похож на example@mail.com")
    return value

def v_city(value: str) -> str:
    value = (value or "").strip()
    if len(value) < 2:
        raise ValueError("Город слишком короткий.")
    return value

def v_university(value: str) -> str:
    value = (value or "").strip()
    if len(value) < 2:
        raise ValueError("Университет слишком короткий.")
    return value

def v_faculty(value: str) -> str:
    value = (value or "").strip()
    if len(value) < 2:
        raise ValueError("Факультет слишком короткий.")
    return value

def v_course(value: str) -> int:
    value = (value or "").strip()
    if not value.isdigit():
        raise ValueError("Курс должен быть числом.")
    course = int(value)
    if course < 1 or course > 6:
        raise ValueError("Курс от 1 до 6.")
    return course

def v_student_id(value: str) -> str:
    value = (value or "").strip()
    if len(value) < 4:
        raise ValueError("Студбилет/ID слишком короткий.")
    return value