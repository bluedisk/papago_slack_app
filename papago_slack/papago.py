import json
import os
import re
from pprint import pprint
from typing import AnyStr, Match, List

import hgtk
import requests

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
        print("[PAPAGO] error on ", text)
        pprint(res)
        return None

    return json.loads(res.content)['message']['result']['translatedText']


def sanitize(blocks: dict) -> (List[str], str):
    text = ""
    extra_list = []
    extra_idx = 0

    for block in blocks:
        for elements in block['elements']:
            for element in elements['elements']:
                etype = element['type']

                if etype == 'text':
                    text += element['text']
                elif etype in EXTRA_FIELD_NAME_FOR_TYPE:
                    text += f"[{extra_idx+1}]"
                    field_name, _ = EXTRA_FIELD_NAME_FOR_TYPE[etype]
                    extra_list.append((etype, element[field_name]))
                    extra_idx += 1
                else:
                    with open("exceptions.txt", "a") as f:
                        f.write(json.dumps(element))
                        f.write("\n\n")
                    pass

    return extra_list, text


def recognize_language(text: str) -> (str, str):
    # language checking
    latin1_count = 0
    hangul_count = 0
    hanja_count = 0
    etc_count = 0

    text = re.sub(r"[ !@#$%^&*()<>?,./;':\"\[\]\\\{\}|\-_+=`~\n\xa0]", "", text)

    for c in text:
        if hgtk.checker.is_latin1(c):
            latin1_count += 1
        elif hgtk.checker.is_hangul(c):
            hangul_count += 1
        elif hgtk.checker.is_hanja(c):
            hanja_count += 1
        else:
            etc_count += 1

    letter_count = latin1_count + hangul_count + hanja_count
    latin_rate = latin1_count / letter_count
    hangul_rate = hangul_count / letter_count

    if latin_rate >= hangul_rate:
        from_lang = "en"
        to_lang = "ko"
    else:
        from_lang = "ko"
        to_lang = "en"

    return from_lang, to_lang


def custom_translate(sanitized_text: str) -> str:
    if sanitized_text in CUSTOM_DICTIONARY:
        return CUSTOM_DICTIONARY[sanitized_text]

    return ""


def desanitize(extra_list: List[str], translated: str) -> str:
    r = re.compile(r'\[([0-9]{1,2})]')

    def replace_dict(match: Match[AnyStr]) -> AnyStr:
        extra_idx = int(match.groups()[0])
        etype, value = extra_list[extra_idx-1]
        _, value_format = EXTRA_FIELD_NAME_FOR_TYPE[etype]

        return value_format.format(value)

    return r.sub(replace_dict, translated)
