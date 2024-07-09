from yookassa import Configuration, Payment
import uuid

Configuration.account_id = '341512'
Configuration.secret_key = 'test_9GmLJpzySySUP5eHMErUS8LNe9etifeipBNEP6spHOQ'
AMOUNT = '150'

def createPayment():

    payment = Payment.create({
        "amount": {
            "value": AMOUNT,
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://www.example.com/return_url"
        },
        "capture": True,
        "description": "Заказ №1"
    }, uuid.uuid4())

    confirmationUrl = payment.confirmation.confirmation_url    

    return confirmationUrl