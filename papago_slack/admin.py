from django.contrib import admin

from papago_slack.models import PapagoSlackUser, PapagoSlackTeam, TranslateLog


@admin.register(PapagoSlackUser)
class PapagoSlackUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'channels']
    search_fields = ['user__id', 'channels']


@admin.register(PapagoSlackTeam)
class PapagoSlackTeamAdmin(admin.ModelAdmin):
    list_display = ['team', 'plan', 'active']


@admin.register(TranslateLog)
class TranslateLogAdmin(admin.ModelAdmin):
    list_display = ['team', 'user', 'length', 'from_lang', 'to_lang', 'created_at']
