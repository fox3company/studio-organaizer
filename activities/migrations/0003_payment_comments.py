# Generated by Django 4.0.5 on 2022-09-09 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='comments',
            field=models.TextField(blank=True, default='', null=True, verbose_name='Additional comments'),
        ),
    ]