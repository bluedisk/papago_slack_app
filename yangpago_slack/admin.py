import json
from json import JSONDecodeError

from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from yangpago_slack.models import YangpagoSlackUser, YangpagoSlackTeam, TranslateLog


@admin.register(YangpagoSlackUser)
class YangpagoSlackUserAdmin(admin.ModelAdmin):
    list_display = ['info', 'channels']
    search_fields = ['user__id', 'channels']

    @admin.display
    def info(self, obj):
        try:
            info = json.loads(obj.slack.info)

            output = ""
            if 'profile' in info and 'image_32' in info['profile']:
                output += format_html("<img src='{}' valign='middle' />&nbsp;&nbsp;&nbsp;", info['profile']['image_32'])
            if 'real_name' in info:
                output += f"{info['real_name']} - "

            output += str(obj.slack.id)

            return mark_safe(output)

        except (JSONDecodeError, TypeError):
            pass

        return str(obj.slack)


@admin.register(YangpagoSlackTeam)
class YangpagoSlackTeamAdmin(admin.ModelAdmin):
    list_display = ['info', 'home', 'plan', 'active']

    @admin.display
    def info(self, obj):
        try:
            info = json.loads(obj.slack.info)

            output = ""
            if 'icon' in info and 'image_34' in info['icon']:
                output += format_html("<img src='{}' valign='middle' />&nbsp;&nbsp;&nbsp;", info['icon']['image_34'])
            if 'name' in info:
                output += f"{info['name']} - "

            output += str(obj.slack.id)

            return mark_safe(output)

        except (JSONDecodeError, TypeError):
            pass

        return str(obj.slack)

    @admin.display
    def home(self, obj):
        try:
            info = json.loads(obj.slack.info)

            if 'public_url' in info:
                return mark_safe(
                    format_html("<a href={}>{}</a>", info['public_url'], info['public_url']))

        except (JSONDecodeError, TypeError):
            pass

        return ""


@admin.register(TranslateLog)
class TranslateLogAdmin(admin.ModelAdmin):
    list_display = ['team', 'user', 'length', 'source_lang_code', 'target_lang_code', 'created_at']
