from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import BaseMiddleware
from aiogram.types.base import TelegramObject
from typing import Dict, Any, Callable, Awaitable

import app.dataabase.requests as rq

class SchedulerMiddleware(BaseMiddleware):

    def __init__(self, scheduler: AsyncIOScheduler):
        self.scheduler = scheduler
        
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        data["scheduler"] = self.scheduler
        return await handler(event, data)




async def send_message_cron(bot: Bot, tg_id, message_text: str):
    await bot.send_message(tg_id, message_text)
    
async def send_message_cron2(bot: Bot):
    question = await rq.get_rand_question_by_category(2)
    users = await rq.get_subscirbed_users()
    for user in users:
        await bot.send_message(str(user.tg_id), f"Привет\n{question.question}")