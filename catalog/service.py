from twilio.rest import Client as TwilioClient

TWILIO_SID = "YOUR_TWILIO_SID"
TWILIO_AUTH_TOKEN = "YOUR_TWILIO_AUTH_TOKEN"
WHATSAPP_FROM = "whatsapp:+14155238886"  # Номер Twilio

def send_whatsapp_message(phone: str, message: str):
    client = TwilioClient(TWILIO_SID, TWILIO_AUTH_TOKEN)
    phone = f"whatsapp:{phone}"  # Формат для Twilio
    response = client.messages.create(
        from_=WHATSAPP_FROM,
        to=phone,
        body=message
    )
    print(f"✅ WhatsApp сообщение отправлено: {response.sid}")


import requests

TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"


def send_telegram_message(chat_id: str, message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        print("✅ Сообщение отправлено в Telegram")
    else:
        print(f"❌ Ошибка Telegram: {response.text}")



from telethon import TelegramClient

API_ID = "YOUR_TELEGRAM_API_ID"
API_HASH = "YOUR_TELEGRAM_API_HASH"
PHONE_NUMBER = "+7XXXXXXXXXX"  # Номер продавца

client = TelegramClient("seller_session", API_ID, API_HASH)

async def send_message(phone, message):
    await client.start(PHONE_NUMBER)  # Авторизация
    user = await client.get_entity(phone)  # Получение ID по номеру телефона
    await client.send_message(user, message)  # Отправка сообщения
    print(f"✅ Сообщение отправлено пользователю {phone}")

with client:
    client.loop.run_until_complete(send_message("+7XXXXXXXXXX", "Здравствуйте! Ваш заказ оформлен."))