import re
from pprint import pprint

import hgtk

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
        return

    # auth check user
    if "client" not in event or 'user' not in event:
        return

    user = event['user']
    if event['channel'] not in user.papago.channels:
        return

    text = event["text"]
    checking_test = re.sub(r"[ !@#$%^&*()<>?,./;':\"\[\]\\\{\}|\-_+=`~]", "", text)

    # language checking
    if hgtk.checker.is_latin1(checking_test):
        print("Translate %s characters to Korean" % len(text))
        from_lang = "en"
        to_lang = "ko"
    else:
        print("Translate %s characters to English" % len(text))
        from_lang = "ko"
        to_lang = "en"

    translated = papago.translate(text, from_lang, to_lang)

    # translating
    if translated:
        new_text = "%s\n> %s" % (text, translated.replace("\n", "\n> "))
        event['client'].chat_update(
            channel=event["channel"], ts=event["ts"], text=new_text
        )

        TranslateLog.objects.create(
            team=user.team.papago,
            user=user.papago,
            length=len(text),
            from_lang=from_lang,
            to_lang=to_lang,
        )
