from datetime import datetime, timedelta
from aiogram import F, Bot, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
import os
# import openai


import app.keyboard as kb
import app.db.requests as rq
from app.scheduler import send_message_cron

load_dotenv()
# openai.api_key = os.getenv('tg_bot_token_new')
# openai.api_key = os.getenv('tg_bot_token')
router = Router()
conversation_history = {}


class CustomQuestion(StatesGroup):
    tg_id = State()
    text = State()


class NewQuestion(StatesGroup):
    password = State()
    category_id = State()
    text = State()


@router.message(CommandStart())
@router.message(F.text == 'На главную')
async def cmd_start(message: Message, bot: Bot):
    await rq.set_user(message.from_user.id,
                      message.from_user.first_name,
                      message.from_user.last_name,
                      False)
    me = await bot.get_me()
    await message.reply(f"Привет!\nЯ - {me.first_name}", reply_markup=kb.main)


@router.message(F.text == 'Подписаться')
async def cmd_subscribe(message: Message):
    await rq.subscribe(message.from_user.id)
    await message.answer(f"Вы подписались от рассылки")


@router.message(F.text == 'Отписаться')
async def cmd_unsubscribe(message: Message):
    await rq.unsubscribe(message.from_user.id)
    await message.answer(f"Вы отписались от рассылки")


@router.message(Command('add'))
async def cmd_add_new_question(message: Message, state: FSMContext):
    await message.answer(f"Введите пароль")
    await state.set_state(NewQuestion.password)


@router.message(Command('clear'))
async def process_clear_command(message: Message):
    user_id = message.from_user.id
    conversation_history[user_id] = []
    await message.reply("История диалога очищена.")


@router.message(NewQuestion.password)
async def password_for_new_question(message: Message, state: FSMContext):
    await state.update_data(password=message.text)
    await state.set_state(NewQuestion.category_id)
    await message.answer(f"Введите id категории")


@router.message(NewQuestion.category_id)
async def category_for_new_question(message: Message, state: FSMContext):
    await state.update_data(category_id=message.text)
    await state.set_state(NewQuestion.text)
    await message.answer('Введите текст вопроса')


@router.message(NewQuestion.text)
async def text_for_new_question(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    data = await state.get_data()
    await rq.add_question(password=data["password"],
                          category_id=data["category_id"],
                          question_text=data["text"])
    await state.clear()


@router.callback_query(F.data == 'to_main')
async def to_main(callback: CallbackQuery):
    await callback.answer('Главное меню')
    await callback.message.answer('Вы вернулись на главную страницу!', reply_markup=kb.main)


@router.message(F.text == 'Категории')
async def categories(message: Message):
    await message.answer('Выберите категорию', reply_markup=await kb.categories())


@router.callback_query(F.data.startswith('user_'))
async def categories(callback: CallbackQuery):
    await callback.answer('Успешно!')
    await callback.message.answer('Выберите категорию', reply_markup=await kb.
                                  categories(callback.data.split('_')[1]))


@router.message(F.text == 'Все пользователи')
async def categories(message: Message):
    await message.answer('Выберите пользователя', reply_markup=await kb.users())


@router.callback_query(F.data.startswith('category_'))
async def category(callback: CallbackQuery):
    await callback.answer('Вы выбрали категорию')
    await callback.message.answer('Выберите вопрос по категории, отправлю его через минуту',
                                  reply_markup=await kb.questions(callback.data.split('_')[1],
                                                                  callback.data.split('_')[2]))


@router.callback_query(F.data.startswith('question_'))
async def question(callback: CallbackQuery, bot: Bot, scheduler: AsyncIOScheduler):
    question_data = await rq.get_question(callback.data.split('_')[1])
    user = await rq.get_user_by_id(callback.data.split('_')[2])
    await callback.answer('Вы выбрали вопрос')
    start_hour = (datetime.now()).hour
    start_minute = (datetime.now() + timedelta(minutes=1)).minute

    scheduler.add_job(send_message_cron, trigger='cron',
                      hour=start_hour, minute=start_minute,
                      start_date=datetime.now(),
                      end_date=datetime.now() + timedelta(hours=2),
                      kwargs={'bot': bot,
                              'tg_id': user.tg_id,
                              'message_text': question_data.question})


@router.callback_query(F.data.startswith('custom_question'))
async def question(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Вы выбрали вопрос')
    user = await rq.get_user_by_id(callback.data.split('_')[2])
    await callback.answer(callback.data)
    await callback.message.answer('Введите свой вопрос, отправлю его через минуту')
    await state.update_data(tg_id=user.tg_id)
    await state.set_state(CustomQuestion.text)


@router.message(CustomQuestion.text)
async def send_custom_question(message: Message, bot: Bot,
                               state: FSMContext, scheduler: AsyncIOScheduler):
    tg_id = await state.get_data()
    start_hour = (datetime.now()).hour
    start_minute = (datetime.now() + timedelta(minutes=1)).minute

    scheduler.add_job(send_message_cron, trigger='cron',
                      hour=start_hour, minute=start_minute,
                      start_date=datetime.now(),
                      end_date=datetime.now() + timedelta(hours=2),
                      kwargs={'bot': bot, 'tg_id': tg_id, 'message_text': message.text})

    await state.clear()


def trim_history(history, max_length=4096):
    current_length = sum(len(message["content"]) for message in history)
    while history and current_length > max_length:
        removed_message = history.pop(0)
        current_length -= len(removed_message["content"])
    return history


@router.message()
async def any_reply(message: Message, bot: Bot):
    user = await rq.get_user_by_tg(message.from_user.id)
    # await message.reply(f"Я пока не умею отвечать на такие сообщения\nХорошего дня!")
    '''await bot.forward_message(os.getenv("MY_ID"), user.tg_id, message_id=message.message_id, 
                                                 message_thread_id=message.message_thread_id)'''
    import g4f
    from g4f.client import AsyncClient
    from g4f.Provider import BingCreateImages, OpenaiChat, Gemini

    user_id = message.from_user.id
    user_input = message.text

    if user_id not in conversation_history:
        conversation_history[user_id] = []
        conversation_history[user_id].append({"role": "user", "content": "пиши на русском языке"})
        conversation_history[user_id].append({"role": "user", "content": "пиши только по русски"})
        conversation_history[user_id].append({"role": "user", "content": "не отвечай на английском"})

    conversation_history[user_id].append({"role": "user", "content": user_input})
    conversation_history[user_id] = trim_history(conversation_history[user_id])

    chat_history = conversation_history[user_id]

    try:
        g4f.debug.logging = False  # enable logging
        g4f.check_version = False  # Disable automatic version checking
        print(g4f.version)  # check version
        print(g4f.Provider.Ails.params)  # supported args

        client = AsyncClient(
            api_key=os.getenv("tg_bot_token_new"),
            provider=g4f.Provider.You,
            # provider=OpenaiChat,
        )

        response = await g4f.ChatCompletion.create_async(
            model=g4f.models.default,
            # model="gpt-3.5-turbo",
            # model="gpt-4",
            # model=g4f.models.gpt_4,
            messages=chat_history,
            # provider=g4f.Provider.PerplexityLabs,
            provider=g4f.Provider.FreeGpt,  # работает 21/07/24
            api_key=os.getenv("tg_bot_token_new"),
        )
        conversation_history[user_id].append({"role": "assistant", "content": response})
        await message.reply(response)

    except Exception as e:
        print(f"{g4f.Provider.GeekGpt.__name__}:", e)
        chat_gpt_response = "Извините, произошла ошибка."


'''
@router.message(Command('Help'))
async def cmd_help(message: Message):
    await message.answer('Раздел помощи')


@router.message(F.text == 'Кнопка')
async def userText(message: Message):
    await message.reply('Сделай выбор', reply_markup=kb.inlineKB)


@router.callback_query(F.data == 'button')
async def callButton(callback: CallbackQuery):
    await callback.answer('Добро пожаловать!')   
    await callback.message.answer('Добро пожаловать!')    


@router.message(Command('Register'))
async def register(message: Message, state: FSMContext):
    await state.set_state(Register.name)
    await message.answer('Введите имя')



@router.message(Register.name)
async def register_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Register.age)
    await message.answer('Сколько вам лет?')


@router.message(Register.age)
async def register_age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await state.set_state(Register.number)
    await message.answer('Введите номер', reply_markup=kb.get_number)



@router.message(Register.number, F.contact)
async def register_number(message: Message, state: FSMContext):    
    await state.update_data(number=message.contact.phone_number)
    data = await state.get_data()
    await message.answer(f'Ваше имя {data["name"]} \nВаш возраст {data["age"]} \nВаш номер: {data["number"]}')
    await state.clear()

    '''