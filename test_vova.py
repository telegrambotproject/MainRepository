import telebot

telebot.apihelper.proxy = {'https': 'https://51.77.210.229:3128'}
bot = telebot.TeleBot('852946157:AAEv1Cg91DaHgGeEgbAKDRvDmm3EGY55nSI')


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Hello there! Wanna see some movies?')
    custom_keyboard = [['Yes, please'],
                       ['Hell no!']]
    reply_markup = telebot.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=message.chat.id,
                     text='',
                     reply_markup=reply_markup)


bot.polling(none_stop=False, interval=0, timeout=20)
