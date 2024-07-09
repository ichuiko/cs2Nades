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

def novelImageGeneratorJob() :
    while True:
        novel = db.getNovelToGenerateImage()
        if novel != None :
            novelJson = json.dumps(novel)
            novelInfo = json.loads(novel[0],strict=False)
            prompt = novelInfo['prompt']
            image = chatgpt.generateImage(prompt=prompt)
            db.updateNovel(novelId=novel[1],image=image)
            
        time.sleep(20)

def novelSendJob(): 
    while True:
        novels = db.getGeneratedNovels()
        if len(novels) != 0 :
            for novel in novels:
                try:
                    keyboard = [[InlineKeyboardButton("Читать", url=f'{formHost}/novel?userId={novel[1]}&novelId={novel[0]}')]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    updater.bot.send_message(chat_id=novel[1],text = 'Магия свершилась! Скорее читай!',reply_markup=reply_markup)
                    db.updateNovel(novelId=novel[0],isSend=1)
                except Exception as e:
                    db.updateNovel(novelId=novel[0],isSend=1)
        time.sleep(3)

def start(update: Update , context : CallbackContext) :
    userId = update.message.from_user.id
    db.createUser(userId=userId)

    text = """Привет! Я бот, который умеет генерировать уникальные сказки для твоего ребенка. Ты можешь посмотреть, какие сказки я уже генерировал, ознакомиться с правилами и сгенерировать свою собственную уникальную сказку"""
    generateData = {
        "aId" : 2
    }
    helpData = {
        "aId" : 3
    }
    myNovelsData = {
        "aId" : 4
    }
    keyboard = [
        [InlineKeyboardButton("Создать историю", callback_data=json.dumps(generateData))],
        [InlineKeyboardButton("Мои истории", callback_data=json.dumps(myNovelsData))],
        [InlineKeyboardButton("Мне нужна помощь", callback_data=json.dumps(helpData))]
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
        text = "Чтобы я смог сгенерировать для тебя сказку, заполни немного информации. \n Не беспокойся, мы нигде не храним эти данные"

        keyboard = [
            [InlineKeyboardButton("Сгенерировать свою историю", url=f'{formHost}?userId={userId}')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=update.effective_chat.id, text=text,reply_markup=reply_markup)
    elif data['aId'] == 2 :
        isFreeNovel = db.checkGeneratedNovels(userId=userId)
        if isFreeNovel == False:
            text = f"Генерация сказки платная, она стоит всего {price} рублей. Для продолжения необходимо оплатить"
            context.bot.send_message(chat_id=update.effective_chat.id, text=text)
            time.sleep(1)
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
        else:
            text = "Чтобы я смог сгенерировать для тебя сказку, заполни немного информации. \n Не беспокойся, мы нигде не храним эти данные"
            keyboard = [
                [InlineKeyboardButton("Сгенерировать свою историю", url=f'{formHost}?userId={userId}')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_id=update.effective_chat.id, text=text,reply_markup=reply_markup)
    elif data['aId'] == 3 :
        text = "К сожалению, я пока работаю в тестовом режиме и могу ошибаться. Если у вас возникли какие то проблемы, напишите @ilya_chuiko"
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    elif data['aId'] == 4 :
        novels = db.getUserNovels(userId=userId)
        
        if len(novels) == 0:
            text = "Ты пока не сгенерировал ни одной сказки. Это можно сделать в главном меню"
            context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        else:
            text = "Ты можешь прочитать сказки, созданные до этого"
            keyboard = []
            for novel in novels:
                novelJson = json.dumps(novel[2])
                novelInfo = json.loads(novel[2],strict=False)
                novelTitle = novelInfo['title']
                button = [InlineKeyboardButton(novelTitle, url=f'{formHost}/novel?userId={novel[1]}&novelId={novel[0]}')]
                keyboard.append(button)
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_id=update.effective_chat.id, text=text,reply_markup=reply_markup)
                
        
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
    novelImageGeneratorJobThread = threading.Thread(target=novelImageGeneratorJob)
    novelImageGeneratorJobThread.start()

    updater.idle()