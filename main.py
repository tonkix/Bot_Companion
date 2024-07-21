import asyncio
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
import logging
import os
from dotenv import load_dotenv

from app.handlers import router
from app.db.models import async_main
from app.scheduler import send_message_cron_at_schedule
from app.scheduler import send_message_cron_at_start
from app.scheduler import SchedulerMiddleware

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Инициализируем логгер
file_handler = logging.FileHandler('my_logs.log')
file_handler.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.INFO,
                    handlers=[file_handler],
                    format='%(levelname)-8s ## %(filename)s:%(lineno)d #####'
                           '[%(asctime)s] - %(name)s - %(message)s')


async def main():
    await async_main()

    logging.info('Starting 2147')

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    scheduler = AsyncIOScheduler()
    start_hour = 12
    start_minute = 00
    scheduler.add_job(send_message_cron_at_schedule, trigger='cron',
                      hour=start_hour + 4, minute=start_minute,
                      start_date=datetime.now(),
                      kwargs={'bot': bot})
    scheduler.add_job(send_message_cron_at_schedule, trigger='cron',
                      hour=start_hour, minute=start_minute,
                      start_date=datetime.now(),
                      kwargs={'bot': bot})
    scheduler.add_job(send_message_cron_at_schedule, trigger='cron',
                      hour=start_hour + 8, minute=start_minute,
                      start_date=datetime.now(),
                      kwargs={'bot': bot})
    scheduler.add_job(send_message_cron_at_start, trigger='date',
                      run_date=datetime.now() + timedelta(seconds=1),
                      kwargs={'bot': bot})
    scheduler.start()
    dp.include_router(router)
    dp.update.middleware.register(SchedulerMiddleware(scheduler))
    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot disabled")
