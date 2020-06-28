from pprint import pprint

import hgtk
import requests

from django_simple_slack_app import slack_events, slack_commands
from . import papago


@slack_commands.on("error")
def on_command_error(error):
    pprint(error)


@slack_commands.on("/papago")
def papago_command(event_data):
    if not event_data['text']:
        requests.post(event_data['response_url'], json={
            "text": "You can turn on/off Papago for you in this channel using `/papago on`, `/papago off`.",
            "response_type": "ephemeral"
        })


@slack_commands.on("/papago.usage")
def papago_command_team(event_data):
    user = event_data['user']

    count, letters = user.team.papago.monthly_usage()

    requests.post(event_data['response_url'], json={
        "text": f"Your team use {count} requests for {letters} letters in this month",
        "response_type": "ephemeral"
    })


@slack_commands.on("/papago.on")
def papago_command_on(event_data):

    if 'user' not in event_data:
        return


    user = event_data['user']
    user.papago.channels.append(event_data['channel_id'])
    user.papago.save()

    requests.post(event_data['response_url'], json={
        "text": "Papago will translate on this channel for you!",
        "response_type": "ephemeral"
    })

    print("PAPAGO ON", event_data['user'].id, "in", event_data['channel_id'])


@slack_commands.on("/papago.off")
def papago_command_off(event_data):
    if 'user' not in event_data:
        return


    user = event_data['user']
    user.papago.channels.remove(event_data['channel_id'])
    user.papago.save()

    requests.post(event_data['response_url'], json={
        "text": "Papago translation is off!",
        "response_type": "ephemeral"
    })

    print("PAPAGO OFF", event_data['user'].user, "in", event_data['channel_id'])