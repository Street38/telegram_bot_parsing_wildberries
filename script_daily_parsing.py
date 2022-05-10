import telebot
from token_bot import TOKEN
from selenium import webdriver
import time
import schedule

bot = telebot.TeleBot(TOKEN)

def daily_parsing():
    with open('links.txt', 'r+') as file:
        for i in file:
            list = i.split()
            browser = webdriver.Firefox()
            browser.get(list[1])
            time.sleep(5)
            block = browser.find_element_by_class_name('same-part-kt__price-block')
            block_arguments = (block.text).split('₽')
            price = (block_arguments[0]).replace(' ', '')
            if int(price) <= int(list[2]):
                bot.send_message(list[2], f'<b>Пссс, цена снизилась.\n'
                                          f'Сейчас цена: {price}р.🎊\nУспей купить {list[1]}</b>',
                                            parse_mode="HTML")
                browser.quit()
            browser.quit()

schedule.every().day.at('18:48').do(daily_parsing)
while True:
    schedule.run_pending()
    time.sleep(1)