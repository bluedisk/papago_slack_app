from calendar import monthrange
from datetime import date

import pycountry
from annoying.fields import AutoOneToOneField
from django.db import models
from django.db.models import Sum

from django_simple_slack_app.models import SlackUser, SlackTeam
from yangpago_slack.language_codes import LANGUAGE_CODES


class ChannelsField(models.TextField):
    def from_db_value(self, value, expression, connection):
        if not value:
            return []
        return list(map(str.strip, value.split(',')))

    def to_python(self, value):
        if isinstance(value, list):
            return value

        if not value or not isinstance(value, str):
            return []

        return list(map(str.strip, value.split(',')))

    def get_prep_value(self, value):
        return ','.join(value)


class YangpagoSlackUser(models.Model):
    user = AutoOneToOneField(SlackUser, on_delete=models.CASCADE, related_name='yangpago')
    channels = ChannelsField("Activated Channel IDs", default=[], null=False, blank=True)

    def __str__(self):
        return f"{self.user.id}"


class YangpagoSlackTeam(models.Model):
    team = AutoOneToOneField(SlackTeam, on_delete=models.CASCADE, related_name='yangpago')
    plan = models.ForeignKey("YangpagoPlan", null=True, blank=True, on_delete=models.SET_NULL)

    active = models.BooleanField("Active?", default=True)

    primary_lang = models.CharField("Primary language", max_length=10, choices=LANGUAGE_CODES, default='kr')
    secondary_lang = models.CharField("Secondary language", max_length=10, choices=LANGUAGE_CODES, default='en')

    ENGINE_CHOICES = (
        ('papago', 'Papago'),
        ('google', 'Google Translation')
    )
    engine = models.CharField("Translation Engine",
                              max_length=10,
                              choices=ENGINE_CHOICES,
                              default='google')

    def __str__(self):
        return f"{self.team}"

    def monthly_usage(self):
        today = date.today().year, date.today().month
        __, ds = monthrange(*today)

        query = TranslateLog.objects. \
            filter(team=self, created_at__range=[date(*today, day=1), date(*today, day=ds)])

        return query.count(), query.aggregate(letters=Sum('length'))['letters']


class YangpagoPlan(models.Model):
    name = models.CharField("Plan Name", max_length=1024)

    updated_at = models.DateTimeField("created time", auto_now=True)
    created_at = models.DateTimeField("created time", auto_now_add=True)


class TranslateLog(models.Model):
    team = models.ForeignKey("YangpagoSlackTeam", on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey("YangpagoSlackUser", on_delete=models.SET_NULL, null=True)

    length = models.IntegerField("letter count")

    source_lang_code = models.CharField("Source language code", max_length=10)
    target_lang_code = models.CharField("Target language code", max_length=10)

    created_at = models.DateTimeField("created time", auto_now_add=True)

