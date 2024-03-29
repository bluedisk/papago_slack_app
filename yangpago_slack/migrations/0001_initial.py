# Generated by Django 3.0.4 on 2020-06-28 12:38

from django.db import migrations, models
import django.db.models.deletion
import yangpago_slack.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('django_simple_slack_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PapagoPlan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1024, verbose_name='Plan Name')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='created time')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created time')),
            ],
        ),
        migrations.CreateModel(
            name='PapagoSlackTeam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True, verbose_name='Active?')),
                ('plan', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='yangpago_slack.PapagoPlan')),
                ('team', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='papago', to='django_simple_slack_app.SlackTeam')),
            ],
        ),
        migrations.CreateModel(
            name='PapagoSlackUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channels', yangpago_slack.models.ChannelsField(blank=True, default=[], verbose_name='활성화된 채널들')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='papago', to='django_simple_slack_app.SlackUser')),
            ],
        ),
        migrations.CreateModel(
            name='TranslateLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('length', models.IntegerField(verbose_name='letter count')),
                ('from_lang', models.CharField(max_length=10, verbose_name='From language code')),
                ('to_lang', models.CharField(max_length=10, verbose_name='To language code')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created time')),
                ('team', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='yangpago_slack.PapagoSlackTeam')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='yangpago_slack.PapagoSlackUser')),
            ],
        ),
    ]
