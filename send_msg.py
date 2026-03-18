import asyncio
import logging
import os

import requests
from dotenv import load_dotenv
from telethon import TelegramClient, connection

# Загрузите переменные окружения из файла .env
load_dotenv()

# # Загрузка токена и ID группы из .env
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_PROXY_URL = os.getenv('TELEGRAM_PROXY_URL')
TELEGRAM_API_ID = os.getenv('TELEGRAM_API_ID')
TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH')
TELEGRAM_MTPROXY_HOST = os.getenv('TELEGRAM_MTPROXY_HOST')
TELEGRAM_MTPROXY_PORT = os.getenv('TELEGRAM_MTPROXY_PORT')
TELEGRAM_MTPROXY_SECRET = os.getenv('TELEGRAM_MTPROXY_SECRET')
TELEGRAM_SESSION_NAME = os.getenv('TELEGRAM_SESSION_NAME', 'telegram_bot')


# TELEGRAM_GROUP_ID = os.getenv('TELEGRAM_GROUP_ID')


def _normalize_mtproto_proxy():
    if not TELEGRAM_MTPROXY_HOST:
        return None

    try:
        proxy_port = int(TELEGRAM_MTPROXY_PORT or '0')
    except ValueError:
        logging.error("Invalid TELEGRAM_MTPROXY_PORT value: %s", TELEGRAM_MTPROXY_PORT)
        return None

    if proxy_port <= 0:
        logging.error("TELEGRAM_MTPROXY_PORT must be a positive integer")
        return None

    proxy_secret = (TELEGRAM_MTPROXY_SECRET or '00000000000000000000000000000000').strip()
    return (TELEGRAM_MTPROXY_HOST, proxy_port, proxy_secret)


async def _send_tg_message_mtproto(message, tg_group_id):
    proxy = _normalize_mtproto_proxy()
    client_kwargs = {
        'session': TELEGRAM_SESSION_NAME,
        'api_id': int(TELEGRAM_API_ID),
        'api_hash': TELEGRAM_API_HASH,
    }

    if proxy:
        client_kwargs['connection'] = connection.ConnectionTcpMTProxyRandomizedIntermediate
        client_kwargs['proxy'] = proxy

    client = TelegramClient(**client_kwargs)
    try:
        await client.start(bot_token=TELEGRAM_TOKEN)
        await client.send_message(int(tg_group_id), message)
        return True
    finally:
        await client.disconnect()


def _can_use_mtproto():
    return bool(TELEGRAM_TOKEN and TELEGRAM_API_ID and TELEGRAM_API_HASH)


def _send_tg_message_bot_api(message, tg_group_id, timeout):
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

    response = requests.post(
        telegram_api_url,
        json=payload,
        timeout=timeout,
        proxies=proxies,
    )
    if response.status_code == 200:
        logging.info("Сообщение отправлено успешно через Telegram Bot API")
        return True

    logging.error(f"Ошибка при отправке сообщения: {response.status_code}, {response.text}")
    return False


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

    try:
        if _can_use_mtproto():
            logging.info("Sending Telegram message via MTProto")
            return asyncio.run(_send_tg_message_mtproto(message, tg_group_id))

        logging.warning(
            "TELEGRAM_API_ID/API_HASH are not configured, falling back to Telegram Bot API"
        )
        return _send_tg_message_bot_api(message, tg_group_id, timeout)
    except Exception as e:
        logging.error(f"Ошибка при отправке Telegram сообщения: {e}")
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
