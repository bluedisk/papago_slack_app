import requests
from django_simple_slack_app import slack_commands
from functools import wraps
from pprint import pprint

from papago_slack.font import make_art


def authorized(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        event_data = args[0]

        if 'user' not in event_data:
            send_response(event_data,
                          "You need to _authorize_ *Papago* to use auto translation! :smirk: \n" +
                          "Visit <https://papago.eggpang.net/slack/install|Authorize Page> to accept Papago :rocket:\n\n"
                          "파파고를 이용하시려면 *파파고*를 _권한 인증_ 해주셔야 합니다! :smirk: \n" +
                          "인증하시려면 <https://papago.eggpang.net/slack/install|인증 페이지>를 방문해주세요! :rocket:")
            return

        return func(*args, **kwargs)

    return wrapper


def send_response(event_data, text, response_type="ephemeral"):
    requests.post(event_data['response_url'], json={
        "text": text,
        "response_type": response_type
    })


@slack_commands.on("error")
@authorized
def on_command_error(error):
    pprint(error)


@slack_commands.on("/papago")
@authorized
def papago_command(event_data):
    if event_data['text']:
        return

    status = "ON" if event_data['channel_id'] in event_data['user'].papago.channels else "OFF"
    status_kr = "켜져" if event_data['channel_id'] in event_data['user'].papago.channels else "꺼져"

    send_response(event_data,
                  "You can turn on/off Papago for you in this channel using `/papago on`, `/papago off`.\n" +
                  f"Papago is turned *{status}* in this channel for you\n\n" +
                  "`/papago on`과 `/papago off` 명령으로 이 채널의 파파고 동작를 개인 설정을 켜고 끌 수 있습니다..\n" +
                  f"현재 이 채널에서 파파고 동작은 *{status_kr}*있습니다.\n")


@slack_commands.on("/papago.usage")
@authorized
def papago_command_team(event_data):
    user = event_data['user']

    count, letters = user.team.papago.monthly_usage()
    send_response(event_data,
                  f"Your team use {count} requests for {letters} letters in this month\n" +
                  f"이 팀의 이번달 파파고 사용 횟수는 {count}번이고 총 {letters}글자를 번역 했습니다.")


@slack_commands.on("/papago.on")
@authorized
def papago_command_on(event_data):
    if 'user' not in event_data:
        return

    user = event_data['user']
    user.papago.channels.append(event_data['channel_id'])
    user.papago.save()

    send_response(event_data,
                  "Papago will translate on this channel for you!\n" +
                  "이제부터 이 채널에 포스팅 하시는 내용을 파파고가 번역 하겠습니다!")
    print("PAPAGO ON", event_data['user'].id, "in", event_data['channel_id'])


@slack_commands.on("/papago.off")
@authorized
def papago_command_off(event_data):
    if 'user' not in event_data:
        return

    user = event_data['user']
    user.papago.channels.remove(event_data['channel_id'])
    user.papago.save()

    send_response(event_data, "Papago translation is off!\n" +
                  "이 채널에서 파파고 번역을 정지합니다! 안되잖아... 안되...")
    print("PAPAGO OFF", event_data['user'].id, "in", event_data['channel_id'])


@slack_commands.on("/papago.saysorry")
@authorized
def papago_saysorry(event_data):
    if 'user' not in event_data:
        return

    send_response(event_data, "죄송합니다... 앞으로 제대로 하겠습니다... :sob:", response_type="in_channel")


@slack_commands.on("/papago.blaming")
@authorized
def papago_blaming(event_data):
    if 'user' not in event_data:
        return

    send_response(event_data, "아.. 이런 시부렁 못해먹겠네... :expressionless:", response_type="in_channel")


@slack_commands.on("/papago.pepe")
@authorized
def papago_blaming(event_data):
    if 'user' not in event_data:
        return

    pepe_art = make_art(event_data['text'][5:])

    send_response(event_data, pepe_art, response_type="in_channel")
