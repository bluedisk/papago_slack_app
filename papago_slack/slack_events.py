from pprint import pprint

from django_simple_slack_app import slack_events
from . import papago
from .models import TranslateLog


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


@slack_events.on("message")
def message_channels(event_data):
    pprint(event_data)
    event = event_data["event"]

    # event type checking
    if "text" not in event or "bot_id" in event or "subtype" in event:
        print("no text or bot_id or it's a subtype")
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
    original_blocks = event["blocks"]

    block_dict, sanitized_text = papago.sanitize(original_blocks)
    from_lang, to_lang = papago.recognize_language(sanitized_text)
    translated = papago.custom_translate(sanitized_text)

    if not translated:
        print(from_lang, to_lang, sanitized_text)
        translated = papago.translate(sanitized_text, from_lang, to_lang)
        print(from_lang, to_lang, translated)

    translated = papago.desanitize(block_dict, translated)

    # translating
    if translated:
        new_text = "%s\n> %s" % (original_text, translated.replace("\n", "\n> "))
        event['client'].chat_update(
            channel=event["channel"], ts=event["ts"], text=new_text
        )

        TranslateLog.objects.create(
            team=user.team.papago,
            user=user.papago,
            length=len(original_text),
            from_lang=from_lang,
            to_lang=to_lang,
        )
