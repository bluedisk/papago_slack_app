from django.conf import settings
from django.http import HttpResponse


def home(request):
    return HttpResponse(f"Hi! there? I'm Papago Slack App #{settings.SLACK_CLIENT_ID}<p/>" + 
                        f"<a href=\"https://slack.com/oauth/v2/authorize?client_id={settings.SLACK_CLIENT_ID}&scope=channels:history,chat:write,commands&user_scope=chat:write\">" +
                        '<img alt="Add to Slack" height="40" width="139" src="https://platform.slack-edge.com/img/add_to_slack.png" srcset="https://platform.slack-edge.com/img/add_to_slack.png 1x, https://platform.slack-edge.com/img/add_to_slack@2x.png 2x"></a>')
