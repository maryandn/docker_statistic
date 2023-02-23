import requests

from django.conf import settings


def send_message_to_tg(text):
    url = f'https://api.telegram.org/{settings.TOKEN_TG}/sendMessage'
    chat_id = settings.CHAT_ID_TG
    requests.post(url, data={'chat_id': chat_id, 'text': text})
