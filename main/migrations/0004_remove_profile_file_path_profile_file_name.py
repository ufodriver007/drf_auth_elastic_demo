# Generated by Django 5.1.2 on 2024-10-19 07:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_alter_profile_task_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='file_path',
        ),
        migrations.AddField(
            model_name='profile',
            name='file_name',
            field=models.TextField(default='', verbose_name='Имя файла'),
        ),
    ]
