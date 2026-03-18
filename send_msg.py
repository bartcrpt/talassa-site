import logging
import os

import requests
from dotenv import load_dotenv

# Загрузите переменные окружения из файла .env
load_dotenv()

# # Загрузка токена и ID группы из .env
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_PROXY_URL = os.getenv('TELEGRAM_PROXY_URL')


# TELEGRAM_GROUP_ID = os.getenv('TELEGRAM_GROUP_ID')


# TODO: после подготовки сайта - переделать ручку на отправку смс через шлюз смс
def send_tg_message(message, tg_group_id, timeout=10):
    """
    Отправляет сообщение в заданную группу Telegram.

    :param message: Текст сообщения для отправки.
    """
    if not TELEGRAM_TOKEN:
        logging.warning("TELEGRAM_TOKEN is not configured, skipping Telegram notification")
        return False

    if not tg_group_id:
        logging.warning("Telegram chat id is not configured, skipping Telegram notification")
        return False

    telegram_api_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": tg_group_id,
        "text": message
    }
    proxies = None
    if TELEGRAM_PROXY_URL:
        proxies = {
            "http": TELEGRAM_PROXY_URL,
            "https": TELEGRAM_PROXY_URL,
        }

    try:
        response = requests.post(
            telegram_api_url,
            json=payload,
            timeout=timeout,
            proxies=proxies,
        )
        if response.status_code == 200:
            logging.info("Сообщение отправлено успешно")
            return True
        else:
            logging.error(f"Ошибка при отправке сообщения: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        logging.error(f"Ошибка при выполнении HTTP-запроса: {e}")
        return False


# send_sms_message(phone, text_for_sms, api_key=api_key, sms_api_gateway=sms_api_gateway)
def send_sms_message(phone, message, sms_api_gateway, timeout=10):
    if not sms_api_gateway:
        logging.warning("SMS_API_GATEWAY is not configured, skipping SMS notification")
        return False

    payload = message

    header = {
        "Content-Type": "application/json",
        # "Authorization": api_key
    }

    try:
        response = requests.post(sms_api_gateway, json=payload, headers=header, timeout=timeout)
        if response.status_code == 200:
            logging.info("Сообщение смс отправлено успешно")
            return True
        else:
            logging.error(f"Ошибка при отправке смс сообщения: {response.status_code}, {response.text}")
            # next line is for debugging
            # logging.error(message)
            return False
    except Exception as e:
        logging.error(f"Ошибка при выполнении HTTP-запроса: {e}")
        return False
