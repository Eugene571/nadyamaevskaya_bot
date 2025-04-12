from sqlalchemy import create_engine, Column, Integer, BigInteger, Boolean, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from bot.config import DB_URL
from contextlib import contextmanager
from datetime import datetime

Base = declarative_base()


# Модель пользователя
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger, unique=True)
    name = Column(String)
    birthday = Column(Date)
    phone = Column(String)
    is_paid = Column(Boolean, default=False)
    has_received_pdf = Column(Boolean, default=False)  # Флаг для проверки, получал ли пользователь PDF


# Подключение к БД
engine = create_engine(DB_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


# Функция для инициализации таблиц
def init_db():
    Base.metadata.create_all(bind=engine)


def parse_birthday(birthday_str: str):
    try:
        return datetime.strptime(birthday_str, "%d.%m.%Y").date()
    except ValueError:
        return None


def save_user_data(tg_id: int, name: str, birthday: str, phone: str):
    # Парсим дату рождения
    birthday_date = parse_birthday(birthday)
    if not birthday_date:
        return "Неверный формат даты! Используй формат ДД.ММ.ГГГГ."

    # Открываем сессию для работы с БД
    with get_session() as session:
        # Ищем пользователя по tg_id
        user = session.query(User).filter_by(tg_id=tg_id).first()
        if user:
            # Обновляем данные пользователя
            user.name = name
            user.birthday = birthday_date  # Сохраняем как объект Date
            user.phone = phone
            session.commit()
        return "Данные успешно сохранены."


# Функция для получения пользователя по tg_id
def get_user_by_tg_id(tg_id: int):
    with get_session() as session:
        user = session.query(User).filter_by(tg_id=tg_id).first()
        return user


# Функция для создания пользователя, если его нет
def create_user_if_not_exists(tg_id: int):
    with get_session() as session:
        user = session.query(User).filter_by(tg_id=tg_id).first()
        if not user:
            user = User(tg_id=tg_id)
            session.add(user)
            session.commit()
        return user


# Функция для получения данных пользователя (с полями: name, birthday, phone)
def get_user_data(tg_id: int):
    user = get_user_by_tg_id(tg_id)
    if user:
        return {
            "name": user.name,
            "birthday": user.birthday,
            "phone": user.phone
        }
    return None
