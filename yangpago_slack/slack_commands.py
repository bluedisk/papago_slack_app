from functools import wraps
from pprint import pprint

from django_simple_slack_app import slack_commands
from yangpago_slack.font import make_art


def authorized(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = args[1]
        response = args[2]

        if not user:
            if response:
                response.ephemeral(
                    "You need to _authorize_ *Papago* to use auto translation! :smirk: \n" +
                    "Visit <https://yangpago.com/slack/install|Authorize Page> to accept Papago :rocket:\n\n"
                    "양파고를 이용하시려면 *양파고*를 _권한 인증_ 해주셔야 합니다! :smirk: \n" +
                    "인증하시려면 <https://yangpago.com/slack/install|인증 페이지>를 방문해주세요! :rocket:")
            return

        return func(*args, **kwargs)

    return wrapper


@slack_commands.on("error")
@authorized
def on_command_error(error):
    pprint(error)


@slack_commands.on("/papago")
@slack_commands.on("/papago.usage")
@slack_commands.on("/papago.on")
@slack_commands.on("/papago.off")
@slack_commands.on("/papago.saysorry")
@slack_commands.on("/papago.blaming")
@slack_commands.on("/papago.pepe")
def yangpago_help(event_data, user, response):
    response.ephemeral(":sob: My name is changed, friend! Please use `/yangpago` instead of `/papago`")


@slack_commands.on("/yangpago")
@authorized
def yangpago_command(event_data, user, response):
    if event_data['text']:
        return

    status = "ON" if event_data['channel_id'] in event_data['user'].yangpago.channels else "OFF"
    status_kr = "켜져" if event_data['channel_id'] in event_data['user'].yangpago.channels else "꺼져"

    response.ephemeral(
        "You can turn on/off Yangpago for you in this channel using `/yangpago on`, `/yangpago off`.\n" +
        f"Yangpago is turned *{status}* in this channel for you\n\n" +
        "`/yangpago on`과 `/yangpago off` 명령으로 이 채널의 양파고 동작를 개인 설정을 켜고 끌 수 있습니다..\n" +
        f"현재 이 채널에서 양파고 동작은 *{status_kr}*있습니다.\n")


@slack_commands.on("/yangpago.usage")
@authorized
def yangpago_command_team(event_data, user, response):
    count, letters = user.team.yangpago.monthly_usage()
    response.ephemeral(
        f"Your team use {count} requests for {letters} letters in this month\n" +
        f"이 팀의 이번달 양파고 사용 횟수는 {count}번이고 총 {letters}글자를 번역 했습니다.")


@slack_commands.on("/yangpago.on")
@authorized
def yangpago_command_on(event_data, user, response):
    user = event_data['user']
    user.yangpago.channels.append(event_data['channel_id'])
    user.yangpago.save()

    response.ephemeral(
        "Yangpago will translate on this channel for you!\n" +
        "이제부터 이 채널에 포스팅 하시는 내용을 양파고가 번역 하겠습니다!")
    print("YANGPAGO ON", event_data['user'].id, "in", event_data['channel_id'])


@slack_commands.on("/yangpago.off")
@authorized
def yangpago_command_off(event_data, user, response):
    user.yangpago.channels.remove(event_data['channel_id'])
    user.yangpago.save()

    response.ephemeral("Yangpago translation is off!\n" +
                       "이 채널에서 양파고 번역을 정지합니다! 안되잖아... 안되...")

    print("YANGPAGO OFF", event_data['user'].id, "in", event_data['channel_id'])


@slack_commands.on("/yangpago.saysorry")
@authorized
def yangpago_saysorry(event_data, user, response):
    response.ephemeral("죄송합니다... 앞으로 제대로 하겠습니다... :sob:", response_type="in_channel")


@slack_commands.on("/yangpago.blaming")
@authorized
def yangpago_blaming(event_data, user, response):
    response.ephemeral("아.. 이런 시부렁 못해먹겠네... :expressionless:", response_type="in_channel")


@slack_commands.on("/yangpago.pepe")
@authorized
def yangpago_blaming(event_data, user, response):
    pepe_art = make_art(event_data['text'][5:])

    response.ephemeral(pepe_art, response_type="in_channel")
