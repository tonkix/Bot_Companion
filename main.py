import asyncio
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
import logging
from dotenv import load_dotenv
import os

load_dotenv()

from app.handlers import router
from app.db.models import async_main
from app.scheduler import send_message_cron_at_schedule
from app.scheduler import send_message_cron_at_start
from app.scheduler import SchedulerMiddleware


# Инициализируем логгер
logger = logging.getLogger(__name__)

async def main():
    await async_main()   
    
    # Конфигурируем логирование
    logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
        '[%(asctime)s] - %(name)s - %(message)s')
    # Выводим в консоль информацию о начале запуска
    logger.info('Starting 2147')
    
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()    
    scheduler = AsyncIOScheduler()    
    start_hour = 12
    start_minute = 00    
    scheduler.add_job(send_message_cron_at_schedule, trigger='cron', 
                      hour=start_hour+4, minute=start_minute, 
                      start_date=datetime.now(), 
                      kwargs={'bot': bot})    
    scheduler.add_job(send_message_cron_at_schedule, trigger='cron', 
                      hour=start_hour, minute=start_minute, 
                      start_date=datetime.now(), 
                      kwargs={'bot': bot})  
    scheduler.add_job(send_message_cron_at_schedule, trigger='cron', 
                      hour=start_hour+8, minute=start_minute, 
                      start_date=datetime.now(), 
                      kwargs={'bot': bot})  
    scheduler.add_job(send_message_cron_at_start, trigger='date',
                      run_date=datetime.now() + timedelta(seconds=1),
                      kwargs={'bot': bot})
    scheduler.start()    
    dp.include_router(router)
    dp.update.middleware.register(SchedulerMiddleware(scheduler))
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot disabled")