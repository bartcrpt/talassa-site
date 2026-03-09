import logging
import os
import requests
from dotenv import load_dotenv

# Загрузите переменные окружения из файла .env
load_dotenv()

# # Загрузка токена и ID группы из .env
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')


# TELEGRAM_GROUP_ID = os.getenv('TELEGRAM_GROUP_ID')


# TODO: после подготовки сайта - переделать ручку на отправку смс через шлюз смс
def send_tg_message(message, tg_group_id):
    """
    Отправляет сообщение в заданную группу Telegram.

    :param message: Текст сообщения для отправки.
    """
    telegram_api_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": tg_group_id,
        "text": message
    }

    try:
        response = requests.post(telegram_api_url, json=payload)
        if response.status_code == 200:
            logging.info("Сообщение отправлено успешно")
        else:
            logging.error(f"Ошибка при отправке сообщения: {response.status_code}, {response.text}")
            #next line is for debugging
            # logging.error(message)
    except Exception as e:
        logging.error(f"Ошибка при выполнении HTTP-запроса: {e}")


# send_sms_message(phone, text_for_sms, api_key=api_key, sms_api_gateway=sms_api_gateway)
def send_sms_message(phone, message, sms_api_gateway):
    payload = message

    header = {
        "Content-Type": "application/json",
        # "Authorization": api_key
    }

    try:
        response = requests.post(sms_api_gateway, json=payload, headers=header)
        if response.status_code == 200:
            logging.info("Сообщение смс отправлено успешно")
        else:
            logging.error(f"Ошибка при отправке смс сообщения: {response.status_code}, {response.text}")
            # next line is for debugging
            # logging.error(message)
    except Exception as e:
        logging.error(f"Ошибка при выполнении HTTP-запроса: {e}")