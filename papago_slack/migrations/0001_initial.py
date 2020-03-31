# Generated by Django 3.0.4 on 2020-03-31 14:22

from django.db import migrations, models
import papago_slack.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PapagoSlackUser',
            fields=[
                ('user', models.CharField(max_length=1024, primary_key=True, serialize=False, verbose_name='Slack User ID')),
                ('token', models.CharField(max_length=1024, unique=True, verbose_name='User Access Token')),
                ('team_id', models.CharField(max_length=1024, null=True, verbose_name='Team ID')),
                ('team_name', models.CharField(max_length=1024, null=True, verbose_name='Team Name')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created time')),
                ('enabled_channels', papago_slack.models.ChannelsField(blank=True, default=[], verbose_name='활성화된 채널들')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
