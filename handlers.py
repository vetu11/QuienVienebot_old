# coding=utf-8
# Archivo: handlers
# Descripción: Aquí se declararán los handlers a las distintas llamadas de la API.

from lang import get_lang
from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup


def generic_message(bot, update, text_code):
    # Responde a cualquier mensaje con un texto genérico, sin añadiduras.
    message = update.effective_message
    user = update.effective_user
    user_lang_code = user.language_code
    lang = get_lang(user_lang_code)

    message.reply_text(lang.get_text(text_code), parse_mode=ParseMode.MARKDOWN)


# --- COMANDOS GENERICOS ---
def start(bot, update):
    # Responde al comando "/start"

    generic_message(bot, update, "start")


def help(bot, update):
    # Responde al comando "/help"

    generic_message(bot, update, "help")


def more(bot, update):
    # Responde al comando "/more"

    generic_message(bot, update, "more")


def donate(bot, update):
    # Responde al comando "/donate"

    user_data["donacion"] = 5
    text = "Gracias de antemano por considerar donar. Soy un único desarrollador y me dedico a hacer bots gra" \
           "tuitos mayormente. Las donaciones iran a cubrir los gastos del servidor como primera prioridad y" \
           " como segunda las horas gastadas delante del ordenador. Puedes donar la cantidad que quieras usan" \
           "do las flechas.\n\nTambién acepto donaciones en ETH `0xa1B41eD75Da5d053793168D1B4F28610779E8a7c`"
    keyboard = [[InlineKeyboardButton("❤ donar %s€ ❤" % user_data["donacion"], callback_data="donate")],
                [InlineKeyboardButton("⏬", callback_data="don*LLL"),
                 InlineKeyboardButton("⬇️", callback_data="don*LL"),
                 InlineKeyboardButton("🔽", callback_data="don*L"),
                 InlineKeyboardButton("🔼", callback_data="don*G"),
                 InlineKeyboardButton("⬆️", callback_data="don*GG"),
                 InlineKeyboardButton("⏫", callback_data="don*GGG")]]
    update.message.reply_text(text,
                              reply_markup=InlineKeyboardMarkup(keyboard),
                              parse_mode=ParseMode.MARKDOWN)


# --- COMANDOS DEL BOT ---
