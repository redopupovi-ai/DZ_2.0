from aiogram.fsm.state import State, StatesGroup

class Reg(StatesGroup):
    full_name = State()
    age = State()
    group_name = State()
    phone = State()
    email = State()
    city = State()
    university = State()
    faculty = State()
    course = State()
    student_id = State()