from django.db import models


class CreatedModel(models.Model):
    """Абстрактная модель. Добавляет дату создания."""
    created = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True
    )

    class Meta:
        abstract = True
