import telegram
from telegram import LabeledPrice, Invoice, Update , InlineKeyboardButton, InlineKeyboardMarkup, TelegramError,  InputMediaPhoto, InputMediaVideo
from telegram.ext import Updater, PreCheckoutQueryHandler, CallbackContext, CommandHandler,MessageHandler,Filters, CallbackQueryHandler, ContextTypes, JobQueue
import logging
import json
from db.db import Database
from datetime import datetime
import gpt.chatgpt as chatgpt
import os.path as pt
import threading
import time

def novelGeneratorJob():
    while True:
        novel = db.getNovelToGenerate()

        if novel != None :
            prompt = chatgpt.generateNovelPrompt(data=json.loads(novel[3]))
            try:
                novelText = chatgpt.generate(prompt=prompt)
                db.updateNovel(novelId=novel[0],text=novelText)
            except Exception as e:
                pass
                #добавить ошибку в логи куда то   
        time.sleep(60)

def novelSendJob(): 
    while True:
        novels = db.getGeneratedNovels()
        if len(novels) != 0 :
            for novel in novels:
                #fileOutput = generateFile(text=novel[2],novelId=novel[0])
                updater.bot.send_message(chat_id=novel[1],text = novel[2])
                #updater.bot.send_document(chat_id=novel[1], document=open(fileOutput, 'rb'))
                db.updateNovel(novelId=novel[0],isSend=1)
        time.sleep(3)

def start(update: Update , context : CallbackContext) :
    userId = update.message.from_user.id
    db.createUser(userId=userId)

    text = """Привет! Я бот, который умеет генерировать уникальные сказки для твоего ребенка. Ты можешь посмотреть, какие сказки я уже генерировал, ознакомиться с правилами и сгенерировать свою собственную уникальную сказку"""
    generateData = {
        "aId" : 2
    }
    keyboard = [
        [InlineKeyboardButton("Сгенерировать свою историю", callback_data=json.dumps(generateData))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id, text=text,reply_markup=reply_markup)

def precheckOut(update: Update, context: CallbackContext):
    query = update.pre_checkout_query
    if query.invoice_payload != 'Custom-Payload':
        query.answer(ok=False, error_message="Что-то пошло не так")
    else:
        query.answer(ok=True)
        
def successful_payment_callback(update: Update, context: CallbackContext):
    text = "Оплата прошла успешно! Теперь давай заполним немного информации о твоем малыше и создадим уникальную сказку!"
    data = {
        'aId' : 1
    }
    keyboard = [
        [InlineKeyboardButton("Заполнить", callback_data=json.dumps(data))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    updater.bot.send_message(chat_id=update.effective_chat.id, text = text,reply_markup=reply_markup)

def button(update: Update, context: ContextTypes) -> None:
    query = update.callback_query
    query.answer()
    data = json.loads(query.data)
    userId = update.callback_query.from_user.id
    messageId = update.callback_query.message.message_id
    #удалять предыдущее сообщение
    
    if data['aId'] == 1 :
        text = "Перейди по ссылке и заполни данные. \n Не беспокойся, мы нигде не храним эти данные и используем их только для генерации сказки"

        keyboard = [
            [InlineKeyboardButton("Сгенерировать свою историю", url=f'{formHost}?userId={userId}')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=update.effective_chat.id, text=text,reply_markup=reply_markup)
    elif data['aId'] == 2 :
        text = f"Генерация сказки платная, она стоит всего {price} рублей. Для продолжения необходимо оплатить"
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        time.sleep(2)
        context.bot.send_invoice(
            chat_id=update.effective_chat.id,
            title = title,
            description = description,
            payload = payload,
            provider_token= provider_token,
            start_parameter = start_parameter,
            currency = currency,
            prices = prices
            )
        
        
if __name__ == "__main__" :
    TOKEN = "6843058991:AAFxLD7PACbGAHSv-3RB8oeVoAfmxosh85M"
    
    db = Database()
    formHost = 'https://restify.space'
    
    #payment settings
    title = "Для продолжения нужно оплатить"
    description = "Генерация сказки искусственным интеллектом"
    payload = 'Custom-Payload'
    provider_token= "381764678:TEST:84242"
    start_parameter = 'test-payment'
    currency = 'RUB'
    price = 100
    prices = [LabeledPrice('Тестовая покупка',price*100)]
    
    
    bot = telegram.Bot(token=TOKEN)
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    button_handler = CallbackQueryHandler(button)
    dispatcher.add_handler(button_handler)
    precheckout_handler = PreCheckoutQueryHandler(precheckOut)
    dispatcher.add_handler(precheckout_handler)
    payment_handler = MessageHandler(Filters.successful_payment, successful_payment_callback)
    dispatcher.add_handler(payment_handler)

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
    updater.start_polling()
    
    #треды для фоновых джоб
    novelSendJobThread = threading.Thread(target=novelSendJob)
    novelSendJobThread.start()
    novelGeneratorJobThread = threading.Thread(target=novelGeneratorJob)
    novelGeneratorJobThread.start()

    updater.idle()