import json
import os
import re
from pprint import pprint
from typing import AnyStr, Match, List

import fasttext
import requests

model = fasttext.load_model('lid.176.bin')

LANG_CODE = {
    '독일어': 'de',
    '러시아어': 'ru',
    '베트남어': 'vi',
    '스페인어': 'es',
    '영어': 'en',
    '이탈리아어': 'it',
    '인도네시아어': 'id',
    '일본어': 'ja',
    '중국어 간체': 'zh-CN',
    '중국어 번체': 'zh-TW',
    '태국어': 'th',
    '프랑스어': 'fr',
    '한국어': 'ko'
}

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

DEFAULT_PRIMARY_CODE = 'ko'
DEFAULT_SECONDARY_CODE = 'en'

PAPAGO_ENDPOINT = 'https://naveropenapi.apigw.ntruss.com/nmt/v1/translation'

EXTRA_FIELD_NAME_FOR_TYPE = {
    'text': ('text', '{}'),
    'user': ('user_id', '<@{}>'),
    'channel': ('channel_id', '<#{}>'),
    'link': ('url', '<{}>'),
    'emoji': ('name', ':{}:'),
    'broadcast': ('range', '<!{}>')
}

CUSTOM_DICTIONARY = {
    'GC': 'Genius Confirmed! (but not that genius like YOGI)',
    'BYT': '치아관리를 시작하도록 하십시오',
    'ND': '나도~~!!!!',
    'GD': '편의점 가자!',
    '파파고': '왜!',
}


def translate(text, from_lang, to_lang):
    payload = {
        'source': from_lang,
        'target': to_lang,
        'text': text,
        'honorific': True
    }

    headers = {
        'X-NCP-APIGW-API-KEY-ID': os.getenv("PAPAGO_CONFIG_KEY"),
        'X-NCP-APIGW-API-KEY': os.getenv("PAPAGO_CONFIG_SECRET")
    }

    res = requests.post(PAPAGO_ENDPOINT, data=payload, headers=headers)

    if res.status_code != 200:
        print(f"[PAPAGO] error on '{text}' : {res.text} ")
        pprint(res)
        return None

    return json.loads(res.content)['message']['result']['translatedText']


def sanitize_block(blocks: dict) -> (List[str], str):
    text = ""
    extras = []
    extra_idx = 0

    for block in blocks:
        for elements in block['elements']:
            for element in elements['elements']:
                etype = element['type']

                if etype == 'text':
                    text += element['text']
                elif etype in EXTRA_FIELD_NAME_FOR_TYPE:
                    text += f"[{extra_idx + 1}]"
                    field_name, _ = EXTRA_FIELD_NAME_FOR_TYPE[etype]
                    extras.append((etype, element[field_name]))
                    extra_idx += 1
                else:
                    with open("exceptions.txt", "a") as f:
                        f.write(json.dumps(element))
                        f.write("\n\n")
                    pass

    return extras, text


def sanitize_text(text: str) -> (List[str], str):
    extras = []

    def bracketize(match):
        extras.append(match.group())
        return f"[{len(extras)}]"

    element_re = re.compile(r'(<(([!@#](subteam\^)?(channel|here|[A-Z0-9]+))|'
                            r'(https?://[\w_.?&=%/-]+))(|.+?)?>)|(:\w+?:)|(`.+?`)')

    return extras, element_re.sub(bracketize, text), extract_letters(element_re.sub("", text))


def extract_letters(text):
    return re.sub(r'[ !@#$%^&*()<>?,./;\':"\[\]\\{}|\-_+=`~\n\xa00-9]', "", text)


def recognize_language(text: str) -> (str, str):
    # language checking

    from_codes, _ = model.predict(text, k=2)
    candi_major, candi_minor = [code[-2:] for code in from_codes]
    print(f"I] from code is {candi_major}, {candi_minor} : {text}")
    from_code = candi_major

    if from_code == 'zh':
        from_code = 'zh-TN'

    if from_code == DEFAULT_PRIMARY_CODE:
        to_code = DEFAULT_SECONDARY_CODE
    else:
        to_code = DEFAULT_PRIMARY_CODE

        if from_code not in TRANS_TABLE.keys():
            print(f"E] wrong origin language {candi_major}, fallback to {candi_minor}")
            from_code = candi_minor

            if from_code not in TRANS_TABLE.keys():
                print(f"E] wrong origin language {candi_major}, changed to {DEFAULT_SECONDARY_CODE}")
                from_code = DEFAULT_SECONDARY_CODE

    return from_code, to_code


def custom_translate(sanitized_text: str) -> str:
    if sanitized_text in CUSTOM_DICTIONARY:
        return CUSTOM_DICTIONARY[sanitized_text]

    return ""


def desanitize(translated: str, extras=None, elements: List[str] = None) -> str:
    r = re.compile(r'\[([0-9]{1,2})]')

    if not extras and elements:
        extras = []
        for etype, value in elements:
            _, value_format = EXTRA_FIELD_NAME_FOR_TYPE[etype]
            extras.append(value_format.format(value))

    def replace_dict(match: Match[AnyStr]) -> AnyStr:
        return extras[int(match.groups()[0]) - 1]

    return r.sub(replace_dict, translated)
