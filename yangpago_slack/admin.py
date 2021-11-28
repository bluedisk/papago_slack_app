from django.contrib import admin

from yangpago_slack.models import YangpagoSlackUser, YangpagoSlackTeam, TranslateLog


@admin.register(YangpagoSlackUser)
class YangpagoSlackUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'channels']
    search_fields = ['user__id', 'channels']


@admin.register(YangpagoSlackTeam)
class YangpagoSlackTeamAdmin(admin.ModelAdmin):
    list_display = ['team', 'plan', 'active']


@admin.register(TranslateLog)
class TranslateLogAdmin(admin.ModelAdmin):
    list_display = ['team', 'user', 'length', 'source_lang_code', 'target_lang_code', 'created_at']
