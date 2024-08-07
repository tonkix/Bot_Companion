from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton

from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.db.requests import get_categories
from app.db.requests import get_all_users
from app.db.requests import get_category_questions

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='/start')],
                                     [KeyboardButton(text='Все пользователи')],
                                     [KeyboardButton(text='На главную')],
                                     [KeyboardButton(text='Подписаться'),
                                      KeyboardButton(text='Отписаться')]],
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт меню'
                           )


async def categories(user_id):
    all_categories = await get_categories()
    keyboard = InlineKeyboardBuilder()
    for category in all_categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f"category_{category.id}_{user_id}"))
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    return keyboard.adjust(1).as_markup()


async def users():
    all_users = await get_all_users()
    keyboard = InlineKeyboardBuilder()
    for user in all_users:
        keyboard.add(
            InlineKeyboardButton(text=str(user.firstname) + " " + str(user.lastname), callback_data=f"user_{user.id}"))
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    return keyboard.adjust(1).as_markup()


async def questions(category_id, user_id):
    all_questions = await get_category_questions(category_id)
    keyboard = InlineKeyboardBuilder()
    for question in all_questions:
        keyboard.add(InlineKeyboardButton(text=question.question, callback_data=f"question_{question.id}_{user_id}"))
    keyboard.add(InlineKeyboardButton(text='Свой вопрос', callback_data=f"custom_question_{user_id}"))
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    return keyboard.adjust(1).as_markup()
