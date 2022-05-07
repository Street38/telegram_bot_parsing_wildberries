import telebot
from token_bot import TOKEN
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time

HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0'
}

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])                                        # Приветсвие и ожидание получения ссылки на товар
def get_url(message):
    sent = bot.reply_to(message, 'Привет, отправь ссылку для отслеживания')
    bot.register_next_step_handler(sent, get_price)

def get_price(message):                                                          # Проверка на корректность ссылки и получение цены
    message_save = message.text
    try:
        browser = webdriver.Firefox()
        browser.get(message_save)
        time.sleep(5)
        block = browser.find_element_by_class_name('same-part-kt__price-block')
        block_arguments = (block.text).split('₽')
        price = int((block_arguments[0]).replace(' ', ''))
        bot.send_message(message.chat.id, f'Цена: {price} р.')
        browser.quit()
    except Exception as e:
        bot.send_message(message.chat.id, 'Не верная ссылка, для повтора нажмите /start')
        browser.quit()
        print(e)


bot.polling()