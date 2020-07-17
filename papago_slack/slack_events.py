import hgtk
import re
from django_simple_slack_app import slack_events
from pprint import pprint

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
    translated = translate(text) if text != 'GC' else 'Genius Confirmed! (but not that genius like YOGI)'

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


def translate(text):
    # language checking
    latin1_count = 0
    hangul_count = 0
    hanja_count = 0
    etc_count = 0

    cheking_text = re.sub(r"<!\w+\^[\w\d]+\|(@\w+)>", "", text)
    cheking_text = re.sub(r"[ !@#$%^&*()<>?,./;':\"\[\]\\\{\}|\-_+=`~\n]", "", cheking_text)

    for c in cheking_text:
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
        print("Translate %s characters to Korean" % len(text))
        from_lang = "en"
        to_lang = "ko"
    else:
        print("Translate %s characters to English" % len(text))
        from_lang = "ko"
        to_lang = "en"

    return papago.translate(text, from_lang, to_lang)