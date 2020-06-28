from calendar import monthrange
from datetime import date

from annoying.fields import AutoOneToOneField
from django.db import models
from django.db.models import Sum

from django_simple_slack_app.models import SlackUser, SlackTeam


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


class PapagoSlackUser(models.Model):
    user = AutoOneToOneField(SlackUser, on_delete=models.CASCADE, related_name='papago')
    channels = ChannelsField("활성화된 채널들", default=[], null=False, blank=True)


class PapagoSlackTeam(models.Model):
    team = AutoOneToOneField(SlackTeam, on_delete=models.CASCADE, related_name='papago')
    plan = models.ForeignKey("PapagoPlan", null=True, blank=True, on_delete=models.SET_NULL)

    active = models.BooleanField("Active?", default=True)

    def monthly_usage(self):
        today = date.today().year, date.today().month
        __, ds = monthrange(*today)

        query = TranslateLog.objects. \
            filter(team=self, created_at__range=[date(*today, day=1), date(*today, day=ds)])

        return query.count(), query.aggregate(letters=Sum('length'))['letters']


class PapagoPlan(models.Model):
    name = models.CharField("Plan Name", max_length=1024)

    updated_at = models.DateTimeField("created time", auto_now=True)
    created_at = models.DateTimeField("created time", auto_now_add=True)


class TranslateLog(models.Model):
    team = models.ForeignKey("PapagoSlackTeam", on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey("PapagoSlackUser", on_delete=models.SET_NULL, null=True)

    length = models.IntegerField("letter count")

    from_lang = models.CharField("From language code", max_length=10)
    to_lang = models.CharField("To language code", max_length=10)

    created_at = models.DateTimeField("created time", auto_now_add=True)
