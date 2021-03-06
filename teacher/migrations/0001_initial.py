# Generated by Django 4.0.5 on 2022-06-24 17:17

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team_name', models.CharField(max_length=25, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=35)),
                ('about', models.TextField()),
                ('avatar', models.ImageField(upload_to='teachers/')),
                ('phone_number', models.CharField(max_length=17, unique=True, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the local format: '0XXXXXXXX'.", regex='^0?\\d{9,15}$')])),
                ('org_team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teacher.team')),
            ],
        ),
    ]
