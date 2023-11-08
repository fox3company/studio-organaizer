# Generated by Django 4.0.5 on 2022-09-07 12:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
        ('lessons', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='clients',
            field=models.ManyToManyField(blank=True, null=True, related_name='lessons', to='users.client'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='queue',
            field=models.ManyToManyField(blank=True, null=True, related_name='+', to='users.client'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='studio',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lessons.studio'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.teacher'),
        ),
    ]