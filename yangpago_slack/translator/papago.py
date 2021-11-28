import os
from pprint import pprint

import requests

basepath = os.path.dirname(__file__)
# model = fasttext.load_model(os.path.join(basepath, 'lid.176.bin'))

TRANS_TABLE = {
    'de': ['ko'],
    'en': ['ja', 'zh-CN', 'zh-TW', 'fr', 'ko'],
    'es': ['ko'],
    'fr': ['en', 'ko'],
    'id': ['ko'],
    'it': ['ko'],
    'ja': ['en', 'zh-CN', 'zh-TW', 'ko'],
    'ko': ['de', 'ru', 'vi', 'es', 'en', 'it', 'id', 'ja', 'zh-CN', 'zh-TW', 'th', 'fr'],
    'ru': ['ko'],
    'th': ['ko'],
    'vi': ['ko'],
    'zh-CN': ['en', 'ja', 'zh-TW', 'ko'],
    'zh-TW': ['en', 'ja', 'zh-CN', 'ko'],
}

PAPAGO_ENDPOINT = 'https://naveropenapi.apigw.ntruss.com/nmt/v1/translation'
PAPAGO_DETECT_ENDPOINT = 'https://openapi.naver.com/v1/papago/detectLangs'

PAPAGO_AUTH_HEADER = {
    'X-NCP-APIGW-API-KEY-ID': os.getenv("PAPAGO_CONFIG_KEY"),
    'X-NCP-APIGW-API-KEY': os.getenv("PAPAGO_CONFIG_SECRET")
}


def translate(text, source_lang_code, target_lang_code):
    payload = {
        'source': source_lang_code,
        'target': target_lang_code,
        'text': text,
        'honorific': True
    }

    result = requests.post(PAPAGO_ENDPOINT, json=payload, headers=PAPAGO_AUTH_HEADER)

    if result.status_code != 200:
        print(f"[PAPAGO] error on '{text}' : {result.text} ")
        pprint(result)
        return None

    return result.json()['message']['result']['translatedText']


def recognize_language(text: str) -> (str, int):
    # language checking
    result = requests.post(PAPAGO_DETECT_ENDPOINT, json={
        'query': text,
    }, headers=PAPAGO_AUTH_HEADER)

    if result.status_code != 200:
        print(f"[PAPAGO] error on '{text}' : {result.text} ")
        pprint(result)
        return None

    language_code = result.json()['message']['result']['langCode']

    return language_code, 1.0
