from datetime import datetime
from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, default=None, on_delete=models.CASCADE, verbose_name='Пользователь')
    file_name = models.TextField(default='', verbose_name='Имя файла')
    task_id = models.CharField(max_length=255)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
