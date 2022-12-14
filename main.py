from aiogram import executor
from create_bot import dp, bot, WEBHOOK_URL, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT
import asyncio
from engine import create_async_engine, proceed_schemas,get_session_maker
from handlers import admin, client, other
from model import Base

other.reg_handlers_other(dp)
admin.reg_handlers_admin(dp)
# client.reg_handlers_client(dp)


async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)

async def on_shutdown(dispatcher):
    await bot.delete_webhook()

executor.start_webhook(dispatcher=dp,skip_updates=True,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT)



