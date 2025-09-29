
from django.db import models
from django.forms import model_to_dict
from django.utils import timezone
from django.contrib.auth.models import User

class Composer(models.Model):
    STATUS_CHOICES = (
        (1, 'Действует'),
        (2, 'Удалена'),
    )

    name = models.CharField(max_length=100, verbose_name="Имя")
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    image = models.URLField(blank=True, null=True, verbose_name="Изображение")
    description = models.TextField(verbose_name="Биография")

    price = models.IntegerField(verbose_name="Тариф")

    analyzed_works = models.IntegerField(default=0, verbose_name="Проанализировано произведений")
    total_intervals = models.IntegerField(default=0, verbose_name="Всего интервалов")
    period = models.CharField(max_length=100, blank=True, verbose_name="Период творчества")
    polyphony_type = models.CharField(max_length=100, blank=True, verbose_name="Тип полифонии")

    interval_stats = models.JSONField(
        default=list,
        verbose_name="Статистика интервалов",
        help_text='Список словарей: [{"IntervalGroup": "...", "Frequency": число, "StdDev": число}, ...]'
    )


    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Композитор"
        verbose_name_plural = "Композиторы"
        db_table = "composers"
        ordering = ("pk",)


class Analysis(models.Model):
    STATUS_CHOICES = (
        (1, 'Введён'),
        (2, 'В работе'),
        (3, 'Завершен'),
        (4, 'Отклонен'),
        (5, 'Удален')
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    date_created = models.DateTimeField(verbose_name="Дата создания", default=timezone.now)
    date_formation = models.DateTimeField(verbose_name="Дата формирования", blank=True, null=True)
    date_complete = models.DateTimeField(verbose_name="Дата завершения", blank=True, null=True)

    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Пользователь", null=True, related_name='owner')
    moderator = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Модератор", null=True, related_name='moderator')


    def get_composers(self):
        composers = []
        for item in ComposerAnalysis.objects.filter(analysis=self):
           
            composer_data = {
                **model_to_dict(item.composer),
                'length': item.length,
                'value':  -1
            }
            composers.append(composer_data)
        return composers

    class Meta:
        verbose_name = "Анализ"
        verbose_name_plural = "Анализы"
        db_table = "analysiss"
        ordering = ('-date_formation',)
    


class ComposerAnalysis(models.Model):
    composer = models.ForeignKey(Composer, on_delete=models.DO_NOTHING, verbose_name="Композитор")
    analysis = models.ForeignKey(Analysis, on_delete=models.DO_NOTHING, verbose_name="Анализ")
    length = models.IntegerField(default=0, verbose_name="Длина")
    value = models.IntegerField(default= 0, blank=True, verbose_name="Значение")

    def __str__(self):
        return f"м-м №{self.id} (композитор {self.composer_id}, анализ {self.analysis_id})"

    class Meta:
        verbose_name = "м-м"
        verbose_name_plural = "м-м"
        db_table = "composer_analysis"
        ordering = ('id',)
        unique_together = ('composer', 'analysis') 

