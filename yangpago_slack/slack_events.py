import json
from pprint import pprint

from django_simple_slack_app import slack_events
from django_simple_slack_app.models import SlackUser, SlackTeam

from yangpago_slack import translator
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
def message_channels(event_data, user: SlackUser):
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

    team = user.team.yangpago
    user = user.yangpago

    if event['channel'] not in user.channels:
        print("not allowed channel for user", user.id, event['channel'])
        print("not id ", user.channels)
        return

    original_text = event["text"]

    sanitizing = False
    translation_engine = team.engine

    # translator
    translate_module = translator.get_translator(translation_engine)

    # # sanitizing text
    if sanitizing:
        extras, sanitized_text, letters = translator.sanitize_text(original_text)
        if len(letters) == 0:
            print("skip translate for 0 length text")
            return
    else:
        sanitized_text = original_text
        extras = []

    # language selection
    source_lang_code, confidence = translate_module.recognize_language(original_text)
    print(f"Detected language {source_lang_code} ({confidence})")

    primary_lang = user.primary_lang or team.primary_lang
    secondary_lang = user.secondary_lang or team.secondary_lang

    if source_lang_code != primary_lang:
        target_lang_code = primary_lang
    else:
        target_lang_code = secondary_lang

    # custom translate
    translated = translator.custom_translate(original_text)

    # API transalte
    if not translated:
        pprint(["TRANS FROM", source_lang_code, target_lang_code, sanitized_text])
        translated = translate_module.translate(sanitized_text, source_lang_code, target_lang_code)
        pprint(["TRANS TO", source_lang_code, target_lang_code, translated])

    # response
    if translated:
        if sanitizing:
            translated = translator.desanitize(translated, extras).replace("\n", "\n> ")

        prefix = LANGUAGE_PREFIX_EMOJI.get(source_lang_code, DEFAULT_LANG_PREFIX)
        new_text = f'{original_text}\n> {prefix}{translated}'

        try:
            user.slack.chat_update(ts=event["ts"], text=new_text)
        except Exception as e:
            pprint(e)

        TranslateLog.objects.create(
            team=team,
            user=user,
            length=len(original_text),
            source_lang_code=source_lang_code,
            target_lang_code=target_lang_code,
        )
