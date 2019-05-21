# coding=utf-8

import logging, json, time, re
from telegram.ext import Updater, InlineQueryHandler, ChosenInlineResultHandler, CallbackQueryHandler,\
    CommandHandler, MessageHandler, Filters, PreCheckoutQueryHandler
from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent, InlineKeyboardButton,\
    InlineKeyboardMarkup, LabeledPrice
from bot_tokens import BOT_TOKEN, PAYMENT_PROVIDER_TOKEN
from uuid import uuid4

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
g_search = re.compile("_g")
dk_search = re.compile("_dk")
ng_search = re.compile("_ng")
DEBUG = False


class FriendList:

    def __init__(self, text, id, from_user_id, list=None, **kargs):

        self.text = text
        self.id = id
        self.from_user_id = from_user_id
        self.date = kargs.get("date", time.time())
        self.list = []

        if list:
            for bot_user in list:
                self.list.append(BotUser(json=bot_user))

    def text_message_and_keyboard(self):

        going, dont_know, not_going = self.get_three_lists()
        g_count = dk_count = ng_count = 0

        msg = "*%s*" % self.text

        if going:
            msg += "\n\n*Dicen que vienen:*"
            while g_count < 5 and going:
                user = going.pop()
                msg += "\n%s" % user.full_name
                g_count += 1
            if g_count == 5 and going:
                msg += "\n*+%s*" % len(going)
            g_count = g_count + len(going)

        if dont_know:
            msg += "\n\n*Dicen que puede que vengan:*"
            while dk_count < 5 and dont_know:
                user = dont_know.pop()
                msg += "\n%s" % user.full_name
                dk_count += 1
            if dk_count == 5 and dont_know:
                msg += "\n*+%s*" % len(dont_know)
            dk_count = dk_count + len(dont_know)

        if not_going:
            msg += "\n\n*Dicen que no vienen:*"
            while ng_count < 5 and not_going:
                user = not_going.pop()
                msg += "\n%s" % user.full_name
                ng_count += 1
            if ng_count == 5 and not_going:
                msg += "\n*+%s*" % len(not_going)
            ng_count = ng_count + len(not_going)

        return msg, self.make_keyboard(g_count, dk_count, ng_count)

    def make_keyboard(self, g_count, dk_count, ng_count):

        keyboard = [[InlineKeyboardButton("Yo voy", callback_data="si*%s" % self.id),
                     InlineKeyboardButton("Puede", callback_data="puede*%s" % self.id),
                     InlineKeyboardButton("Yo no voy", callback_data="no*%s" % self.id)],
                    [InlineKeyboardButton("CERRAR ✋️", callback_data="close*%s" % self.id),
                     InlineKeyboardButton("Reenviar", switch_inline_query="id*%s" % self.id)]]

        if g_count > 5 or dk_count > 5 or ng_count > 5:

            if not DEBUG:
                url = "t.me/QuienVienebot?start=%s" % self.id
            else:
                url = "t.me/vetutestbot?start=%s" % self.id

            keyboard.insert(1, [InlineKeyboardButton("(%s)" % g_count, url=url + "_g"),
                                InlineKeyboardButton("(%s)" % dk_count, url=url + "_dk"),
                                InlineKeyboardButton("(%s)" % ng_count, url=url + "_ng")])

        return InlineKeyboardMarkup(keyboard)

    def add_user(self, usuario):

        user_id = usuario.t_id
        already_in = -1
        for user in self.list:
            if user.t_id == user_id:
                already_in = self.list.index(user)

        if already_in >= 0:
            if self.list[already_in].position == usuario.position:
                self.list.pop(already_in)
            else:
                self.list.pop(already_in)
                self.list.append(usuario)
        else:
            self.list.append(usuario)

        self.date = time.time()

    def to_json(self):

        u_list = []
        for u in self.list:
            u_list.append(u.to_json())

        j_son = {"text":self.text,
                 "id":self.id,
                 "from_user_id":self.from_user_id,
                 "date":self.date,
                 "list":u_list}

        return j_son

    def get_going(self):

        list = []

        for persona in self.list:

            if persona.position == "si":
                list.append(persona)

        return list

    def get_dont_know(self):

        list = []

        for persona in self.list:

            if persona.position == "puede":
                list.append(persona)

        return list

    def get_not_going(self):

        list = []

        for persona in self.list:

            if persona.position == "no":
                list.append(persona)

        return list

    def get_three_lists(self):

        list_going = []
        list_dont_know = []
        list_not_going = []

        for persona in self.list:

            if persona.position == "si":
                list_going.append(persona)
            elif persona.position == "puede":
                list_dont_know.append(persona)
            else:
                list_not_going.append(persona)

        return list_going, list_dont_know, list_not_going


class BotUser:

    def __init__(self, json=None, t_id=None, full_name=None, username=None, position=None):

        if json:

            self.t_id = json["t_id"]
            self.full_name = json["full_name"]
            self.username = json["username"]
            self.position = json["position"]

        else:

            self.t_id = t_id
            self.full_name = full_name
            self.username = username
            self.position = position

    def to_json(self):
        j_son = {"t_id":self.t_id,
                 "full_name":self.full_name,
                 "username":self.username,
                 "position":self.position}

        return j_son


def make_buttons(uuid):

    return InlineKeyboardMarkup([[InlineKeyboardButton("Yo voy", callback_data="si*%s" % uuid),
                                  InlineKeyboardButton("Puede", callback_data="puede*%s" % uuid),
                                  InlineKeyboardButton("Yo no voy", callback_data="no*%s" % uuid)],
                                 [InlineKeyboardButton("Ajustes ⚙️️", callback_data="close*%s" % uuid),
                                  InlineKeyboardButton("Reenviar", switch_inline_query="id*%s" % uuid)]])


with open("bot_list_list.json") as f:
    l_l = json.load(f)
    friend_list_list = []
    for f_list in l_l:
        friend_list_list.append(FriendList(text=f_list["text"],
                                           id=f_list["id"],
                                           list=f_list["list"],
                                           from_user_id=f_list["from_user_id"],
                                           date=f_list["date"]))

del f, l_l


def search_lists_by_user(t_user_id):
    global friend_list_list
    n = 0
    while n < len(friend_list_list):
        if friend_list_list[n].date < time.time() - 604800:
            friend_list_list.pop(n)
        else:
            n += 1

    matches = []
    for list in friend_list_list:
        if list.from_user_id == t_user_id:
            matches.append(list)

    return matches


def search_list_by_id(list_id):
    global friend_list_list

    for list in friend_list_list:
        if list.id == list_id:
            return list
    return None


# BOT FUNCTIONS
def stopBot(updater):
    logger.info("Apagando bot...")
    updater.stop()
    logger.info("Bot apagado")


def get_id_from_start_command(args):

    assert len(args) == 1, "Hay más de un argumento"

    if g_search.search(args[0]):
        return args[0].replace("_g", ""), "g"
    elif dk_search.search(args[0]):
        return args[0].replace("_dk", ""), "dk"
    elif ng_search.search(args[0]):
        return args[0].replace("_ng", ""), "ng"
    else:
        raise


def start_command(bot, update, args, user_data):
    if args:

        if args[0] != "donacion":
            try:
                list_id, orden = get_id_from_start_command(args)
                lista = search_list_by_id(list_id)

                msg = "*%s*\n\n" % lista.text

                if orden == "g":
                    lista_personas = lista.get_going()
                    if lista_personas:
                        msg += "*Dicen que vienen:*"
                    else:
                        msg += "*Nadie ha dicho que viene D:*"
                elif orden == "dk":
                    lista_personas = lista.get_dont_know()
                    if lista_personas:
                        msg += "*Dicen que puede que vengan:*"
                    else:
                        msg += "*Nadie ha dicho que puede que venga*"
                else:
                    lista_personas = lista.get_not_going()
                    if lista_personas:
                        msg += "*Dicen que no viene:*"
                    else:
                        msg += "*Nadie ha dicho que no viene :D*"

                if lista_personas:
                    for persona in lista_personas:
                        msg += "\n%s" % persona.full_name

                update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
                return
            finally:
                pass
        else:
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

            return

    msg = "¡Hola! Bienvenido a la versión 0.2 de @QuienVienebot!\n\nEste bot es un bot _inline_, esto quiere decir " \
          "que para usarme no hace falta ni que uses este chat! Para empezar escribe en cualquier chat *@QuienViene" \
          "bot ¿Quien viene a casa de Marta?*, por ejemplo.\n¡Gracias por usarme!"

    update.message.reply_text(text=msg,
                              parse_mode=ParseMode.MARKDOWN)


def delete_list(id=None, index=None):
    pass


def empty_query(bot, update):

    user_matches = search_lists_by_user(update.inline_query.from_user.id)
    results = []

    if user_matches:
        for list_match in user_matches:

            message, keyboard = list_match.text_message_and_keyboard()

            results.append(InlineQueryResultArticle(id=list_match.id,
                                                    title=list_match.text,
                                                    description="Pulsa para enviar esta cita ya creada",
                                                    reply_markup=keyboard,
                                                    input_message_content=InputTextMessageContent(message_text=message,
                                                                                                  parse_mode=ParseMode.MARKDOWN,
                                                                                                  disable_web_page_preview=True)))

    else:
        msg_text = "*No tienes ninguna cita creada*\n" \
                   "Para crear una cita escribe en cualquier chat: _@QuienVienebot ¿Quién viene a...?_"

        results = [InlineQueryResultArticle(id="sin_cita",
                                            title="No tienes ninguna cita creada",
                                            description="sigue escribiendo para crear una",
                                            input_message_content=InputTextMessageContent(message_text=msg_text,
                                                                                          parse_mode=ParseMode.MARKDOWN,
                                                                                          disable_web_page_preview=True))]

    update.inline_query.answer(results,
                               is_personal=True,
                               cache_time=0,
                               switch_pm_text="Se aceptan donaciones ❤️",
                               switch_pm_parameter="donacion")


def full_query(bot, update):
    query_split = update.inline_query.query.split("*")

    if query_split[0] == "id":
        list_id = query_split[1]
        lista = search_list_by_id(list_id)

        if lista:
            message, keyboard = lista.text_message_and_keyboard()

            results = [InlineQueryResultArticle(id=list_id,
                                                title=lista.text,
                                                description="Pulsa para enviar esta lista ya creada",
                                                reply_markup=keyboard,
                                                input_message_content=InputTextMessageContent(
                                                    message_text=message,
                                                    parse_mode=ParseMode.MARKDOWN,
                                                    disable_web_page_preview=True))]
        else:

            msg_text = "*La lista que solicitas no se encuentra*\nPuede que haya sido cerrada o que haya caducado. Pa" \
                       "ra crear una nueva escribe en cualquier chat @QuienVienebot."

            results = [InlineQueryResultArticle(id="sin_cita",
                                                title="No existe ninguna cita con esa ID",
                                                description="puede que haya sido cerrada o que haya caducado, crea una nueva",
                                                input_message_content=InputTextMessageContent(message_text=msg_text,
                                                                                              parse_mode=ParseMode.MARKDOWN,
                                                                                              disable_web_page_preview=True))]
    else:
        list_id = uuid4()

        results = [InlineQueryResultArticle(id=list_id,
                                            title=update.inline_query.query,
                                            description="Pulsa para enviar",
                                            reply_markup=make_buttons(list_id),
                                            input_message_content=InputTextMessageContent(message_text="*%s*" % update.inline_query.query,
                                                                                          parse_mode=ParseMode.MARKDOWN,
                                                                                          disable_web_page_preview=True))]
    update.inline_query.answer(results,
                               is_personal=True,
                               cache_time=0,
                               switch_pm_text="Se aceptan donaciones ❤️",
                               switch_pm_parameter="donacion")


def inline_query(bot, update):

    if update.inline_query.query:
        full_query(bot, update)
    else:
        empty_query(bot, update)


def chosen_result(bot, update):

    if update.chosen_inline_result.query and "id*" not in update.chosen_inline_result.query:
        global friend_list_list

        friend_list_list.append(FriendList(text=update.chosen_inline_result.query,
                                           id=update.chosen_inline_result.result_id,
                                           from_user_id=update.chosen_inline_result.from_user.id))


def callback_query_exception(bot, update):
    update.callback_query.answer("Proximamente...")


def add_me_to_list(bot, update):
    # Función para responder a un botón pulsado de voy / no voy etc...

    telegram_user = update.callback_query.from_user
    if telegram_user.last_name:
        full_name = telegram_user.first_name + " " + telegram_user.last_name
    else:
        full_name = telegram_user.first_name
    position = update.callback_query.data.split("*")[0]
    list_id = update.callback_query.data.split("*")[1]
    list = search_list_by_id(list_id)
    if list:
        usuario = BotUser(t_id=telegram_user.id,
                          full_name=full_name,
                          username=telegram_user.username,
                          position=position)
        list.add_user(usuario)

        message, keyboard = list.text_message_and_keyboard()

        bot.edit_message_text(text=message,
                              parse_mode=ParseMode.MARKDOWN,
                              disable_web_page_preview=True,
                              reply_markup=keyboard,
                              inline_message_id=update.callback_query.inline_message_id)
        update.callback_query.answer("okay 👍")
    else:
        update.callback_query.answer("⚠️ Parece que esa lista no existe", show_alert=True)
        bot.edit_message_reply_markup(inline_message_id=update.callback_query.inline_message_id,
                                      reply_markup=(InlineKeyboardMarkup([[]])))


def close_list(bot, update):
    global friend_list_list

    list_id = update.callback_query.data.split("*")[1]
    n = None
    for n in range(len(friend_list_list)):
        if friend_list_list[n].id == list_id:
            break
        else:
            n = None

    if n is not None:
        if friend_list_list[n].from_user_id == update.callback_query.from_user.id:
            friend_list_list.pop(n)
            update.callback_query.answer("okay, lista cerrada 👍")
            bot.edit_message_reply_markup(inline_message_id=update.callback_query.inline_message_id,
                                          reply_markup=(InlineKeyboardMarkup([[]])))
        else:
            update.callback_query.answer("⚠️ No has creado esta lista")
    else:
        update.callback_query.answer("⚠️ parece que esa lista no existe")
        bot.edit_message_reply_markup(inline_message_id=update.callback_query.inline_message_id,
                                      reply_markup=(InlineKeyboardMarkup([[]])))


def change_donation_quantity(bot, update, user_data):

    if "donacion" not in user_data:
        user_data["donacion"] = 5

    s = update.callback_query.data.split("*")
    change = 5 ** (s[1].count("G") - 1) if "G" in s[1] else -(5 ** (s[1].count("L") - 1))
    user_data["donacion"] += change
    if user_data["donacion"] < 1:
        user_data["donacion"] = 1

    keyboard = [[InlineKeyboardButton("❤ donar %s€ ❤" % user_data["donacion"], callback_data="donate")],
                [InlineKeyboardButton("⏬", callback_data="don*LLL"),
                 InlineKeyboardButton("⬇️", callback_data="don*LL"),
                 InlineKeyboardButton("🔽", callback_data="don*L"),
                 InlineKeyboardButton("🔼", callback_data="don*G"),
                 InlineKeyboardButton("⬆️", callback_data="don*GG"),
                 InlineKeyboardButton("⏫", callback_data="don*GGG")]]

    update.effective_message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))
    update.callback_query.answer()


def donate(bot, update, user_data):

    title = "Donación"
    description = "Gracias por aportar a este proyecto. Usa el botón pagar para proceder al pago."
    prices = [LabeledPrice("Donación", user_data["donacion"] * 100)]

    bot.send_invoice(chat_id=update.effective_chat.id,
                     title=title,
                     description=description,
                     payload="donacion_completada",
                     provider_token=PAYMENT_PROVIDER_TOKEN,
                     start_parameter="donacion",
                     currency="EUR",
                     prices=prices)
    update.effective_message.edit_reply_markup(reply_markup=InlineKeyboardMarkup([[]]))


def aprove_transaction(bot, update):
    query = update.pre_checkout_query
    # check the payload, is this from your bot?
    if query.invoice_payload != 'donacion_completada':
        # answer False pre_checkout_query
        bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=False,
                                      error_message="Algo ha fallado, vuelve a intentarlo por favor.")
    else:
        bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=True)


def completed_donation(bot, update):
    update.effective_message.reply_text("Muchisimas gracias por donar!! ❤️❤️❤️")
    bot.send_message(254234845, "%s ha donado!" % update.effective_chat.id)


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


def main():
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(InlineQueryHandler(inline_query))
    dispatcher.add_handler(ChosenInlineResultHandler(chosen_result))
    dispatcher.add_handler(CallbackQueryHandler(add_me_to_list, pattern="(si\*)|(puede\*)|(no\*)"))
    dispatcher.add_handler(CallbackQueryHandler(close_list, pattern="close\*"))
    dispatcher.add_handler(CallbackQueryHandler(change_donation_quantity, pattern=r"don\*", pass_user_data=True))
    dispatcher.add_handler(CallbackQueryHandler(donate, pattern=r"donate$", pass_user_data=True))
    dispatcher.add_handler(CallbackQueryHandler(callback_query_exception))
    dispatcher.add_handler(CommandHandler("start", start_command, pass_args=True, pass_user_data=True))
    dispatcher.add_handler(MessageHandler(filters=Filters.successful_payment, callback=completed_donation))
    dispatcher.add_handler(PreCheckoutQueryHandler(aprove_transaction))

    dispatcher.add_error_handler(error)

    updater.start_polling()

    # CONSOLA
    while True:
        inp = raw_input("")
        if inp:
            input_c = inp.split()[0]
            args = inp.split()[1:]
            strig = ""
            for e in args:
                strig = strig + " " + e

            if input_c == "stop":
                stopBot(updater)
                break

            else:
                print "Comando desconocido"


if __name__ == '__main__':
    main()


with open("bot_list_list.json", "w") as f:
    l_l = []
    for f_list in friend_list_list:
        l_l.append(f_list.to_json())
    json.dump(l_l, f, indent=2)
