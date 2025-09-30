# models.py
from django.db import models
class Composer(models.Model):
    name = models.CharField(max_length=200)
    portrait_url = models.URLField()
    period = models.CharField(max_length=100)
    analyzed_works = models.IntegerField()
    total_intervals = models.IntegerField()
    polyphony_type = models.CharField(max_length=100)
    biography = models.TextField()

    interval_stats = models.JSONField(
        verbose_name="Статистика интервалов",
        default=list,
        help_text='Формат: [{"interval_group": "Терции", "frequency": 25.1, "std_dev": 2.0}, ...]'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Композитор"
        verbose_name_plural = "Композиторы"


class Analysis(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    anonymous_stats = models.JSONField(
        verbose_name="Статистика анонимного произведения",
        help_text='Формат: [{"IntervalGroup": "...", "Frequency": число}, ...]'
    )
    
    composers = models.ManyToManyField(
        Composer,
        related_name='analyses',
        verbose_name="Композиторы-кандидаты"
    )
    
    match_results = models.JSONField(
        default=dict,
        verbose_name="Результаты совпадения",
        help_text='Формат: {"1": 98.3, "2": 87.1, ...}'
    )

    def __str__(self):
        return f"Заявка #{self.id}"

    class Meta:
        verbose_name = "Заявка на атрибуцию"
        verbose_name_plural = "Заявки на атрибуцию"