from aiogram import F, Bot, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


import app.keyboard as kb
import app.dataabase.requests as rq


MY_ID = '657559316'
BOT_TOKEN = "7184261886:AAFONN2GZCnUWh_hpl4wi327EmAyk28rd7c"
bot = Bot(token=BOT_TOKEN)
router = Router()


'''class Register(StatesGroup):
    name = State()
    age = State()
    number = State()'''

@router.message(CommandStart())
@router.message(F.text == 'На главную')
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id, message.from_user.first_name, message.from_user.last_name)
    await message.reply('Привет!', reply_markup=kb.main)
    await message.answer('Я - бот 2147')
    

@router.callback_query(F.data == 'to_main')
async def to_main(callback: CallbackQuery):
    await callback.answer('Главное меню')
    await callback.message.answer('Вы вернулись на главную страницу!', reply_markup=kb.main)


@router.message(F.text == 'Категории')
async def categories(message: Message):
    await message.answer('Выберите категорию', reply_markup=await kb.categories())
    

@router.callback_query(F.data.startswith('user_'))
async def categories(callback: CallbackQuery):
    await callback.message.answer('Выберите категорию', reply_markup=await kb.
                                  categories(callback.data.split('_')[1]))

    
@router.message(F.text == 'Все пользователи')
async def categories(message: Message):
    await message.answer('Выберите пользователя', reply_markup=await kb.users())


@router.callback_query(F.data.startswith('category_'))
async def category(callback: CallbackQuery):
    await callback.answer('Вы выбрали категорию')
    await callback.message.answer('Выберите вопрос по категории',
                                  reply_markup=await kb.questions(callback.data.split('_')[1], 
                                                                  callback.data.split('_')[2]))

@router.callback_query(F.data.startswith('question_'))
async def question(callback: CallbackQuery):
    question_data = await rq.get_question(callback.data.split('_')[1])
    user = await rq.get_user_by_id(callback.data.split('_')[2])
    await callback.answer('Вы выбрали вопрос')
    await bot.send_message(user.tg_id, question_data.question)


@router.message()
async def any_reply(message: Message):
    user = await rq.get_user_by_tg(message.from_user.id)
    await bot.forward_message(MY_ID, user.tg_id, message_id=message.message_id, 
                                                 message_thread_id=message.message_thread_id)

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