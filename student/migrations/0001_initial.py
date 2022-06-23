# Generated by Django 4.0.5 on 2022-06-22 19:41

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('teacher', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity_name', models.CharField(default='Contempory Dance', max_length=35)),
                ('about', models.TextField()),
                ('meadia_repr', models.ImageField(upload_to='activities/')),
            ],
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='The Space project[Center]', max_length=35)),
                ('geo', models.URLField(default='https://goo.gl/maps/HZwWj15NgYrt2vBz9')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=35)),
                ('about', models.TextField(default='')),
                ('avatar', models.ImageField(blank=True, upload_to='students/')),
                ('phone_number', models.CharField(max_length=17, unique=True, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the local format: '0XXXXXXXX'.", regex='^0?\\d{9,15}$')])),
            ],
        ),
        migrations.CreateModel(
            name='Studio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveSmallIntegerField(default=8, validators=[django.core.validators.MinValueValidator(1)])),
                ('geo_location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='student.location')),
            ],
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveSmallIntegerField(default=25, validators=[django.core.validators.MaxValueValidator(35)])),
                ('start_date', models.DateField()),
                ('start_time', models.TimeField()),
                ('duration', models.TimeField()),
                ('activity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='student.activitytype')),
                ('studio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='student.studio')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teacher.teacher')),
            ],
        ),
        migrations.CreateModel(
            name='CTransactions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('summ', models.PositiveSmallIntegerField(default=0)),
                ('numb_of_lessons', models.PositiveSmallIntegerField(default=1)),
                ('date_tr', models.DateTimeField()),
                ('untill', models.DateField(blank=True, null=True)),
                ('type_of_tr', models.CharField(choices=[('charge', 'Payment: +n lessons'), ('visit', 'Visit: -1 lesson from the account')], default='charge', max_length=9)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transaction', to='student.client')),
                ('lesson', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='student.activitytype')),
            ],
        ),
        migrations.AddField(
            model_name='client',
            name='student_ptr',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='student.student'),
        ),
    ]
