import telebot
from token_bot import TOKEN
from selenium import webdriver
import time
from telebot import types


bot = telebot.TeleBot(TOKEN)

LIST_REPLY = []

@bot.message_handler(commands=['start'])                            # Обрабатываем /start, выводим клавиатуру.
def keyboard(message):
    startboard = types.ReplyKeyboardMarkup(resize_keyboard= True, row_width= 3, one_time_keyboard=True)
    create = types.KeyboardButton(text='Добавить товар🎁')
    edit = types.KeyboardButton(text='Редактировать мои отслеживания🛠')
    delete = types.KeyboardButton(text='Удалить все отслеживания🗑')
    #delete_all = types.KeyboardButton(text='Выборочное удаление🗑')
    startboard.add(create, edit, delete)
    bot.send_message(message.chat.id, 'Привет, я бот который помогает сделать покупки на www.wildberries.ru в нужный '
                                      'момент🎁, выбери действие', reply_markup=startboard)


@bot.message_handler(func= lambda m: m.text == 'Добавить товар🎁')   # Обрабатываем нажатие кнопки 'Добавить товар' и запрашиваем на него ссылку.
def get_url(message):
    LIST_REPLY.clear()
    try:
        sent = bot.reply_to(message, 'Отправь мне ссылку на товар и я тебе напишу когда цена снизится')
        bot.register_next_step_handler(sent, request_link)
    except Exception as e:
        print(f'Ошибка в функции get_url {e}')

def request_link(message):                                          # Обрабатываем отправленную пользователем ссылку / запрашиваем стоимость товара при которой уведомить пользователя/ Формируем список данными от пользователя 'LIST_REPLY'
    try:
        artikel = [i for i in (message.text).split('/') if i.isdigit()]
        link = f'https://www.wildberries.ru/catalog/{artikel[0]}/detail.aspx'
        LIST_REPLY.append(str(message.chat.id) + '-' + link)
        LIST_REPLY.append(link)
        LIST_REPLY.append(message.chat.id)
        sent = bot.reply_to(message, 'Укажите цену ниже которой будет отправленно уведомление')
        bot.register_next_step_handler(sent, processing_link)
    except Exception as e:
        bot.send_message(message.chat.id, 'Не верная ссылка, для повторного ввода нажмите /start')

def processing_link(message):                                       # Открываем страницу, парсим стоимость товара (Использую selenium, т.к если использовать request, то через несколько запросов блокируют).
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
                                              f'\nУведомление сработает при цене {LIST_REPLY[3]}р. и ниже')
        browser.quit()
    except Exception as e:
        bot.send_message(message.chat.id, 'Не верная ссылка, либо такого товара не существует. '
                                          'Для повторного ввода нажмите /start')
        browser.quit()
        print(e)

def save_data():                                                    # Создаем файл со ссылками пользователей на товары / Проверяем на уникальность / Добавляем в список если условия выполнены
    with open('links.txt', 'r+') as list:
        if LIST_REPLY[1] not in list.read():
            print(*LIST_REPLY, file=list)
            return True
        else:
            bot.send_message(LIST_REPLY[2], 'Данный товар уже добавлен в список отслеживания.\n'
                                            'Выбрать другой: /start\n'
                                            'Отредактировать мои отслеживания: /edit')

@bot.message_handler(func= lambda m: m.text == 'Удалить все отслеживания🗑')     #
def dell_all(message):
    count = get_data(message.from_user.id)
    if count == 0:
        bot.send_message(message.chat.id, 'У вас не было товаров в отслеживании')
    else:
        bot.send_message(message.chat.id, f'Всего отменено {count} отслеживаний')

def get_data(id):
    with open('links.txt', 'r+') as list:
        lines = [i.strip() for i in list.readlines()]

    with open('links.txt', 'w') as list2:
        count = 0
        for i in lines:
            if str(id) not in i:
                print(i, file=list2)
            else:
                count += 1
    return count

@bot.message_handler(func= lambda m: m.text == 'Редактировать мои отслеживания🛠')
def edit_list(message):
    list_product = []
    count = 1
    with open('links.txt', 'r+') as list:
        for i in list:
            if str(message.chat.id) in i:
                value = (str(count) + ' ' + i).split()
                bot.send_message(message.chat.id, f'№{value[0]} - товар {value[2]}, цена при которой будет '
                                                  f'выполнено уведомление {value[4]} р.')
                list_product.append(value)
                count += 1
        if count == 1:
            bot.send_message(message.chat.id, 'У вас нет отслеживаний')
        else:
            sent = bot.reply_to(message, 'Укажите номер отслеживания который нужно отредактировать')
            bot.register_next_step_handler(sent, processing_message, list_product)

def processing_message(message, *args):
    tracking_number = message.text
    for i in args:
        for j in i:
            if j[0] == str(tracking_number):
                board = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
                edit2 = types.KeyboardButton(text='Редактировать цену уведомления🎁')
                dell = types.KeyboardButton(text='Удалить товар🛠')
                board.add(edit2, dell)
                bot.send_message(message.chat.id, f'Ссылка на товар:{j[2]}\nЦена при которой сработает уведомление: {j[4]} р.'
                                                  f'\nВыберете действие', reply_markup=board)

    @bot.message_handler(func=lambda m: m.text == 'Удалить товар🛠')
    def dell_product(message):
        with open('links.txt', 'r+') as list:
            lines = [i.strip() for i in list.readlines()]
        with open('links.txt', 'w') as list2:
            for i in lines:
                if j[1] not in i:
                    print(i, file=list2)

    @bot.message_handler(func=lambda m: m.text == 'Редактировать цену уведомления🎁')
    def edit_price_level_notification(message):
        sent = bot.reply_to(message, f'Сейчас цена товара при которой произойдет уведомления указана: {j[4]} р., '
                                          f'укажите новую стоимость товара ')
        bot.register_next_step_handler(sent, edit_level_price, j)

def edit_level_price(message, j):
    level_price = message.text
    with open('links.txt', 'r+') as list:
        lines = [i.strip() for i in list.readlines()]
    with open('links.txt', 'w') as list2:
        for i in lines:
            if j[1] in i:
                j[4] = level_price
                print(*j[1:], file=list2)
                bot.send_message(message.chat.id, f'Цена успешно изменена')
                break
            else:
                print(i, file=list2)







bot.polling()