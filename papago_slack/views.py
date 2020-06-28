from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse


def home(request):
    return HttpResponse(f"Hi! there? I'm Papago Slack App #{settings.SLACK_CLIENT_ID}<p/>" + 
                        f"<a href=\"{reverse('install')}\">" +
                        '<img alt="Add to Slack" height="40" width="139" src="https://platform.slack-edge.com/img/add_to_slack.png" srcset="https://platform.slack-edge.com/img/add_to_slack.png 1x, https://platform.slack-edge.com/img/add_to_slack@2x.png 2x"></a>')
