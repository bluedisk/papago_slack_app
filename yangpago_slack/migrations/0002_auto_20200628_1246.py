# Generated by Django 3.0.4 on 2020-06-28 12:46

import annoying.fields
from django.db import migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('django_simple_slack_app', '0001_initial'),
        ('yangpago_slack', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='papagoslackteam',
            name='team',
            field=annoying.fields.AutoOneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='papago', to='django_simple_slack_app.SlackTeam'),
        ),
        migrations.AlterField(
            model_name='papagoslackuser',
            name='user',
            field=annoying.fields.AutoOneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='papago', to='django_simple_slack_app.SlackUser'),
        ),
    ]
