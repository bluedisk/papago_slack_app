from pprint import pprint

import html
import requests
from google.cloud.translate_v3 import TranslationServiceClient
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file('keys/yangpago-361fc7901229.json')
translation_clinet = TranslationServiceClient(credentials=credentials)

GOOGLE_ENDPOINT = 'https://translation.googleapis.com/language/translate/v2'
PARENT_PATH = f'projects/{credentials.project_id}'


def recognize_language(text: str) -> (str, int):
    result = translation_clinet.detect_language(request={'content': text, 'parent': PARENT_PATH})
    return result.languages[0].language_code, result.languages[0].confidence


def translate(text, source_lang_code, target_lang_code):
    result = translation_clinet.translate_text(
        request={
            'contents': [text],
            'parent': PARENT_PATH,
            'source_language_code': source_lang_code, # optional
            'target_language_code': target_lang_code
        })

    return html.unescape(result.translations[0].translated_text)
