import json
import re
from typing import List, Match, AnyStr

DEFAULT_PRIMARY_CODE = 'ko'
DEFAULT_SECONDARY_CODE = 'en'

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
    '파파고': '저는 양파고에요',
    '양파고': '왜요?',
    '양파고!': '왜!!'
}


def extract_letters(text):
    return re.sub(r'[ !@#$%^&*()<>?,./;\':"\[\]\\{}|\-_+=`~\n\xa00-9]', "", text)


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
