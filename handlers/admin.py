import asyncio

from aiogram import Dispatcher, types
from create_bot import bot, dp
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import os
from sqlalchemy.future import select
from sqlalchemy import update, insert
from model import invite_message_class, User
from create_bot import session_maker
from psycopg2.errors import UniqueViolation
from aiogram.utils.exceptions import BotBlocked, CantInitiateConversation
from sqlalchemy.exc import IntegrityError

ADMIN_ID = int(os.getenv("ADMIN_ID"))
SEC_ADMIN = int(os.getenv("SEC_ADMIN"))
trd = int(os.getenv("trd"))


# engine_session = session()
# t = engine_session.query(invite_message_class).filter(invite_message_class.id == 1).all()
# photo_id = t[0].invite_picture
# caption_message = t[0].invite_message
# engine_session.commit()

# photo_id = ''
# caption = ''


async def write_info(variable):
    async with session_maker() as session:
        await session.execute(update(invite_message_class).where(invite_message_class.id == 1).values(
            invite_message=variable['invite'],
            invite_picture=variable['photo']))
        await session.commit()


# async def get_invite_message():
#     async with session_maker() as session:
#         stmt = await session.execute(select(invite_message_class))
#         result = stmt.scalars().first()
#         print(result.id)
#         global caption
#         caption = result.invite_message
#         global photo_id
#         photo_id = result.invite_picture
#         print('123123123')
#         await session.commit()
#         print(session.get_transaction())

#
# ioloop = asyncio.get_event_loop()
# ioloop.run_until_complete(get_invite_message())
# print(ioloop)


class FSMAdmin(StatesGroup):
    photo = State()
    invite = State()


async def block_bot(message: types.Message):
    print('block_bot')
    if message.from_user.id == ADMIN_ID or message.from_user.id == SEC_ADMIN or message.from_user.id == trd:
        await bot.send_message(message.from_user.id, 'Welcome')
    else:
        await bot.send_message(message.from_user.id, 'Not Enough Permissions')


# async def register_new_admin(message: types.ChatMemberOwner):
#     global ID
#     member = await bot.get_chat_member(message.chat.id, message.from_user.id)
#     if (member.is_chat_member()):
#         ID = message.from_user.id

#     await message.delete()
#     print(ID)

async def change_invite_start(message: types.Message):
    print('start and photo')
    if message.from_user.id == ADMIN_ID or message.from_user.id == SEC_ADMIN or message.from_user.id == trd:
        await FSMAdmin.photo.set()
        await message.reply('?????????????? ????????')
    else:
        await bot.send_message(message.from_user.id, 'Not Enough Permissions')


async def load_invite_photo(message: types.Message, state: FSMContext):
    print('message')
    async with state.proxy() as data:
        data['photo'] = message.photo[0].file_id
        await FSMAdmin.next()
        await message.reply('?????????? ?????????????????????????????? ??????????????????')


async def load_invite_message(message: types.Message, state=FSMContext):
    print('load')
    async with state.proxy() as data:
        data['invite'] = message.text
        global photo_id
        photo_id = data['photo']
        print(photo_id)
        global caption
        caption_message = data['invite']
        print(caption_message)
        await write_info(data)
        print(caption_message)
        await bot.send_photo(chat_id=message.from_user.id, photo=data['photo'], caption=data['invite'])
        await state.finish()


async def print_invite(chat_member: types.Message):
    print('print message')
    if chat_member.from_user.id == ADMIN_ID or chat_member.from_user.id == SEC_ADMIN or chat_member.from_user.id == trd:
        await bot.send_photo(chat_member.from_user.id, photo=photo_id, caption=caption)


async def inviteApplyMessage(chat_member: types.ChatJoinRequest):
    async with session_maker() as session:
        stmt = await session.execute(select(invite_message_class))
        result = stmt.scalars().first()
        print(result.id)
        caption = result.invite_message
        photo_id = result.invite_picture
        try:
            stm = await session.execute(insert(User).values(user_id=str(chat_member.from_user.id)))
        except IntegrityError:
            print('Already exists: ' + str(chat_member.from_user.id))
        await session.commit()
    try:
        print('send photo')
        await bot.send_photo(chat_id=chat_member.from_user.id, photo=photo_id, caption=caption)
    except BotBlocked:
        print('Bot Blocked:' + str(chat_member.from_user.id))
    except CantInitiateConversation:
        print('Cant Initiate Dialog:' + str(chat_member.from_user.id))


async def error_command(message: types.Message):
    print('error_command')
    if message.from_user.id == ADMIN_ID or message.from_user.id == SEC_ADMIN or message.from_user.id == trd:

        await bot.send_message(message.from_user.id, "?????? ?????????? ????????????????")
    else:
        await bot.send_message(message.from_user.id, 'Not Enough permissions')


# async def invite_message(message: types.Message):
#     await bot.send_message(message.from_user.id,open("inputtext.txt","r").read())

def reg_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(change_invite_start, commands=['??????????????????????????????'], state=None)
    dp.register_message_handler(load_invite_photo, content_types=['photo'], state=FSMAdmin.photo)
    dp.register_message_handler(load_invite_message, state=FSMAdmin.invite)
    dp.register_message_handler(block_bot, commands='start')
    dp.register_message_handler(print_invite, commands=['invite'])
    dp.register_chat_join_request_handler(inviteApplyMessage)
    dp.register_message_handler(error_command)
    # dp.register_message_handler(invite_message, commands=['??????'])
    # dp.register_message_handler(register_new_admin, commands=['register'])

    # session_engine = session()
    # session_engine.query(invite_message_class).filter(invite_message_class.id == 1).update(
    #     {"invite_message": variable['invite'], "invite_picture": variable['photo']})
    # session_engine.commit()
