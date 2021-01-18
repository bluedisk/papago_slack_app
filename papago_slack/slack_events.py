import json
from pprint import pprint

from django_simple_slack_app import slack_events
from . import papago
from .models import TranslateLog

LANG_PREFIX = {
    'de': ':flag-de: ',
    'ru': ':flag-ru: ',
    'vi': ':flag-vi: ',
    'es': ':flag-es: ',
    'en': ':flag-us: ',
    'it': ':flag-it: ',
    'id': ':flag-id: ',
    'ja': ':flag-jp: ',
    'th': ':flag-th: ',
    'fr': ':flag-fr: ',
    'ko': ':flag-kr: ',
    'zh-CN': ':cn: ',
    'zh-TW': ':cn: ',
}

DEFAULT_LANG_PREFIX = ':open_mouth: '


@slack_events.on("error")
def on_event_error(error):
    print("Error caused for ", end="")
    pprint(error)


@slack_events.on("oauth")
def on_event_error(user):
    print("OAuth finished for ", end="")
    pprint(user)


@slack_events.on("app_home_opened")
def on_event_app_home_opened(user):
    print("OAuth finished for ", end="")
    pprint(user)


class SlackEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return json.JSONEncoder.default(self, obj)
        except TypeError:
            return str(obj)


@slack_events.on("message")
def message_channels(event_data):
    event = event_data["event"]
    if "previous_message" in event:
        return

    # event type checking
    if "text" not in event or "bot_id" in event:
        print("no text or has bot_id or it's a duplicated message")

        with open("failed_detail.json", "ta") as f:
            f.write(json.dumps(event_data, cls=SlackEncoder))

        return

    # auth check user
    if "client" not in event or 'user' not in event:
        print("unregistered user")
        return

    user = event['user']
    if event['channel'] not in user.papago.channels:
        print("not allowed channel for user", user.id, event['channel'])
        print("not id ", user.papago.channels)
        return

    original_text = event["text"]
    # original_blocks = event["blocks"]

    # sanitizing text
    extras, sanitized_text, letters = papago.sanitize_text(original_text)
    if len(letters) == 0:
        print("skip translate for 0 length text")
        return

    # translate
    from_lang, to_lang = papago.recognize_language(original_text)
    translated = papago.custom_translate(sanitized_text)

    if not translated:
        pprint(["TRANS FROM", from_lang, to_lang, sanitized_text])
        translated = papago.translate(sanitized_text, from_lang, to_lang)
        pprint(["TRANS TO", from_lang, to_lang, translated])

    # response
    if translated:
        translated = papago.desanitize(translated, extras).replace("\n", "\n> ")
        prefix = LANG_PREFIX.get(from_lang, DEFAULT_LANG_PREFIX)
        new_text = f'{original_text}\n> {prefix}{translated}'

        try:
            event['client'].chat_update(
                channel=event["channel"], ts=event["ts"], text=new_text
            )
        except Exception as e:
            pprint(e)

        TranslateLog.objects.create(
            team=user.team.papago,
            user=user.papago,
            length=len(original_text),
            from_lang=from_lang,
            to_lang=to_lang,
        )
