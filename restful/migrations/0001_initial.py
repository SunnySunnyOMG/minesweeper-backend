# Generated by Django 2.1.7 on 2019-03-17 01:15

import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('size_x', models.PositiveSmallIntegerField(default=8, validators=[django.core.validators.MaxValueValidator(40), django.core.validators.MinValueValidator(1)])),
                ('size_y', models.PositiveSmallIntegerField(default=8, validators=[django.core.validators.MaxValueValidator(40), django.core.validators.MinValueValidator(1)])),
                ('mine_num', models.PositiveSmallIntegerField(default=8, validators=[django.core.validators.MaxValueValidator(1599), django.core.validators.MinValueValidator(1)])),
                ('map_data', django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.SmallIntegerField(), size=40), editable=False, size=40)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('duration', models.IntegerField(default=0)),
                ('status', models.CharField(choices=[('PD', 'pending'), ('WN', 'won'), ('LT', 'lost')], default='PD', max_length=2)),
                ('score', models.IntegerField(default=0)),
                ('snapshot', django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.SmallIntegerField(), size=40), default=list, size=40)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('username', models.CharField(max_length=30, unique=True)),
                ('name', models.CharField(default='noname', max_length=30)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='history',
            name='player',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='restful.Player'),
        ),
        migrations.AddField(
            model_name='game',
            name='history',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='restful.History'),
        ),
        migrations.AddField(
            model_name='game',
            name='player',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='restful.Player'),
        ),
    ]
