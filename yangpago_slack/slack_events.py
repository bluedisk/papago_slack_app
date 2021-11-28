import json
from pprint import pprint

from django_simple_slack_app import slack_events
from yangpago_slack import translator
from yangpago_slack.translator import DEFAULT_PRIMARY_CODE, DEFAULT_SECONDARY_CODE
from .language_codes import LANGUAGE_PREFIX_EMOJI
from .models import TranslateLog

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
def message_channels(event_data, user):
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
    if not user:
        print("unregistered user")
        return

    if event['channel'] not in user.yangpago.channels:
        print("not allowed channel for user", user.id, event['channel'])
        print("not id ", user.yangpago.channels)
        return

    original_text = event["text"]
    # original_blocks = event["blocks"]

    # sanitizing text
    extras, sanitized_text, letters = translator.sanitize_text(original_text)
    if len(letters) == 0:
        print("skip translate for 0 length text")
        return

    # translate
    # translate_module = translator.papago
    translate_module = translator.google

    # language selection
    source_lang_code, confidence = translate_module.recognize_language(original_text)
    print(f"Detected language {source_lang_code} ({confidence})")

    if source_lang_code != DEFAULT_PRIMARY_CODE:
        target_lang_code = DEFAULT_PRIMARY_CODE
    else:
        target_lang_code = DEFAULT_SECONDARY_CODE

    # custom translate
    translated = translator.custom_translate(sanitized_text)

    # API transalte
    if not translated:
        pprint(["TRANS FROM", source_lang_code, target_lang_code, sanitized_text])
        translated = translate_module.translate(sanitized_text, source_lang_code, target_lang_code)
        pprint(["TRANS TO", source_lang_code, target_lang_code, translated])

    # response
    if translated:
        translated = translator.desanitize(translated, extras).replace("\n", "\n> ")
        prefix = LANGUAGE_PREFIX_EMOJI.get(source_lang_code, DEFAULT_LANG_PREFIX)
        new_text = f'{original_text}\n> {prefix}{translated}'

        try:
            user.chat_update(ts=event["ts"], text=new_text)
        except Exception as e:
            pprint(e)

        TranslateLog.objects.create(
            team=user.team.yangpago,
            user=user.yangpago,
            length=len(original_text),
            source_lang_code=source_lang_code,
            target_lang_code=target_lang_code,
        )
