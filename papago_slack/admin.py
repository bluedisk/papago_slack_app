from django.contrib import admin

from papago_slack.models import PapagoSlackUser, PapagoSlackTeam, TranslateLog


@admin.register(PapagoSlackUser)
class PapagoSlackUserAdmin(admin.ModelAdmin):
    pass


@admin.register(PapagoSlackTeam)
class PapagoSlackTeamAdmin(admin.ModelAdmin):
    pass


@admin.register(TranslateLog)
class TranslateLogAdmin(admin.ModelAdmin):
    pass
