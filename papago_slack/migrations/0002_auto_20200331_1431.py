# Generated by Django 3.0.4 on 2020-03-31 14:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('papago_slack', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='papagoslackuser',
            old_name='enabled_channels',
            new_name='channels',
        ),
    ]
