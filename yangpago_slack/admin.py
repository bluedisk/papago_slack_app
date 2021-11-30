import json

from django.contrib import admin

from yangpago_slack.models import YangpagoSlackUser, YangpagoSlackTeam, TranslateLog


@admin.register(YangpagoSlackUser)
class YangpagoSlackUserAdmin(admin.ModelAdmin):
    list_display = ['name', 'channels']
    search_fields = ['user__id', 'channels']

    @admin.display
    def name(self, obj):
        if obj.slack.info:
            print(obj.slack.info)
            info = json.loads(obj.slack.info)
            return f"{info.get('real_name', 'no info')}({obj.slack})"

        return str(obj.slack)


@admin.register(YangpagoSlackTeam)
class YangpagoSlackTeamAdmin(admin.ModelAdmin):
    list_display = ['slack', 'plan', 'active']


@admin.register(TranslateLog)
class TranslateLogAdmin(admin.ModelAdmin):
    list_display = ['team', 'user', 'length', 'source_lang_code', 'target_lang_code', 'created_at']
