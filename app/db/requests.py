import random
from app.db.models import async_session
from app.db.models import User, Category, Question
from sqlalchemy import select


async def set_user(tg_id, firstname, lastname, subscribed):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id,
                             firstname=firstname,
                             lastname=lastname,
                             subscribed=subscribed))
            await session.commit()


async def check_password(password):
    return password == '41802967'


async def get_user_by_tg(tg_id):
    async with async_session() as session:
        return await session.scalar(select(User).where(User.tg_id == tg_id))


async def get_user_by_id(id):
    async with async_session() as session:
        return await session.scalar(select(User).where(User.id == id))


async def subscribe(tg_id):
    async with async_session() as session:
        result = await session.execute(select(User)
                                       .order_by(User.id)
                                       .where(User.tg_id == tg_id)
                                       .limit(1))
        user = result.scalar()
        user.subscribed = True
        await session.commit()


async def unsubscribe(tg_id):
    async with async_session() as session:
        result = await session.execute(select(User)
                                       .order_by(User.id)
                                       .where(User.tg_id == tg_id)
                                       .limit(1))
        user = result.scalar()
        user.subscribed = False
        await session.commit()


async def add_question(password, category_id, question_text):
    async with async_session() as session:
        if check_password(password):
            session.add(Question(question=question_text,
                                 category=category_id))
            await session.commit()


async def get_all_users():
    async with async_session() as session:
        return await session.scalars(select(User))


async def get_categories():
    async with async_session() as session:
        return await session.scalars(select(Category))


async def get_category_questions(category_id):
    async with async_session() as session:
        return await session.scalars(select(Question).where(Question.category == category_id))


async def get_question(question_id):
    async with async_session() as session:
        return await session.scalar(select(Question).where(Question.id == question_id))


async def get_subscribed_users():
    async with async_session() as session:
        return await session.scalars(select(User).where(User.subscribed == 1))


async def get_rand_question_by_category(category_id):
    async with async_session() as session:
        data = await session.scalars(select(Question).where(Question.category == category_id))
        data = list(data)
        return data[random.randrange(len(data))]
