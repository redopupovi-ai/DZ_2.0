from datetime import datetime

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

import texts as t
from states import Reg
from validators import (
    v_full_name, v_age, v_group, v_phone, v_email, v_city,
    v_university, v_faculty, v_course, v_student_id
)
from db import exists_user, upsert_user
from config import DB_PATH, ADMIN_ID

router = Router()

@router.message(Command("start"))
async def start(message: Message):
    await message.answer(t.START_TEXT)

@router.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(t.CANCEL_TEXT)

@router.message(Command("register"))
async def register(message: Message, state: FSMContext):
    await state.clear()
    if await exists_user(DB_PATH, message.from_user.id):
        await message.answer("Ты уже зарегистрирован. Можешь пройти /register заново — данные перезапишутся.")
    await state.set_state(Reg.full_name)
    await message.answer(t.ASK_FULLNAME)

@router.message(Reg.full_name)
async def step_full_name(message: Message, state: FSMContext):
    try:
        full_name = v_full_name(message.text)
    except ValueError as e:
        await message.answer(f"{e}\n{t.ASK_FULLNAME}")
        return
    await state.update_data(full_name=full_name)
    await state.set_state(Reg.age)
    await message.answer(t.ASK_AGE)

@router.message(Reg.age)
async def step_age(message: Message, state: FSMContext):
    try:
        age = v_age(message.text)
    except ValueError as e:
        await message.answer(f"{e}\n{t.ASK_AGE}")
        return
    await state.update_data(age=age)
    await state.set_state(Reg.group_name)
    await message.answer(t.ASK_GROUP)

@router.message(Reg.group_name)
async def step_group(message: Message, state: FSMContext):
    try:
        group_name = v_group(message.text)
    except ValueError as e:
        await message.answer(f"{e}\n{t.ASK_GROUP}")
        return
    await state.update_data(group_name=group_name)
    await state.set_state(Reg.phone)
    await message.answer(t.ASK_PHONE)

@router.message(Reg.phone)
async def step_phone(message: Message, state: FSMContext):
    try:
        phone = v_phone(message.text)
    except ValueError as e:
        await message.answer(f"{e}\n{t.ASK_PHONE}")
        return
    await state.update_data(phone=phone)
    await state.set_state(Reg.email)
    await message.answer(t.ASK_EMAIL)

@router.message(Reg.email)
async def step_email(message: Message, state: FSMContext):
    try:
        email = v_email(message.text)
    except ValueError as e:
        await message.answer(f"{e}\n{t.ASK_EMAIL}")
        return
    await state.update_data(email=email)
    await state.set_state(Reg.city)
    await message.answer(t.ASK_CITY)

@router.message(Reg.city)
async def step_city(message: Message, state: FSMContext):
    try:
        city = v_city(message.text)
    except ValueError as e:
        await message.answer(f"{e}\n{t.ASK_CITY}")
        return
    await state.update_data(city=city)
    await state.set_state(Reg.university)
    await message.answer(t.ASK_UNI)

@router.message(Reg.university)
async def step_university(message: Message, state: FSMContext):
    try:
        university = v_university(message.text)
    except ValueError as e:
        await message.answer(f"{e}\n{t.ASK_UNI}")
        return
    await state.update_data(university=university)
    await state.set_state(Reg.faculty)
    await message.answer(t.ASK_FACULTY)

@router.message(Reg.faculty)
async def step_faculty(message: Message, state: FSMContext):
    try:
        faculty = v_faculty(message.text)
    except ValueError as e:
        await message.answer(f"{e}\n{t.ASK_FACULTY}")
        return
    await state.update_data(faculty=faculty)
    await state.set_state(Reg.course)
    await message.answer(t.ASK_COURSE)

@router.message(Reg.course)
async def step_course(message: Message, state: FSMContext):
    try:
        course = v_course(message.text)
    except ValueError as e:
        await message.answer(f"{e}\n{t.ASK_COURSE}")
        return
    await state.update_data(course=course)
    await state.set_state(Reg.student_id)
    await message.answer(t.ASK_STUDENT_ID)

@router.message(Reg.student_id)
async def step_student_id(message: Message, state: FSMContext):
    try:
        student_id = v_student_id(message.text)
    except ValueError as e:
        await message.answer(f"{e}\n{t.ASK_STUDENT_ID}")
        return

    data = await state.get_data()
    row = {
        "tg_id": message.from_user.id,
        "full_name": data["full_name"],
        "age": data["age"],
        "group_name": data["group_name"],
        "phone": data["phone"],
        "email": data["email"],
        "city": data["city"],
        "university": data["university"],
        "faculty": data["faculty"],
        "course": data["course"],
        "student_id": student_id,
        "telegram_username": message.from_user.username or "no_username",
        "created_at": datetime.utcnow().isoformat(timespec="seconds"),
    }

    await upsert_user(DB_PATH, row)
    await state.clear()

    try:
        await message.bot.send_message(
            ADMIN_ID,
            "✅ Новая регистрация:\n"
            f"ФИО: {row['full_name']}\n"
            f"Возраст: {row['age']}\n"
            f"Группа: {row['group_name']}\n"
            f"Курс: {row['course']}\n"
            f"Город: {row['city']}\n"
            f"Телефон: {row['phone']}\n"
            f"Email: {row['email']}\n"
            f"Студбилет: {row['student_id']}\n"
            f"TG: @{row['telegram_username']}\n"
            f"ID: {row['tg_id']}"
        )
    except Exception:
        pass

    await message.answer(
        "✅ Зарегистрировал!\n\n"
        f"ФИО: {row['full_name']}\n"
        f"Возраст: {row['age']}\n"
        f"Группа: {row['group_name']}\n"
        f"Телефон: {row['phone']}\n"
        f"Email: {row['email']}\n"
        f"Город: {row['city']}\n"
        f"Университет: {row['university']}\n"
        f"Факультет: {row['faculty']}\n"
        f"Курс: {row['course']}\n"
        f"Студбилет: {row['student_id']}\n"
        f"Юзернейм: @{row['telegram_username']}\n"
    )