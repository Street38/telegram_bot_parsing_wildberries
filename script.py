import telebot
from token_bot import TOKEN
from selenium import webdriver
import time
import schedule

bot = telebot.TeleBot(TOKEN)

LIST_REPLY = []

@bot.message_handler(commands=['start'])
def get_url(message):
    LIST_REPLY.clear()
    sent = bot.reply_to(message, 'Привет, я бот который помогает сделать покупки в нужный момент;), '
                                 'отправь мне ссылку на товар')
    bot.register_next_step_handler(sent, request_link)

def request_link(message):
    try:
        artikel = [i for i in (message.text).split('/') if i.isdigit()]
        link = f'https://www.wildberries.ru/catalog/{artikel[0]}/detail.aspx'
        LIST_REPLY.append(str(message.chat.id) + '-' + link)
        LIST_REPLY.append(link)
        LIST_REPLY.append(message.chat.id)
        sent = bot.reply_to(message, 'Укажите цену ниже которой будет отправленно уведомление')
        bot.register_next_step_handler(sent, request_update_interval)
    except Exception as e:
        bot.send_message(message.chat.id, 'Не верная ссылка, для повторного ввода нажмите /start')

def request_update_interval(message):
    LIST_REPLY.append(message.text)
    bot.send_message(message.chat.id, 'Проверка запущенна, пожалуйста, ожидайте ответа, это займет до 15 секунд')
    try:
        browser = webdriver.Firefox()
        browser.get(LIST_REPLY[1])
        time.sleep(5)
        block = browser.find_element_by_class_name('same-part-kt__price-block')
        block_arguments = (block.text).split('₽')
        price = (block_arguments[0]).replace(' ', '')
        LIST_REPLY.append(price)
        if save_data():
            bot.send_message(message.chat.id, f'Отслеживание успешно запущено.\nТекущая цена: {price} р.'
                                              f'\nУведомление сработает при цене {LIST_REPLY[2]}р. и ниже')
        browser.quit()
    except Exception as e:
        bot.send_message(message.chat.id, 'Не верная ссылка, либо такого товара не существует. '
                                          'Для повторного ввода нажмите /start')
        browser.quit()
        print(e)

def save_data():
    with open('links.txt', 'r+') as list:
        if LIST_REPLY[1] not in list.read():
            print(*LIST_REPLY, file=list)
            return True
        else:
            bot.send_message(LIST_REPLY[2], 'Данный товар уже добавлен в список отслеживания.\n'
                                            'Выбрать другой: /start\n'
                                            'Отредактировать мои отслеживания: /edit')




bot.polling()