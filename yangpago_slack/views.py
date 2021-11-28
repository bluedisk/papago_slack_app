from django.conf import settings
from django.shortcuts import render


def home(request):
    return render(request, 'landing.html', {'slack_client_id': settings.SLACK_CLIENT_ID})
