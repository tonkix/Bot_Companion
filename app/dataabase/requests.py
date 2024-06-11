from app.dataabase.models import async_session
from app.dataabase.models import User, Category, Question
from sqlalchemy import select


async def set_user(tg_id, firstname, lastname):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        
        if not user:
            session.add(User(tg_id=tg_id, firstname=firstname, lastname=lastname))
            await session.commit()


async def get_user_by_tg(tg_id):
    async with async_session() as session:
        return await session.scalar(select(User).where(User.tg_id == tg_id))


async def get_user_by_id(id):
    async with async_session() as session:
        return await session.scalar(select(User).where(User.id == id))


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