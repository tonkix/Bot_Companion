import asyncio
from aiogram import Bot, Dispatcher

from app.handlers import router
from app.dataabase.models import async_main

BOT_TOKEN = "7184261886:AAFONN2GZCnUWh_hpl4wi327EmAyk28rd7c"


async def main():
    await async_main()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot disabled")