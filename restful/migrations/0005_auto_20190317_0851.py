# Generated by Django 2.1.7 on 2019-03-17 08:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('restful', '0004_remove_game_score'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='history',
            name='player',
        ),
        migrations.DeleteModel(
            name='History',
        ),
    ]